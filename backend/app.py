from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory, send_file
from flask_cors import CORS
from db import get_connection
from werkzeug.utils import secure_filename
from datetime import datetime, date, time, timedelta
from xhtml2pdf import pisa
import uuid
import mysql.connector
import openpyxl
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import datetime
from reportlab.lib.colors import black
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Paragraph
import datetime as datatime
import random

SECRET_KEY = "miclavesecreta"

app = Flask(__name__, static_folder="./static", static_url_path="")
CORS(app)
app.secret_key = SECRET_KEY

@app.route("/test-db")
def test_db():
    conn = get_connection()
    if conn and conn.is_connected():
        return "✅ Conexión a la base de datos exitosa"
    else:
        return "❌ Fallo la conexión a la base de datos"

@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('registro'))

#----------------------------------------------------------------------------------
# REGISTRO DE ASISTENCIA
#----------------------------------------------------------------------------------
def buscar_asistencia_ajax(numero_documento):
    """Busca un registro de asistencia por número de documento para AJAX."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT nombrecompleto, tipo_persona, vinculacion_facultad, vinculacion_institucion, telefono
        FROM asistencia_visita
        WHERE numero_documento = %s
        LIMIT 1
        """
        cursor.execute(query, (numero_documento,))
        resultado = cursor.fetchone()
        return resultado
    except Exception as e:
        print(f"Error al buscar asistencia (AJAX): {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@app.route('/buscar_persona', methods=['POST'])
def buscar_persona():
    """Endpoint para la búsqueda de persona por número de documento (AJAX)."""
    numero_documento = request.form.get('numero_documento')
    if numero_documento:
        datos = buscar_asistencia_ajax(numero_documento)
        return jsonify(datos)
    return jsonify(None)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    mensaje = None
    error = None

    if request.method == 'POST':
        numero_documento = request.form.get('numero_documento')
        nombrecompleto = request.form.get('nombrecompleto')
        tipo_persona = request.form.get('tipo_persona')
        vinculacion_facultad = request.form.get('vinculacion_facultad')
        vinculacion_semestre = request.form.get('vinculacion_semestre')
        vinculacion_institucion = request.form.get('vinculacion_institucion')
        telefono = request.form.get('telefono')
        actividad_desarrollada = request.form.get('actividad_desarrollada')
        codigo_visita = request.form.get('codigo_visita')
        fecha_registro_asistencia = datetime.now().date()

        if not nombrecompleto:
            error = 'El nombre completo es obligatorio.'
        elif not tipo_persona:
            error = 'El tipo de persona es obligatorio.'

        if error:
            return render_template('registro.html', error=error)

        conn = get_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO asistencia_visita (fecha, nombrecompleto, numero_documento, tipo_persona,
        vinculacion_facultad, vinculacion_semestre, vinculacion_institucion, telefono,
        actividad_desarrollada, codigo_visita)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (fecha_registro_asistencia, nombrecompleto, numero_documento, tipo_persona,
                  vinculacion_facultad, vinculacion_semestre, vinculacion_institucion, telefono,
                  actividad_desarrollada, codigo_visita)

        try:
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            mensaje = 'Asistencia registrada.'
            return render_template('registro.html', mensaje=mensaje)
        except Exception as e:
            print(f"Error al insertar en asistencia_visita: {e}")
            conn.rollback()
            cursor.close()
            conn.close()
            error = 'Error al registrar la asistencia.'
            return render_template('registro.html', error=error)

    return render_template('registro.html')

#----------------------------------------------------------------------------------
# AUTORIZACIÓN
#----------------------------------------------------------------------------------
def buscar_autorizacion_ajax(identificacion):
    """Busca un registro de autorización por identificación para AJAX."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT nombreresponsable, ocupacion, entidad, direccion_barrio, municipio, telefono
        FROM autorizacion_ingreso
        WHERE identificacion = %s
        LIMIT 1
        """
        cursor.execute(query, (identificacion,))
        resultado = cursor.fetchone()
        return resultado
    except Exception as e:
        print(f"Error al buscar autorización (AJAX): {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@app.route('/buscar_autorizacion_info', methods=['POST'])
def buscar_autorizacion_info():
    """Endpoint para la búsqueda de información de autorización por identificación (AJAX)."""
    identificacion = request.form.get('identificacion')
    if identificacion:
        datos = buscar_autorizacion_ajax(identificacion)
        return jsonify(datos)
    return jsonify(None)

@app.route('/autorizacion', methods=['GET', 'POST'])
def autorizacion_form():
    # if not session.get('loggedin'):
    #     return redirect(url_for('login'))
    now = datetime.now()
    fecha_automatica = now.strftime('%Y-%m-%d')

    if request.method == 'POST':
        def generar_codigo_visita():
            letras = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            codigo = random.choice(letras)
            for _ in range(5):
                codigo += str(random.randint(0, 9))
            return codigo
        codigo_visita = request.form.get('codigo_visita')
        identificacion = request.form.get('identificacion')
        nombreresponsable = request.form.get('nombreresponsable')
        ocupacion = request.form.get('ocupacion')
        entidad = request.form.get('entidad')
        direccion_barrio = request.form.get('direccion_barrio')
        municipio = request.form.get('municipio')
        telefono = request.form.get('telefono')
        objetivovisita = request.form.get('objetivovisita')
        numeropersonas = request.form.get('numeropersonas', type=int)
        vinculacion = request.form.get('vinculacion')
        hora_llegada_str = request.form.get('hora_llegada')
        hora_salida_str = request.form.get('hora_salida')
        fecha_str = request.form.get('fecha')
        usuario_id = 1  

        hora_llegada = None
        if hora_llegada_str:
            try:
                hora_llegada = datetime.strptime(hora_llegada_str, '%H:%M').time()
            except ValueError:
                error = 'Formato de hora de llegada incorrecto (HH:MM).'
                return render_template('autorizacion.html', error=error,
                                       fecha=fecha_automatica)
        else:
            error = 'La hora de llegada es obligatoria.'
            return render_template('autorizacion.html', error=error,
                                   fecha=fecha_automatica)

        fecha = None
        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                error = 'Formato de fecha incorrecto (AAAA-MM-DD).'
                return render_template('autorizacion.html', error=error,
                                       fecha=fecha_automatica)
        else:
            fecha = datetime.strptime(fecha_automatica, '%Y-%m-%d').date()

        hora_salida = None
        if hora_salida_str:
            try:
                hora_salida = datetime.strptime(hora_salida_str, '%H:%M').time()
            except ValueError:
                error = 'Formato de hora de salida incorrecto (HH:MM).'
                return render_template('autorizacion.html', error=error,
                                       fecha=fecha_automatica)

        conn = get_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO autorizacion_ingreso (codigo_visita, identificacion, nombreresponsable,
        ocupacion, entidad, direccion_barrio, municipio, telefono, objetivovisita,
        numeropersonas, vinculacion, hora_llegada, hora_salida, fecha, usuario_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (codigo_visita, identificacion, nombreresponsable, ocupacion, entidad,
                  direccion_barrio, municipio, telefono, objetivovisita, numeropersonas,
                  vinculacion, hora_llegada, hora_salida, fecha, usuario_id)
        try:
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('autorizacion_form', mensaje='Autorización guardada'))
        except Exception as e:
            print(f"Error al insertar en autorizacion_ingreso: {e}")
            conn.rollback()
            cursor.close()
            conn.close()
            error = "Error al guardar la autorización de ingreso."
            return render_template('autorizacion.html', error=error,
                                   fecha=fecha_automatica)

    mensaje = request.args.get('mensaje')
    return render_template('autorizacion.html', fecha=fecha_automatica, mensaje=mensaje)


@app.route('/buscar_autorizacion_identificacion/<identificacion>')
def buscar_autorizacion_identificacion(identificacion):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM autorizacion_ingreso WHERE identificacion = %s"
    cursor.execute(query, (identificacion,))
    autorizacion = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if autorizacion:
        autorizacion_dict = {
            'codigo_visita': autorizacion[1],
            'nombreresponsable': autorizacion[3],
            'identificacion': autorizacion[2],
            'ocupacion': autorizacion[4],
            'entidad': autorizacion[5],
            'direccion_barrio': autorizacion[6],
            'municipio': autorizacion[7],
            'telefono': autorizacion[8],
            'objetivovisita': autorizacion[9],
            'numeropersonas': autorizacion[10],
            'vinculacion': autorizacion[11],
            'hora_llegada': autorizacion[12].strftime('%H:%M') if autorizacion[12] else None,
            'hora_salida': autorizacion[13].strftime('%H:%M') if autorizacion[13] else None,
            'fecha': autorizacion[14].strftime('%Y-%m-%d') if autorizacion[14] else None,
            # No incluimos el archivo por seguridad y eficiencia
        }
        return jsonify({'autorizacion': autorizacion_dict})
    return jsonify({'error': 'No se encontró ninguna autorización con esa identificación.'})
    pass

@app.route('/autocomplete')
def autocomplete():
    term = request.args.get('term')
    field = request.args.get('field')
    conn = get_connection()
    cursor = conn.cursor()
    results = []
    if field in ['nombreresponsable', 'ocupacion', 'entidad', 'direccion_barrio', 'municipio', 'telefono']:
        query = f"SELECT DISTINCT {field} FROM autorizacion_ingreso WHERE {field} LIKE %s LIMIT 10"
        cursor.execute(query, ('%' + term + '%',))
        results = [row[0] for row in cursor.fetchall() if row[0]]
    cursor.close()
    conn.close()
    return jsonify(results)
    pass

def nl2br_filter(s):
    """Reemplaza saltos de línea con etiquetas <br>."""
    if s:
        return s.replace('\n', '<br>')
    return ''

app.jinja_env.filters['nl2br'] = nl2br_filter

@app.route('/generar_pdf/<codigo_visita>')
def generar_pdf(codigo_visita):
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM autorizacion_ingreso WHERE codigo_visita = %s", (codigo_visita,))
    autorizacion = cursor.fetchone()
    cursor.close()
    conn.close()

    if not autorizacion:
        return "Autorización no encontrada."

    def parse_date_time(value, format_string):
        if value:
            try:
                return datetime.strptime(str(value), format_string)
            except ValueError:
                return None
        return None
   
    output = BytesIO()
    c = canvas.Canvas(output, pagesize=letter)
    styles = getSampleStyleSheet()
    style_center = styles['Normal']
    style_center.alignment = TA_CENTER
    fuente_tamano = 8
    altura_fila = 0.25 * inch
    ancho_total = 7.1 * inch  
    x_inicio = (letter[0] - ancho_total) / 2  
    y_inicio = letter[1] - 1.8 * inch

    autorizacion_pdf = {
        'codigo_visita': autorizacion[1],
        'identificacion': autorizacion[2],
        'nombreresponsable': autorizacion[3],
        'ocupacion': autorizacion[4],
        'entidad': autorizacion[5],
        'direccion_barrio': autorizacion[6],
        'municipio': autorizacion[7],
        'telefono': autorizacion[8],
        'objetivovisita': autorizacion[9],
        'numeropersonas': autorizacion[10],
        'vinculacion': autorizacion[11],  
        'hora_llegada': parse_date_time(autorizacion[12], '%H:%M:%S') if len(autorizacion) > 12 else None,
        'hora_salida': parse_date_time(autorizacion[13], '%H:%M:%S') if len(autorizacion) > 13 else None,
        'fecha': parse_date_time(autorizacion[14], '%Y-%m-%d') if len(autorizacion) > 14 else None,
    }

     # --- Elementos Estáticos del Encabezado Centrado y Unido ---
    logo_path = "static/logo_jardin.png"  # Asegúrate de que la ruta sea correcta

    # --- Dimensiones y Posiciones ---
    logo_ancho_imagen = 0.8 * inch
    logo_alto_imagen = 0.8 * inch
    espacio_entre_lineas = 0.25 * inch
    altura_bloque_texto = 3 * espacio_entre_lineas + 0.1 * inch

    # --- Posición Vertical Central del Encabezado (¡Bajamos el valor!) ---
    y_centro_encabezado = 10.0 * inch # Disminuimos el valor para bajar el encabezado

    # --- Posición y Cuadro del Logo ---
    logo_ancho_cuadro = 1.1 * inch
    logo_alto_cuadro = altura_bloque_texto # Misma altura que el texto
    logo_x_cuadro = (letter[0] - (logo_ancho_cuadro + 4.0 * inch + 1.9 * inch)) / 2 # Inicio horizontal centrado
    logo_y_cuadro = y_centro_encabezado - logo_alto_cuadro / 2 # Centrar verticalmente
    c.rect(logo_x_cuadro, logo_y_cuadro, logo_ancho_cuadro, logo_alto_cuadro)
    logo_x_imagen = logo_x_cuadro + (logo_ancho_cuadro - logo_ancho_imagen) / 2
    logo_y_imagen = logo_y_cuadro + (logo_alto_cuadro - logo_alto_imagen) / 2
    try:
        c.drawImage(logo_path, logo_x_imagen, logo_y_imagen, width=logo_ancho_imagen, height=logo_alto_imagen)
    except:
        print(f"No se pudo cargar el logo desde: {logo_path}")

    c.setFont("Helvetica-Bold", 10)
    ancho_texto_izq = 4.5 * inch
    x_texto_izq = logo_x_cuadro + logo_ancho_cuadro
    y_texto_centro_izq = y_centro_encabezado # Centrar verticalmente el bloque de texto izquierdo

    # Cuadro del Texto Izquierdo
    c.rect(x_texto_izq, y_texto_centro_izq - altura_bloque_texto / 2, ancho_texto_izq, altura_bloque_texto)
    c.drawCentredString(x_texto_izq + ancho_texto_izq / 2, y_texto_centro_izq - espacio_entre_lineas * -0.5, "MACROPROCESO MISIONAL")
    c.line(x_texto_izq, y_texto_centro_izq - espacio_entre_lineas * -0.4, x_texto_izq + ancho_texto_izq, y_texto_centro_izq - espacio_entre_lineas * -0.4)
    c.drawCentredString(x_texto_izq + ancho_texto_izq / 2, y_texto_centro_izq - espacio_entre_lineas * 0.3, "PROCESO: DOCENCIA")
    c.line(x_texto_izq, y_texto_centro_izq - espacio_entre_lineas * 0.4, x_texto_izq + ancho_texto_izq, y_texto_centro_izq - espacio_entre_lineas * 0.4)
    c.drawCentredString(x_texto_izq + ancho_texto_izq / 2, y_texto_centro_izq - espacio_entre_lineas * 1, "FORMATO SOLICITUD DE AUTORIZACIÓN PARA INGRESO")

    c.setFont("Helvetica", 10)
    ancho_texto_der = 1.5 * inch
    x_texto_der = x_texto_izq + ancho_texto_izq
    y_texto_centro_der = y_centro_encabezado # Centrar verticalmente el bloque de texto derecho

    # Cuadro del Texto Derecho
    c.rect(x_texto_der, y_texto_centro_der - altura_bloque_texto / 2, ancho_texto_der, altura_bloque_texto)
    c.drawCentredString(x_texto_der + ancho_texto_der / 2, y_texto_centro_der - espacio_entre_lineas * -0.5, autorizacion[1])
    c.line(x_texto_der, y_texto_centro_der - espacio_entre_lineas * -0.4, x_texto_der + ancho_texto_der, y_texto_centro_der - espacio_entre_lineas * -0.4)
    c.drawCentredString(x_texto_der + ancho_texto_der / 2, y_texto_centro_der - espacio_entre_lineas * 0.3, "VERSIÓN: 01")
    c.line(x_texto_der, y_texto_centro_der - espacio_entre_lineas * 0.4, x_texto_der + ancho_texto_der, y_texto_centro_der - espacio_entre_lineas * 0.4)
    c.drawCentredString(x_texto_der + ancho_texto_der / 2, y_texto_centro_der - espacio_entre_lineas * 1, "Página 1 de 1")
    # -------------------------------------------------------------------------------
    ancho_columna = ancho_total / 3

    # Dibujar los rectángulos de las tres columnas
    c.rect(x_inicio, y_inicio - altura_fila, ancho_columna, altura_fila)
    c.rect(x_inicio + ancho_columna, y_inicio - altura_fila, ancho_columna, altura_fila)
    c.rect(x_inicio + 2 * ancho_columna, y_inicio - altura_fila, ancho_columna, altura_fila)

    c.rect(x_inicio, y_inicio - 2 * altura_fila, ancho_columna, altura_fila)
    c.rect(x_inicio + ancho_columna, y_inicio - 2 * altura_fila, ancho_columna, altura_fila)
    c.rect(x_inicio + 2 * ancho_columna, y_inicio - 2 * altura_fila, ancho_columna, altura_fila)

    c.rect(x_inicio, y_inicio - 3 * altura_fila, ancho_columna, altura_fila)
    ancho_segundo_rectangulo = ancho_columna * 2
    c.rect(x_inicio + ancho_columna, y_inicio - 3 * altura_fila, ancho_segundo_rectangulo, altura_fila)

    c.setFont("Helvetica-Bold", fuente_tamano)
    c.drawString(x_inicio + ancho_columna * 0.14, y_inicio + altura_fila * 0.1 - 0.2 * inch, "NOMBRE DEL RESPONSABLE:")
    c.drawString(x_inicio + ancho_columna * 1.05, y_inicio + altura_fila * 0.1 - 0.2 * inch, "IDENTIFICACION:")
    c.drawString(x_inicio + ancho_columna * 2.05, y_inicio + altura_fila * 0.1 - 0.2 * inch, "OCUPACION:") 
    c.setFont("Helvetica-Bold", fuente_tamano - 1)
    c.drawString(x_inicio + ancho_columna * 0.14, y_inicio + altura_fila * 0.1 - 0.45 * inch, autorizacion[3])
    c.drawString(x_inicio + ancho_columna * 1.05, y_inicio + altura_fila * 0.1 - 0.45 * inch, autorizacion[2])
    c.drawString(x_inicio + ancho_columna * 2.05, y_inicio + altura_fila * 0.1 - 0.45 * inch, autorizacion[4])
    # --------------------------------------------------------------------------
    c.setFont("Helvetica-Bold", fuente_tamano - 0)
    c.drawString(x_inicio + ancho_columna * 0.14, y_inicio + altura_fila * 0.1 - 0.69 * inch, "ENTIDAD:")
    c.drawString(x_inicio + ancho_columna * 1.05, y_inicio + altura_fila * 0.1 - 0.69 * inch, "DIRECCION/BARRIO:")
    y_inicio = letter[1] - 2.05 * inch
    y_campo_fila2 = y_inicio - 3 * altura_fila
    c.rect(x_inicio, y_campo_fila2, ancho_columna, altura_fila)
    c.drawString(x_inicio + ancho_columna * 0.14, y_inicio + altura_fila * 0.1 - 0.69 * inch, autorizacion[5])
    c.rect(x_inicio + ancho_columna, y_campo_fila2, ancho_columna * 2, altura_fila)
    c.drawString(x_inicio + ancho_columna * 1.05, y_inicio + altura_fila * 0.1 - 0.69 * inch, autorizacion[6])
    #--------------------------------------------------------------------------
    y_inicio = letter[1] - 2.3 * inch
    c.setFont("Helvetica-Bold", fuente_tamano - 0)
    c.drawString(x_inicio + ancho_columna * 0.14, y_inicio + altura_fila * 0.1 - 0.69 * inch, "MUNICIPIO:")
    c.drawString(x_inicio + ancho_columna * 1.05, y_inicio + altura_fila * 0.1 - 0.69 * inch, "No TELEFONO:")   
    y_campo_fila2 = y_inicio - 3 * altura_fila
    c.rect(x_inicio, y_campo_fila2, ancho_columna, altura_fila)
    c.rect(x_inicio + ancho_columna, y_campo_fila2, ancho_columna * 2, altura_fila)
    y_inicio = letter[1] - 2.55 * inch
    y_campo_fila2 = y_inicio - 3 * altura_fila
    c.rect(x_inicio, y_campo_fila2, ancho_columna, altura_fila)
    c.drawString(x_inicio + ancho_columna * 0.14, y_inicio + altura_fila * 0.1 - 0.69 * inch, autorizacion[7])
    c.rect(x_inicio + ancho_columna, y_campo_fila2, ancho_columna * 2, altura_fila)
    c.drawString(x_inicio + ancho_columna * 1.05, y_inicio + altura_fila * 0.1 - 0.69 * inch, autorizacion[8]) 
    #--------------------------------------------------------------------------
    y_inicio_objetivo = letter[1] - 3.28 * inch # Ajustar la posición inicial más abajo
    c.setFont("Helvetica-Bold", fuente_tamano)
    y_etiqueta_objetivo = y_inicio_objetivo - 0.8 * altura_fila # Ajustar posición de la etiqueta
    c.drawString(inch, y_etiqueta_objetivo, "OBJETIVO DE LA PRACTICA O VISITA:")
    y_campo_objetivo_titulo = y_inicio_objetivo - 1.1 * altura_fila # Ajustar posición del primer rectángulo
    altura_campo_objetivo_titulo = 1 * altura_fila # Reducir altura del primer rectángulo
    ancho_campo_objetivo = ancho_total
    c.rect(x_inicio, y_campo_objetivo_titulo, ancho_campo_objetivo, altura_campo_objetivo_titulo)
    y_inicio_objetivo = letter[1] - 3.88 * inch # Ajustar la posición inicial más abajo
    y_campo_objetivo_texto = y_inicio_objetivo - 1.1 * altura_fila - 0.1 * inch # Iniciar el segundo rectángulo justo debajo del primero
    altura_campo_objetivo_texto = 2.8 * altura_fila # Aumentar la altura del segundo rectángulo
    c.rect(x_inicio, y_campo_objetivo_texto, ancho_campo_objetivo, altura_campo_objetivo_texto)

    c.setFont("Helvetica", fuente_tamano - 1)
    texto = autorizacion_pdf.get('objetivovisita',autorizacion[9])

    styles = getSampleStyleSheet()
    style_objetivo = styles['Normal']
    style_objetivo.leading = 1.1 * fuente_tamano # Ajustar el espaciado entre líneas
    parrafo_objetivo = Paragraph(texto, style_objetivo)
    ancho_disponible = ancho_campo_objetivo - 2 * 0.2 * inch # Reducir el margen horizontal
    altura_disponible = altura_campo_objetivo_texto - 2 * 0.2 * inch # Reducir el margen vertical
    parrafo_objetivo.wrapOn(c, ancho_disponible, altura_disponible)
    parrafo_objetivo.drawOn(c, inch + 0.05 * inch, y_campo_objetivo_texto + 0.20 * inch) # Ajustar la posición del texto
    #---------------------------------------------------------------------------
    y_inicio = letter[1] - 4.2 * inch
    c.setFont("Helvetica-Bold", fuente_tamano - 0)
    c.drawString(inch, y_inicio - altura_fila * 2.5 - 0.05 * inch, "Numero de personas que ingresan:")
    y_campo_fila2 = y_inicio - 3 * altura_fila
    c.rect(x_inicio, y_campo_fila2, ancho_columna, altura_fila)
    c.rect(x_inicio + ancho_columna, y_campo_fila2, ancho_columna * 2, altura_fila)
    c.drawString(x_inicio + ancho_columna * 1.05, y_inicio + altura_fila * 0.1 - 0.69 * inch, str(autorizacion[10]))
    y_inicio = letter[1] - 4.45 * inch
    c.setFont("Helvetica-Bold", fuente_tamano - 0)
    c.drawString(inch, y_inicio - altura_fila * 2.5 - 0.05 * inch, "Facultad - Semestre - Institución:")
    y_campo_fila2 = y_inicio - 3 * altura_fila
    c.rect(x_inicio, y_campo_fila2, ancho_columna, altura_fila)
    c.rect(x_inicio + ancho_columna, y_campo_fila2, ancho_columna * 2, altura_fila)
    c.drawString(x_inicio + ancho_columna * 1.05, y_inicio + altura_fila * 0.1 - 0.69 * inch, autorizacion[11])
    y_inicio = letter[1] - 4.7 * inch
    c.setFont("Helvetica-Bold", fuente_tamano - 0)
    c.drawString(inch, y_inicio - altura_fila * 2.5 - 0.05 * inch, "Hora de llegada:")
    y_campo_fila2 = y_inicio - 3 * altura_fila
    c.rect(x_inicio, y_campo_fila2, ancho_columna, altura_fila)
    c.rect(x_inicio + ancho_columna, y_campo_fila2, ancho_columna * 2, altura_fila)
    c.drawString(x_inicio + ancho_columna * 1.05, y_inicio + altura_fila * 0.1 - 0.69 * inch,  autorizacion_pdf['hora_llegada'].strftime("%I:%M %p") if autorizacion_pdf['hora_llegada'] else "")
    y_inicio = letter[1] - 4.95 * inch
    c.setFont("Helvetica-Bold", fuente_tamano - 0)
    c.drawString(inch, y_inicio - altura_fila * 2.5 - 0.05 * inch, "Hora de salida:")
    y_campo_fila2 = y_inicio - 3 * altura_fila
    c.rect(x_inicio, y_campo_fila2, ancho_columna, altura_fila)
    c.rect(x_inicio + ancho_columna, y_campo_fila2, ancho_columna * 2, altura_fila)
    c.drawString(x_inicio + ancho_columna * 1.05, y_inicio + altura_fila * 0.1 - 0.69 * inch,  autorizacion_pdf['hora_salida'].strftime("%I:%M %p") if autorizacion_pdf['hora_llegada'] else "")
    #---------------------------------------------------------------------------
    y_inicio = letter[1] - 5.5 * inch
    c.setFont("Helvetica-Bold", fuente_tamano - 0)
    c.drawString(inch, y_inicio - altura_fila * 2.5 - 0.05 * inch, "RECOMENDACIONES:")
    y_inicio = letter[1] - 5.75 * inch
    c.drawString(inch, y_inicio - altura_fila * 2.5 - 0.05 * inch, "-No salirse de los senderos para evitar cualquier tipo de accidentes.")
    y_inicio = letter[1] - 5.9 * inch
    c.drawString(inch, y_inicio - altura_fila * 2.5 - 0.05 * inch, "-Disponga de ropa adecuada para el recorrido o permanencia (Pantalón largo,sudadera, gorra, tenis, botas).")
    y_inicio = letter[1] - 6.05 * inch
    c.drawString(inch, y_inicio - altura_fila * 2.5 - 0.05 * inch, "-En tiempo de invierno utilizar preferiblemente botas pantaneras.")
    y_inicio = letter[1] - 6.20 * inch
    c.drawString(inch, y_inicio - altura_fila * 2.5 - 0.05 * inch, "-No extraer material vegetal ni semillas del jardin botánico.")
    y_inicio = letter[1] - 6.35 * inch  
    c.drawString(inch, y_inicio - altura_fila * 2.5 - 0.05 * inch, "-No arrojar basura en los senderos durante el recorrido.")
    y_inicio = letter[1] - 6.5 * inch 
    c.drawString(inch, y_inicio - altura_fila * 2.5 - 0.05 * inch,"-No cazar.")
    y_inicio = letter[1] - 6.65 * inch 
    c.drawString(inch, y_inicio - altura_fila * 2.5 - 0.05 * inch, "-No realizar fogatas o incendios.")
    #---------------------------------------------------------------------------
    y_inicio = letter[1] - 7 * inch
    hoy = datetime.now()
    dia = str(hoy.day)  
    mes_en = hoy.strftime("%B")  
    anio = str(hoy.year)  
    mes_es_dict = {
        "January": "Enero",
        "February": "Febrero",
        "March": "Marzo",
        "April": "Abril",
        "May": "Mayo",
        "June": "Junio",
        "July": "Julio",
        "August": "Agosto",
        "September": "Septiembre",
        "October": "Octubre",
        "November": "Noviembre",
        "December": "Diciembre",
    }
    mes_es = mes_es_dict.get(mes_en, mes_en) 
    texto_fecha = f"En mocoa a los {dia} días del mes de {mes_es} de {anio}"
    c.drawString(inch, y_inicio - altura_fila * 2.5 - 0.05 * inch, texto_fecha)
    #---------------------------------------------------------------------------
    y_inicio = letter[1] - 8.2 * inch 
    c.drawCentredString(letter[0] / 2, y_inicio, "AUTORIZACION")  
    #---------------------------------------------------------------------------
   
    y_inicio = letter[1] - 9.3 * inch
    c.setFont("Helvetica-Bold", fuente_tamano)
    line_width_firma = 3 * inch
    line_x_center = letter[0] / 2
    line_x_start_firma = line_x_center - line_width_firma / 2
    line_x_end_firma = line_x_start_firma + line_width_firma
    c.line(line_x_start_firma, y_inicio - 0.1 * inch, line_x_end_firma, y_inicio - 0.1 * inch)
    y_inicio = letter[1] - 9.6 * inch
    c.setFont("Helvetica-Bold", fuente_tamano)
    c.drawCentredString(letter[0] / 2, y_inicio, "HERNAN WILLIAM BURGOS N.")
    c.setFont("Helvetica", fuente_tamano)
    c.drawCentredString(letter[0] / 2, y_inicio - 0.15 * inch, "Técnico Operario \"JARBOTA\"")
    #---------------------------------------------------------------------------
    y_inicio = letter[1] - 9.8 * inch
    line_width = 7 * inch  
    line_x_start = (letter[0] - line_width) / 2
    line_x_end = line_x_start + line_width
    c.line(line_x_start, y_inicio - 0.1 * inch, line_x_end, y_inicio - 0.1 * inch)

    y_inicio = letter[1] - 10 * inch
    c.setFont("Helvetica", fuente_tamano - 1)
    sede_mocoa = "Sede Mocoa: \"Aire Libre\" Paraje B/ Luis Carlos Galán - 📞 4296105 - Subsede Sibundoy: \"Granja Versalles\" - 📞 4260437"
    correo = "Correo Electrónico: itputumayo@itp.edu.co Página Web: www.itp.edu.co"
    lema = "\"El saber como Arma de Vida\""

    # Centrar los textos
    c.drawCentredString(letter[0] / 2, y_inicio, sede_mocoa)
    c.drawCentredString(letter[0] / 2, y_inicio - 0.15 * inch, correo)
    c.drawCentredString(letter[0] / 2, y_inicio - 0.3 * inch, lema)
    #---------------------------------------------------------------------------
    c.save()
    output.seek(0)
    return send_file(output, mimetype='application/pdf', as_attachment=True, download_name=f"autorizacion_{codigo_visita}.pdf")

@app.route('/buscar_autorizacion/<codigo>')
def buscar_autorizacion(codigo):

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT codigo_visita, nombreresponsable, identificacion
            FROM autorizacion_ingreso
            WHERE codigo_visita = %s
        """, (codigo,))
        autorizacion_raw = cursor.fetchone()
        cursor.close()
        conn.close()

        if autorizacion_raw:
            autorizacion_dict = {
                'codigo_visita': autorizacion_raw[0],
                'nombreresponsable': autorizacion_raw[1],
                'identificacion': autorizacion_raw[2]
            }
            return jsonify({'autorizacion': autorizacion_dict})
        else:
            return jsonify({'error': f'No se encontró autorización con el código: {codigo}'}), 404
    except Exception as e:
        print(f"Error al buscar autorización: {e}")
        cursor.close()
        conn.close()
        return jsonify({'error': f'Error al buscar la autorización en la base de datos: {str(e)}'}), 500

#----------------------------------------------------------------------------------
# EXCEL
#----------------------------------------------------------------------------------
@app.route('/generar_excel')
def generar_excel():
    if not session.get('loggedin'):
        return redirect(url_for('login'))

    tipo_reporte = request.args.get('tipo')
    fecha_inicio_str = request.args.get('fecha_inicio')
    fecha_fin_str = request.args.get('fecha_fin')

    if not tipo_reporte or not fecha_inicio_str or not fecha_fin_str:
        return "Faltan parámetros para generar el Excel.", 400

    try:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
    except ValueError:
        return "Formato de fecha incorrecto.", 400

    conn = get_connection()
    cursor = conn.cursor()

    if tipo_reporte == 'autorizaciones':
        cursor.execute("SELECT codigo_visita, identificacion, nombreresponsable, ocupacion, entidad, direccion_barrio, municipio, telefono, objetivovisita, numeropersonas, vinculacion, hora_llegada, hora_salida, fecha FROM autorizacion_ingreso WHERE fecha BETWEEN %s AND %s", (fecha_inicio, fecha_fin))
        autorizaciones = cursor.fetchall()
        nombre_archivo = 'reporte_autorizaciones.xlsx'
        nombres_columnas = ['Código de Visita', 'Identificación', 'Nombre Responsable', 'Ocupación', 'Entidad', 'Dirección / Barrio', 'Municipio', 'Teléfono', 'Objetivo de la Visita', 'Número de Personas', 'Vinculación (General)', 'Hora de Llegada', 'Hora de Salida', 'Fecha']
    elif tipo_reporte == 'visitas':
        cursor.execute("SELECT fecha, nombrecompleto, numero_documento, tipo_persona, vinculacion_facultad, vinculacion_semestre, vinculacion_institucion, telefono, actividad_desarrollada, codigo_visita FROM asistencia_visita WHERE fecha BETWEEN %s AND %s", (fecha_inicio, fecha_fin))
        visitas = cursor.fetchall()
        nombre_archivo = 'reporte_visitas.xlsx'
        nombres_columnas = ['Fecha', 'Nombre Completo', 'Número de Documento', 'Tipo de Persona', 'Vinculación Facultad', 'Vinculación Semestre', 'Vinculación Institución', 'Teléfono', 'Actividad Desarrollada', 'Código de Visita']
    else:
        cursor.close()
        conn.close()
        return "Tipo de reporte no válido.", 400

    cursor.close()
    conn.close()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(nombres_columnas)

    if tipo_reporte == 'autorizaciones':
        for autorizacion in autorizaciones:
            ws.append(list(autorizacion))
    elif tipo_reporte == 'visitas':
        for visita in visitas:
            ws.append(list(visita))

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=nombre_archivo, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

#----------------------------------------------------------------------------------
# LOGIN USUARIO
#----------------------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Función para manejar el inicio de sesión de usuarios.
    """
    mensaje = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_connection() # Obtiene la conexión usando tu función
        if conn is None:
            mensaje = 'No se pudo conectar a la base de datos.'
            return render_template('login.html', mensaje=mensaje)

        try:
            cursor = conn.cursor(dictionary=True) # Usamos dictionary=True para obtener diccionarios
            cursor.execute('SELECT * FROM usuario WHERE username = %s AND password = %s', (username, password))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                return redirect(url_for('autorizacion_list'))  # Corrected this line
            else:
                mensaje = '¡Incorrecto username / password!'
        except mysql.connector.Error as e:
            print(f"Error de MySQL: {e}")
            mensaje = 'Error de base de datos: Por favor, inténtelo de nuevo.'
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    return render_template('login.html', mensaje=mensaje)
#----------------------------------------------------------------------------------
# PANEL ADMIN
#----------------------------------------------------------------------------------
def obtener_datos_autorizacion(codigo_visita):
    """
    Función para obtener los datos de una autorización de ingreso por su código de visita.

    Args:
        codigo_visita (str): El código de visita de la autorización.

    Returns:
        dict: Un diccionario con los datos de la autorización, o None si no se encuentra.
    """
    conn = get_connection()
    try: #manejo de errores
        cursor = conn.cursor(dictionary=True) #Usar siempre dictionary=True
        cursor.execute('SELECT * FROM autorizacion_ingreso WHERE codigo_visita = %s', (codigo_visita,))
        autorizacion = cursor.fetchone()
        return autorizacion
    except mysql.connector.Error as e:
        print(f"Error al obtener autorización: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            conn.close() #cerrar la conexion

@app.route('/lista_autorizacion', methods=['GET', 'POST'])
def autorizacion_list():
    """
    Función para mostrar la lista de autorizaciones de ingreso con paginación y ordenamiento.
    """
    conn = get_connection()
    if conn is None:
        return render_template('lista_autorizacion.html', error="No se pudo conectar a la base de datos")

    try:
        cursor = conn.cursor(dictionary=True)
        if not session.get('loggedin'):
            return redirect(url_for('login'))

        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))  # Registros por página
        order_by = request.args.get('order_by', 'codigo_visita')
        order_dir = request.args.get('order_dir', 'asc')

        # Validar las columnas de ordenamiento para evitar inyecciones SQL (simple whitelist)
        if order_by not in ['codigo_visita', 'nombreresponsable', 'fecha', 'hora_llegada', 'estado']:
            order_by = 'codigo_visita'
        if order_dir not in ['asc', 'desc']:
            order_dir = 'asc'

        offset = (page - 1) * per_page

        query = f"""
            SELECT ai.*, ea.estado, ea.motivo_estado
            FROM autorizacion_ingreso ai
            LEFT JOIN estado_autorizacion ea ON ai.id = ea.autorizacion_ingreso_id
            ORDER BY {order_by} {order_dir}
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (per_page, offset))
        autorizaciones = cursor.fetchall()

        # Obtener el total de registros para la paginación
        cursor.execute("SELECT COUNT(*) as total FROM autorizacion_ingreso")
        total_records = cursor.fetchone()['total']
        total_pages = (total_records + per_page - 1) // per_page

        return render_template(
            'lista_autorizacion.html',
            autorizaciones=autorizaciones,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            order_by=order_by,
            order_dir=order_dir
        )
    except mysql.connector.Error as e:
        print(f"Error al listar autorizaciones: {e}")
        return render_template('lista_autorizacion.html', error="Error al obtener la lista de autorizaciones")
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route('/actualizar_estado_autorizacion', methods=['POST'])
def actualizar_estado_autorizacion():
    """
    Función para actualizar el estado de una autorización de ingreso (Aceptar o Rechazar).
    """
    conn = get_connection()
    if conn is None:
        return render_template('lista_autorizacion.html', error="No se pudo conectar a la base de datos") # Mejor manejo de error
    try:
        cursor = conn.cursor(dictionary=True)
        if not session.get('loggedin'):
            return redirect(url_for('login'))

        if request.method == 'POST':
            autorizacion_id = request.form['autorizacion_id']
            estado = request.form['estado']
            motivo_estado = request.form.get('motivo_estado', None)

            # Validar que el estado sea válido
            if estado not in ('Aceptada', 'Rechazada', 'Pendiente'):
                return jsonify({'success': False, 'message': 'Estado no válido'})

            # Primero, verificar si ya existe un estado para esta autorización
            cursor.execute('SELECT * FROM estado_autorizacion WHERE autorizacion_ingreso_id = %s', (autorizacion_id,))
            existing_estado = cursor.fetchone()

            if existing_estado:
                # Si existe, actualizar el estado existente
                cursor.execute(
                    'UPDATE estado_autorizacion SET estado = %s, motivo_estado = %s, fecha_decision = NOW() WHERE autorizacion_ingreso_id = %s',
                    (estado, motivo_estado, autorizacion_id)
                )
            else:
                # Si no existe, insertar un nuevo registro de estado
                cursor.execute(
                    'INSERT INTO estado_autorizacion (autorizacion_ingreso_id, estado, motivo_estado, fecha_decision) VALUES (%s, %s, %s, NOW())',
                    (autorizacion_id, estado, motivo_estado)
                )
            conn.commit()
            # Redirigir a la lista de autorizaciones después de la actualización
            return redirect(url_for('autorizacion_list'))  # Cambiado a redirect
        else:
            return jsonify({'success': False, 'message': 'Método no permitido'})
    except mysql.connector.Error as e:
        print(f"Error al actualizar estado: {e}")
        conn.rollback()
        return render_template('lista_autorizacion.html', error=f"Error al actualizar el estado: {e}") # Envía el error a la página
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route('/ver_detalle_autorizacion/<codigo_visita>')
def ver_detalle_autorizacion(codigo_visita):
    """
    Función para ver el detalle de una autorización de ingreso.

    Args:
        codigo_visita (str): El código de visita de la autorización.

    Returns:
        str: Renderiza la plantilla 'detalle_autorizacion.html' con los detalles de la autorización.
    """
    conn = get_connection()
    if conn is None:
        return render_template('detalle_autorizacion.html', error="No se pudo conectar a la base de datos")
    try: #manejo de errores
        cursor = conn.cursor(dictionary=True) #Usar siempre dictionary=True
        if not session.get('loggedin'):
            return redirect(url_for('login'))

        autorizacion = obtener_datos_autorizacion(codigo_visita)
        if not autorizacion:
            return "Autorización no encontrada"  # O podrías renderizar una plantilla de error

        # Obtener el estado de la autorización
        cursor.execute('SELECT estado, motivo_estado FROM estado_autorizacion WHERE autorizacion_ingreso_id = %s', (autorizacion['id'],))
        estado_info = cursor.fetchone()

        estado = estado_info['estado'] if estado_info else 'Pendiente'
        motivo_estado = estado_info['motivo_estado'] if estado_info else None
        return render_template('detalle_autorizacion.html', autorizacion=autorizacion, estado=estado, motivo_estado=motivo_estado)
    except mysql.connector.Error as e:
        print(f"Error al ver detalle de autorización: {e}")
        return render_template('detalle_autorizacion.html', error="Error al obtener el detalle de la autorización")
    finally:
        if conn and conn.is_connected():
            conn.close() #cerrar la conexion
#----------------------------------------------------------------------------------
# LOGOUT
#----------------------------------------------------------------------------------
@app.route('/logout')
def logout():
    """
    Función para cerrar la sesión del usuario.
    """
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")