def menu_tipo_examen():
    while True:
        print("\n==Tipo de examen==")
        print("(1) Preocupacional")
        print("(2) Periódico")
        print("(3) Retiro")
        print("(4) Otro")
        print("(5) Salir")

        opcion = input("\nIngrese la opción a realizar: ")

        if opcion == "1":
            return "Preocupacional"
        elif opcion == "2":
            return "Periódico"
        elif opcion == "3":
            return "Retiro"
        elif opcion == "4":
            return "Otro"
        elif opcion == "5":
            break
        else:
            print("Opción inválida. Intente nuevamente.")

def menu_perfil_examen():
    while True:
        print("\n==Perfil de examen==")
        print("(1) Administrativo")
        print("(2) Operativo")
        print("(3) Mina")
        print("(4) Alto riesgo")
        print("(5) Salir")

        opcion = input("\nIngrese la opción a realizar: ")

        if opcion == "1":
            return "Administrativo"
        elif opcion == "2":
            return "Operativo"
        elif opcion == "3":
            return "Mina"
        elif opcion == "4":
            return "Alto riesgo"
        elif opcion == "5":
            break
        else:
            print("Opción inválida. Intente nuevamente.")

def menu_sexo():
    while True:
        print("\n==Sexo del paciente==")
        print("(1) Masculino")
        print("(2) Femenino")

        opcion = input("\nIngrese la opción correspondiente: ")

        if opcion == "1":
            return "Masculino"
        elif opcion == "2":
            return "Femenino"
        else:
            print("Opción inválida. Intente nuevamente.")