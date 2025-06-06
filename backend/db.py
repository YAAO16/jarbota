import mysql.connector

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="asistencia",
            user="root",
            password="root",
            database="asistencia"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Error al conectar a la base de datos: {err}")
        return None