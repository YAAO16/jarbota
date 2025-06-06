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

def generar_diseno_pdf():
    output = BytesIO()
    c = canvas.Canvas(output, pagesize=letter)
    styles = getSampleStyleSheet()
    style_center = styles['Normal']
    style_center.alignment = TA_CENTER
    fuente_tamano = 8
    altura_fila = 0.25 * inch
    ancho_total = 7.1 * inch  # Ancho total del bloque de las tres columnas
    x_inicio = (letter[0] - ancho_total) / 2  # Centrar horizontalmente
    y_inicio = letter[1] - 1.8 * inch


    # --- Datos de Ejemplo para Pruebas ---
    autorizacion_prueba = {
        'nombreresponsable': "ADRIAN BURGS",
        'identificacion': "123456789",
        'ocupacion': "Ingeniero",
        'entidad': "Universidad del Putumayo",
        'direccion_barrio': "Barrio Centro",
        'municipio': "Mocoa",
        'telefono': "3101234567",
        'objetivovisita': "Realizar una exploración detallada de la diversidad florística presente en una zona específica de Mocoa, Putumayo, identificando las principales especies vegetales nativas y exóticas, y analizando su distribución y posibles usos locales, contribuyendo así al conocimiento de la riqueza biológica de la región amazónica colombiana",
        'numeropersonas': 5,
        'hora_llegada': datetime.now().time(),
        'hora_salida': datetime.now().time(),
        'fecha': datetime.now().date()
    }

    # --- Elementos Estáticos del Encabezado Centrado y Unido ---
    logo_path = "logo_jardin.png"  # Asegúrate de que la ruta sea correcta

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
    c.drawCentredString(x_texto_der + ancho_texto_der / 2, y_texto_centro_der - espacio_entre_lineas * -0.5, "F-JB-001")
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
    c.drawString(x_inicio + ancho_columna * 0.14, y_inicio + altura_fila * 0.1 - 0.45 * inch, "ADRIAN BURGOS")
    c.drawString(x_inicio + ancho_columna * 1.05, y_inicio + altura_fila * 0.1 - 0.45 * inch, "1193221281")
    c.drawString(x_inicio + ancho_columna * 2.05, y_inicio + altura_fila * 0.1 - 0.45 * inch, "DOCENTE")
    # --------------------------------------------------------------------------
    c.setFont("Helvetica-Bold", fuente_tamano - 0)
    c.drawString(x_inicio + ancho_columna * 0.14, y_inicio + altura_fila * 0.1 - 0.69 * inch, "ENTIDAD:")
    c.drawString(x_inicio + ancho_columna * 1.05, y_inicio + altura_fila * 0.1 - 0.69 * inch, "DIRECCION/BARRIO:")
    y_inicio = letter[1] - 2.05 * inch
    y_campo_fila2 = y_inicio - 3 * altura_fila
    c.rect(x_inicio, y_campo_fila2, ancho_columna, altura_fila)
    c.drawString(x_inicio + ancho_columna * 0.14, y_inicio + altura_fila * 0.1 - 0.69 * inch, "ITP")
    c.rect(x_inicio + ancho_columna, y_campo_fila2, ancho_columna * 2, altura_fila)
    c.drawString(x_inicio + ancho_columna * 1.05, y_inicio + altura_fila * 0.1 - 0.69 * inch, "LUIS CARLOS GALVAN")
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
    c.drawString(x_inicio + ancho_columna * 0.14, y_inicio + altura_fila * 0.1 - 0.69 * inch, "MOCOA")
    c.rect(x_inicio + ancho_columna, y_campo_fila2, ancho_columna * 2, altura_fila)
    c.drawString(x_inicio + ancho_columna * 1.05, y_inicio + altura_fila * 0.1 - 0.69 * inch, "3144046644") 
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
    texto = autorizacion_prueba.get('objetivovisita', '')

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
    c.drawString(x_inicio + ancho_columna * 1.05, y_inicio + altura_fila * 0.1 - 0.69 * inch, "16") 
    y_inicio = letter[1] - 4.45 * inch
    c.setFont("Helvetica-Bold", fuente_tamano - 0)
    c.drawString(inch, y_inicio - altura_fila * 2.5 - 0.05 * inch, "Facultad - Semestre - Institución:")
    y_campo_fila2 = y_inicio - 3 * altura_fila
    c.rect(x_inicio, y_campo_fila2, ancho_columna, altura_fila)
    c.rect(x_inicio + ancho_columna, y_campo_fila2, ancho_columna * 2, altura_fila)
    c.drawString(x_inicio + ancho_columna * 1.05, y_inicio + altura_fila * 0.1 - 0.69 * inch, "INGENIERIA DE SISTEMAS-9-ITP")
    y_inicio = letter[1] - 4.7 * inch
    c.setFont("Helvetica-Bold", fuente_tamano - 0)
    c.drawString(inch, y_inicio - altura_fila * 2.5 - 0.05 * inch, "Hora de llegada:")
    y_campo_fila2 = y_inicio - 3 * altura_fila
    c.rect(x_inicio, y_campo_fila2, ancho_columna, altura_fila)
    c.rect(x_inicio + ancho_columna, y_campo_fila2, ancho_columna * 2, altura_fila)
    c.drawString(x_inicio + ancho_columna * 1.05, y_inicio + altura_fila * 0.1 - 0.69 * inch, "12:00")
    y_inicio = letter[1] - 4.95 * inch
    c.setFont("Helvetica-Bold", fuente_tamano - 0)
    c.drawString(inch, y_inicio - altura_fila * 2.5 - 0.05 * inch, "Hora de salida:")
    y_campo_fila2 = y_inicio - 3 * altura_fila
    c.rect(x_inicio, y_campo_fila2, ancho_columna, altura_fila)
    c.rect(x_inicio + ancho_columna, y_campo_fila2, ancho_columna * 2, altura_fila)
    c.drawString(x_inicio + ancho_columna * 1.05, y_inicio + altura_fila * 0.1 - 0.69 * inch, "02:00")
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
    return output


if __name__ == '__main__':
    from flask import Flask, send_file
    
    app_prueba = Flask(__name__)

    @app_prueba.route('/diseno_pdf')
    def mostrar_diseno_pdf():
        pdf_bytes = generar_diseno_pdf()
        return send_file(
            pdf_bytes,
            mimetype='application/pdf',
            as_attachment=False,  # Para mostrar en el navegador
            download_name="diseno_autorizacion.pdf"
        )

    app_prueba.run(debug=True, host="0.0.0.0")