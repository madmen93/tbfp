from services.flujo_pacientes import menu_flujo_pacientes
from services.gestion_protocolos import generar_protocolo
from services.kpi_operativo import mostrar_kpi
from services.grafico_kpi import mostrar_diagrama_pareto
from menus.menu_citas import menu_citas


def menu_indicadores():
    while True:
        print("\n==== INDICADORES DE GESTIÓN ====")
        print("(1) Ver KPI operativo")
        print("(2) Abrir diagrama de Pareto")
        print("(3) Volver")

        opcion = input("\nSeleccione: ")
        if opcion == "1":
            print(mostrar_kpi())
        elif opcion == "2":
            mostrar_diagrama_pareto()
        elif opcion == "3":
            break
        else:
            print("Opción inválida.")


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
            menu_indicadores()
        elif opcion == "5":
            break
        else:
            print("\nOpción inválida. Intente nuevamente")
