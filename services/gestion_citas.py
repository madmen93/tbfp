from models.cita import Cita

lista_citas = []

def registrar_cita(cita):
    lista_citas.append(cita)

def mostrar_citas():

    for cita in lista_citas:
        cita.mostrar_cita()