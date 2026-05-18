from models.paciente import Paciente
from models.cita import Cita
from models.emo import Emo
from menus.menu_auxiliares import menu_perfil_examen, menu_tipo_examen, menu_sexo
from services.gestion_citas import generar_id_cita, mostrar_citas, registrar_cita, editar_cita,eliminar_cita


def menu_citas():
    while True:
        print("\n===GESTIÓN DE CITAS MÉDTICAS===")
        print("(1) Registrar cita")
        print("(2) Mostrar citas")
        print("(3) Editar cita")
        print("(4) Eliminar cita")
        print("(5) Salir")

        opcion = input("Escoja la opción que desea realizar: ")

        if opcion == "1":
            empresa = input("Razon social: ")
            nombre = input("Nombre completo del paciente: ")
            idPaciente = input("Documento de identidad: ")
            edad = input("Edad del paciente: ")
            sexo = menu_sexo()

            paciente = Paciente(nombre, idPaciente, edad, sexo, empresa)

            tipo = menu_tipo_examen()
            perfil = menu_perfil_examen()

            emo = Emo(tipo, perfil)

            idCita = generar_id_cita()
            fecha = input("Fecha: ")
            hora = input("Hora: ")

            cita = Cita(idCita, paciente, fecha, hora, emo)

            registrar_cita(cita)
            break

        elif opcion == "2":
            mostrar_citas()
            break
        elif opcion == "3":
            editar_cita()
            break
        elif opcion == "4":
            eliminar_cita()
            break
        elif opcion == "5":
            break
        else:
            print("Opción inválida. Intente nuevamente.")
