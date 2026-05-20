from datetime import datetime, date, timedelta

def validar_nombre_completo(nombre):

    palabras = nombre.strip().split()

    return len(palabras) >= 3

def validar_texto_no_vacio(texto):
    return texto.strip() != ""

def validar_solo_letras(texto):
    return texto.replace(" ", "").isalpha()


def validar_dni(dni):
    return dni.isdigit() and len(dni) == 8


def validar_edad(edad):
    return edad.isdigit() and int(edad) > 17

def validar_fecha(fecha):
    try:
        fecha_cita = datetime.strptime(fecha, "%d/%m/%Y").date()
        return fecha_cita >= date.today()

    except ValueError:
        return False
    

def validar_hora(hora):

    try:
        hora_cita = datetime.strptime(hora, "%H:%M").time()

        hora_inicio = datetime.strptime("19:00", "%H:%M").time()
        hora_fin = datetime.strptime("22:00", "%H:%M").time()

        return hora_inicio <= hora_cita <= hora_fin

    except ValueError:
        return False
    
