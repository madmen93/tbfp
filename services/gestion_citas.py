from models.cita import Cita

lista_citas = []

TOPE_POR_HORARIO = 15

HORAS_DISPONIBLES = [
    "19:00", "19:15", "19:30", "19:45",
    "20:00", "20:15", "20:30", "20:45",
    "21:00", "21:15", "21:30", "21:45",
    "22:00",
]


def contar_citas_horario(fecha, hora):
    return sum(1 for c in lista_citas if c.fecha == fecha and c.hora == hora)


def contar_citas_fecha(fecha):
    return sum(1 for c in lista_citas if c.fecha == fecha)

# GENERADOR DE ID CITAS

def generar_id_cita():
    numero = len(lista_citas) + 1
    return f"C{numero:04d}"

# REGISTRAR CITA

def registrar_cita(cita):
    lista_citas.append(cita)
    print("\nCita registrada correctamente.")

# MOSTRAR CITA

def mostrar_citas():

    for cita in lista_citas:
        cita.mostrar_cita()

# EDITAR CITA

def editar_cita():

    idCita = input("\nIngrese el id de la cita a editar: ")

    for cita in lista_citas:
        if cita.id_cita == idCita:
            print("=== CITA ENCONTRADA ===")
            cita.mostrar_cita()
            print("\nIngrese los nuevos datos de la cita")

            nuevaFecha = input("Nueva fecha: ")
            nuevaHora = input("Nueva hora: ")

            cita.fecha = nuevaFecha
            cita.hora = nuevaHora

            print("\nCita actualizada correctamente.")
        else:
            print("\nNo se encontró la cita.")
            #¿Break?

# ELIMINAR CITA

def eliminar_cita():
     
     idCita = input("\nIngrese el id de la cita a eliminar: ")

     for cita in lista_citas:
        if cita.id_cita == idCita:
            print("=== CITA ENCONTRADA ===")
            cita.mostrar_cita()
            
            confirmacion = input(f"\n¿Está seguro de eliminar la cita {idCita}? \nEscriba: \n(1) si desea continuar con la eliminación o \n(0) si desea cancelar la acción: ")

            if confirmacion == "1":
                lista_citas.remove(cita)
                print("\nCita correctamente eliminada")
            elif confirmacion == "0":
                print("\nAcción cancelada")
            else:
                print("No se reconoce este comando.")
        else:
            print("\nNo se encontró la cita.")


# VALIDACIÓN  DEL TOPE DE CITAS POR HORA

def validar_tope_atenciones(fecha, hora):
    contador = 0

    for cita in lista_citas:
        if cita.fecha == fecha and cita.hora == hora:
            contador += 1

    return contador < TOPE_POR_HORARIO
        
         
         
