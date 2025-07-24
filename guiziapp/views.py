# guiziapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.utils import timezone
from django.http import JsonResponse, Http404

# Importa los modelos
from .models import Categoria, Quiz, Pregunta, OpcionRespuesta, IntentoQuiz, RespuestaUsuario, UserProfile
from django.contrib.auth.models import User
from guiziapp.forms import CustomSignupForm # Tu formulario de registro


# --- Vistas de Autenticación (MANTENIDAS EXACTAMENTE COMO LAS PROPORCIONASTE) ---
def home(request):
    return render(request, 'home.html')

def sobre_nosotros(request):
    return render(request, 'sobre_nosotros.html')

def signup_view(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Cuenta creada con éxito!')
            return redirect('guiziapp:login')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
            data = request.POST.copy()
            data['email'] = ''
            data['password1'] = ''
            data['password2'] = ''
            form = CustomSignupForm(data)
    else:
        form = CustomSignupForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, '¡Has iniciado sesión correctamente!')
                return redirect('guiziapp:lista_quizzes')
            else:
                messages.error(request, 'Correo o contraseña incorrectos.')

        except User.DoesNotExist:
            messages.error(request, 'No existe un usuario registrado con ese correo.')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('guiziapp:login')

# --- FIN Vistas de Autenticación ---


# --- Vistas para Quizzes ---

def lista_quizzes_view(request):
    categorias = Categoria.objects.all().order_by('nombre')
    quizzes_por_categoria = {}
    selected_category_name = request.GET.get('category')

    if selected_category_name:
        try:
            selected_category = Categoria.objects.get(nombre__iexact=selected_category_name)
            quizzes_por_categoria[selected_category.nombre] = Quiz.objects.filter(categoria=selected_category).order_by('titulo')
        except Categoria.DoesNotExist:
            messages.warning(request, f"La categoría '{selected_category_name}' no existe.")
    else:
        for categoria in categorias:
            quizzes_por_categoria[categoria.nombre] = Quiz.objects.filter(categoria=categoria).order_by('titulo')

    context = {
        'categorias': categorias,
        'quizzes_por_categoria': quizzes_por_categoria,
        'selected_category_name': selected_category_name,
    }
    return render(request, 'lista_actividades.html', context)


# Las vistas 'crear_quiz_view' y 'editar_quiz_view' SON ELIMINADAS.


def iniciar_quiz_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    preguntas = quiz.preguntas.all().order_by('id')

    if not preguntas.exists():
        messages.error(request, "Este quiz no tiene preguntas todavía. ¡Vuelve más tarde!")
        return redirect('guiziapp:lista_quizzes')

    if not request.user.is_authenticated:
        request.session['quiz_id_to_start'] = quiz.id
        # print(f"DEBUG: Usuario no autenticado. Redirigiendo a pedir nombre para quiz ID: {quiz.id}") # DEBUG
        return redirect('guiziapp:pedir_nombre_anonimo')

    intento_quiz = IntentoQuiz.objects.create(
        usuario=request.user,
        quiz=quiz,
        completado=False
    )
    request.session['intento_quiz_id'] = intento_quiz.id
    request.session['pregunta_actual_index'] = 0
    # print(f"DEBUG: INICIAR_QUIZ_VIEW - IntentoQuiz creado con ID: {intento_quiz.id} para usuario: {request.user.username}") # DEBUG
    return redirect('guiziapp:jugar_quiz', quiz_id=quiz.id)

def pedir_nombre_anonimo_view(request):
    if request.method == 'POST':
        nombre_anonimo = request.POST.get('nombre_anonimo')
        quiz_id = request.session.get('quiz_id_to_start')

        if not nombre_anonimo:
            messages.error(request, "Por favor, introduce tu nombre para jugar.")
            return render(request, 'pedir_nombre_anonimo.html')

        if not quiz_id:
            messages.error(request, "Error: No se encontró el quiz para iniciar.")
            return redirect('guiziapp:lista_quizzes')

        quiz = get_object_or_404(Quiz, id=quiz_id)

        intento_quiz = IntentoQuiz.objects.create(
            nombre_anonimo=nombre_anonimo,
            quiz=quiz,
            completado=False
        )
        request.session['intento_quiz_id'] = intento_quiz.id
        request.session['pregunta_actual_index'] = 0

        if 'quiz_id_to_start' in request.session:
            del request.session['quiz_id_to_start']
        # print(f"DEBUG: PEDIR_NOMBRE_ANONIMO_VIEW - IntentoQuiz creado con ID: {intento_quiz.id} para anónimo: {nombre_anonimo}") # DEBUG
        return redirect('guiziapp:jugar_quiz', quiz_id=quiz.id)

    return render(request, 'pedir_nombre_anonimo.html')


def jugar_quiz_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    intento_quiz_id = request.session.get('intento_quiz_id')
    pregunta_actual_index = request.session.get('pregunta_actual_index', 0)

    # print(f"DEBUG: JUGAR_QUIZ_VIEW - ID de sesión intento_quiz_id: {intento_quiz_id}") # DEBUG

    if not intento_quiz_id:
        messages.error(request, "No se ha encontrado un intento de quiz activo.")
        # Redirigir a iniciar quiz de nuevo para crear un intento válido.
        return redirect('guiziapp:iniciar_quiz', quiz_id=quiz.id)

    try:
        # Intentar obtener el IntentoQuiz sin el filtro 'completado=True'
        intento_quiz = IntentoQuiz.objects.get(id=intento_quiz_id, quiz=quiz)
        # print(f"DEBUG: JUGAR_QUIZ_VIEW - IntentoQuiz {intento_quiz.id} encontrado. Completado: {intento_quiz.completado}") # DEBUG
    except IntentoQuiz.DoesNotExist:
        messages.error(request, f"El intento de quiz con ID {intento_quiz_id} no existe o no pertenece a este quiz. Iniciando uno nuevo.")
        # Si el intento no existe, redirigir para crear uno nuevo
        return redirect('guiziapp:iniciar_quiz', quiz_id=quiz.id)


    if intento_quiz.completado:
        # Si el intento ya está marcado como completado en DB, redirigir a resultados
        # print(f"DEBUG: JUGAR_QUIZ_VIEW - IntentoQuiz {intento_quiz.id} ya está completado. Redirigiendo a resultados.") # DEBUG
        return redirect('guiziapp:resultados_quiz', intento_quiz_id=intento_quiz.id)

    preguntas = list(quiz.preguntas.all().order_by('id'))
    total_preguntas = len(preguntas)

    if pregunta_actual_index >= total_preguntas:
        # Lógica para finalizar el quiz si ya no hay más preguntas pendientes en la sesión
        if not intento_quiz.completado: # Solo actualiza si no se ha completado ya
            intento_quiz.completado = True
            intento_quiz.fecha_finalizacion = timezone.now()
            intento_quiz.tiempo_transcurrido_segundos = (intento_quiz.fecha_finalizacion - intento_quiz.fecha_inicio).total_seconds()
            intento_quiz.save() # ¡Asegurarse de guardar!
            # print(f"DEBUG: JUGAR_QUIZ_VIEW - IntentoQuiz {intento_quiz.id} FINALIZADO y GUARDADO. Redirigiendo a resultados.") # DEBUG
        return redirect('guiziapp:resultados_quiz', intento_quiz_id=intento_quiz.id)

    pregunta_actual = preguntas[pregunta_actual_index]
    opciones_mezcladas = list(pregunta_actual.opciones.all())
    import random
    random.shuffle(opciones_mezcladas)

    context = {
        'quiz': quiz,
        'pregunta': pregunta_actual,
        'opciones': opciones_mezcladas,
        'pregunta_numero': pregunta_actual_index + 1,
        'total_preguntas': total_preguntas,
        'tiempo_limite_pregunta': pregunta_actual.tiempo_limite,
        'intento_quiz_id': intento_quiz.id,
    }
    return render(request, 'jugar_quiz.html', context)


# Vista para procesar la respuesta a una pregunta (recibida por AJAX)
def procesar_respuesta_quiz_ajax(request):
    if request.method == 'POST':
        try:
            intento_quiz_id = request.POST.get('intento_quiz_id')
            pregunta_id = request.POST.get('pregunta_id')
            opcion_seleccionada_id = request.POST.get('opcion_seleccionada_id')

            tiempo_respuesta_str = request.POST.get('tiempo_respuesta_segundos', '0')
            try:
                tiempo_respuesta_int = int(float(tiempo_respuesta_str))
            except ValueError:
                tiempo_respuesta_int = 0
                # print(f"Advertencia: tiempo_respuesta_segundos '{tiempo_respuesta_str}' no es numérico. Usando 0.")


            intento_quiz = get_object_or_404(IntentoQuiz, id=intento_quiz_id)
            pregunta = get_object_or_404(Pregunta, id=pregunta_id)

            if pregunta.quiz != intento_quiz.quiz:
                return JsonResponse({'error': 'La pregunta no pertenece a este quiz.'}, status=400)

            opcion_seleccionada = None
            es_correcta = False
            if opcion_seleccionada_id:
                opcion_seleccionada = get_object_or_404(OpcionRespuesta, id=opcion_seleccionada_id)
                if opcion_seleccionada.pregunta != pregunta:
                    return JsonResponse({'error': 'La opción seleccionada no pertenece a esta pregunta.'}, status=400)
                es_correcta = opcion_seleccionada.es_correcta

            puntaje_obtenido = 0
            if es_correcta:
                puntaje_base_pregunta = 100
                puntaje_por_tiempo = max(0, puntaje_base_pregunta - (tiempo_respuesta_int * 2))
                puntaje_obtenido = puntaje_por_tiempo

                intento_quiz.puntaje += puntaje_obtenido
                intento_quiz.save()

            RespuestaUsuario.objects.create(
                intento_quiz=intento_quiz,
                pregunta=pregunta,
                opcion_seleccionada=opcion_seleccionada,
                es_correcta=es_correcta,
                tiempo_respuesta_segundos=tiempo_respuesta_int
            )

            request.session['pregunta_actual_index'] += 1

            total_preguntas = intento_quiz.quiz.preguntas.count()
            quiz_terminado = (request.session['pregunta_actual_index'] >= total_preguntas)

            response_data = {
                'success': True,
                'es_correcta': es_correcta,
                'puntaje_obtenido': puntaje_obtenido,
                'puntaje_total_actual': intento_quiz.puntaje,
                'quiz_terminado': quiz_terminado,
            }
            return JsonResponse(response_data)

        except (IntentoQuiz.DoesNotExist, Pregunta.DoesNotExist, OpcionRespuesta.DoesNotExist) as e:
            # Captura errores si los IDs no se encuentran
            # print(f"Error 404 en procesar_respuesta_quiz_ajax: {e}") # DEBUG
            return JsonResponse({'error': f'Objeto no encontrado: {e}'}, status=404)
        except ValueError as e:
            # Captura errores de conversión de tipo (ej. tiempo_respuesta_segundos no es numérico)
            # print(f"Error de ValueError en procesar_respuesta_quiz_ajax: {e}") # DEBUG
            return JsonResponse({'error': f'Error en el formato de datos: {e}'}, status=400)
        except Exception as e:
            # Captura cualquier otro error inesperado
            # print(f"Error inesperado en procesar_respuesta_quiz_ajax: {e}") # DEBUG
            return JsonResponse({'error': f'Un error inesperado ocurrió en el servidor: {e}'}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def resultados_quiz_view(request, intento_quiz_id):
    # Ya no necesitamos el filtro completado=True aquí, la vista jugar_quiz_view lo asegura.
    # Si por alguna razón llega aquí sin estar completado, lo completamos y guardamos.
    intento_quiz = get_object_or_404(IntentoQuiz, id=intento_quiz_id)

    # Asegurarse de que el intento está marcado como completado y con fecha final
    if not intento_quiz.completado:
        intento_quiz.completado = True
        intento_quiz.fecha_finalizacion = timezone.now()
        intento_quiz.tiempo_transcurrido_segundos = (intento_quiz.fecha_finalizacion - intento_quiz.fecha_inicio).total_seconds()
        intento_quiz.save() # ¡Guardar los cambios!

    respuestas_correctas = intento_quiz.respuestas_individuales.filter(es_correcta=True).count()
    total_preguntas = intento_quiz.quiz.preguntas.count()
    porcentaje_acierto = (respuestas_correctas / total_preguntas * 100) if total_preguntas > 0 else 0

    context = {
        'intento': intento_quiz,
        'respuestas_correctas': respuestas_correctas,
        'total_preguntas': total_preguntas,
        'porcentaje_acierto': round(porcentaje_acierto, 2),
    }

    if 'intento_quiz_id' in request.session:
        del request.session['intento_quiz_id']
    if 'pregunta_actual_index' in request.session:
        del request.session['pregunta_actual_index']
    if 'quiz_id_to_start' in request.session:
        del request.session['quiz_id_to_start']

    return render(request, 'resultados_quiz.html', context)


def ranking_view(request):
    top_10_intentos = IntentoQuiz.objects.filter(completado=True).order_by('-puntaje', 'tiempo_transcurrido_segundos')[:10]

    ranking_data = []
    for i, intento in enumerate(top_10_intentos):
        ranking_data.append({
            'posicion': i + 1,
            'nombre_jugador': intento.get_player_name(),
            'quiz_titulo': intento.quiz.titulo,
            'puntaje': intento.puntaje,
            'tiempo_segundos': intento.tiempo_transcurrido_segundos,
        })

    context = {
        'ranking': ranking_data,
    }
    return render(request, 'ranking.html', context)

# La vista 'mis_actividades_view' se simplifica ya que no hay creación de quizzes por usuarios.
@login_required
def mis_actividades_view(request):
    mis_intentos_completados = IntentoQuiz.objects.filter(
        usuario=request.user, completado=True
    ).order_by('-fecha_finalizacion')[:10]

    context = {
        'mis_intentos_completados': mis_intentos_completados,
    }
    return render(request, 'mis_actividades.html', context)