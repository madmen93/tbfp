from utils.validaciones import validar_dni, validar_solo_letras, validar_hora, validar_edad, validar_fecha, validar_texto_no_vacio, validar_nombre_completo

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

def pedir_empresa():
    while True:
        empresa = input("Razón social: ").upper()

        if validar_texto_no_vacio(empresa):
            return empresa

        print("No debe estar vacío.")


def pedir_nombre():
    while True:
        nombre = input("Nombre completo del paciente: ").upper()

        if validar_texto_no_vacio(nombre) and validar_solo_letras(nombre) and validar_nombre_completo(nombre):
            return nombre

        print("Nombre inválido: no debe estar vacío ni contener números y debe contener al menos un nombre y dos apellidos.")


def pedir_dni():
    while True:
        dni = input("Documento de identidad: ")

        if validar_dni(dni):
            return dni

        print("DNI inválido: debe contener 8 dígitos.")


def pedir_edad():
    while True:
        edad = input("Edad del paciente: ")

        if validar_edad(edad):
            return int(edad)

        print("Edad inválida: el paciente debe ser mayor de edad")

def pedir_fecha():
    while True:
        fecha = input("Fecha (dd/mm/aaaa): ")

        if validar_fecha(fecha):
            return fecha

        print("Fecha inválida: La cita de programarse a partir del día de mañana y con el formato dd/mm/aaaa.")


def pedir_hora():
    while True:
        hora = input("Hora (HH:MM): ")

        if validar_hora(hora):
            return hora

        print("Hora inválida: las citas solo pueden registrarse entre 07:00 y 11:00, use el formato HH:MM.")