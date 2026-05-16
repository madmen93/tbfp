# =====================================================
# SISTEMA DE FLUJO DE PACIENTES
# =====================================================

areas = {
    "Triaje": [],
    "Laboratorio": [],
    "Audiometría": [],
    "Rayos X": [],
    "Medicina Ocupacional": []
}

LIMITE = 5


def registrar_paciente_en_area():
    while True:
        nombre = input("\nIngrese nombre del paciente: ").strip()

        if not nombre:
            print("El nombre no puede estar vacío.")
            continue

        if any(c.isdigit() for c in nombre):
            print("El nombre no debe contener números.")
            continue

        break

    print("\nÁREAS DISPONIBLES")
    print("1. Triaje")
    print("2. Laboratorio")
    print("3. Audiometría")
    print("4. Rayos X")
    print("5. Medicina Ocupacional")

    opcion_area = input("\nSeleccione área: ")

    if opcion_area == "1":
        area = "Triaje"
    elif opcion_area == "2":
        area = "Laboratorio"
    elif opcion_area == "3":
        area = "Audiometría"
    elif opcion_area == "4":
        area = "Rayos X"
    elif opcion_area == "5":
        area = "Medicina Ocupacional"
    else:
        print("Área inválida.")
        return

    areas[area].append(nombre)

    print("\nPaciente registrado correctamente en el área:", area)

    verificar_saturacion(area)


def verificar_saturacion(area):
    if len(areas[area]) > LIMITE:
        print(f"ALERTA: El área de {area} está SATURADA.")

        for nombre_area, lista in areas.items():
            if len(lista) < LIMITE:
                print(f"Recomendación: redirigir pacientes a {nombre_area}.")
                break


def ver_estado_areas():
    print("\n=== ESTADO DE ÁREAS ===")

    for area, lista in areas.items():
        cantidad = len(lista)

        print(f"\nÁrea: {area}")
        print(f"Cantidad de pacientes: {cantidad}")

        if cantidad > LIMITE:
            print("Estado: SATURADA")
        else:
            print("Estado: DISPONIBLE")


def ver_pacientes_por_area():
    print("\n=== PACIENTES POR ÁREA ===")

    for area, lista in areas.items():
        print(f"\nÁREA: {area}")

        if lista:
            for paciente in lista:
                print(f"- {paciente}")
        else:
            print("No hay pacientes registrados.")


def menu_flujo_pacientes():
    while True:
        print("\n=== CONTROL DE FLUJO DE PACIENTES ===")
        print("1. Registrar paciente en área")
        print("2. Ver estado de áreas")
        print("3. Ver pacientes por área")
        print("4. Volver al menú principal")

        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":
            registrar_paciente_en_area()
        elif opcion == "2":
            ver_estado_areas()
        elif opcion == "3":
            ver_pacientes_por_area()
        elif opcion == "4":
            break
        else:
            print("Opción inválida.")