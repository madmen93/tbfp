from services.flujo_pacientes import menu_flujo_pacientes
from services.gestion_protocolos import generar_protocolo
from menus.menu_citas import menu_citas


def menu_principal():
    while True:
        print("\n==== Bienvenido al menu principal del TBMedic ====")
        print("(1) Gestión de citas")
        print("(2) Gestión de protocolos médicos")
        print("(3) Flujo de pacientes")
        print("(4) Indicadores de gestión")
        print("(5) Salir")
        
        opcion = input("\nEscoja la opción a realizar en esta oportunidad: ")

        if opcion == "1":
            menu_citas()
        elif opcion == "2":
            generar_protocolo()
        elif opcion == "3":
            menu_flujo_pacientes()
        elif opcion == "4":
            print("4")
        elif opcion == "5":
            break
        else:
            print("\nOpción inválida. Intente nuevamente")

