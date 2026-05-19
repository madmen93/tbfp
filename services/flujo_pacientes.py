# =====================================================
# SISTEMA INTELIGENTE DE FLUJO DE PACIENTES
# =====================================================

areas = {
    "Triaje": [],
    "Laboratorio": [],
    "Audiometría": [],
    "Rayos X": [],
    "Medicina Ocupacional": []
}

# TIEMPO ESTIMADO POR AREA
tiempos = {
    "Triaje": 5,
    "Laboratorio": 10,
    "Audiometría": 8,
    "Rayos X": 12,
    "Medicina Ocupacional": 15
}

LIMITE = 5
contador = 0


# =====================================================
# REGISTRAR PACIENTE
# =====================================================

def registrar_paciente():

    global contador

    while True:

        nombre = input("\nIngrese nombre del paciente: ").strip()

        # OPERADORES LOGICOS
        if not nombre or any(c.isdigit() for c in nombre):
            print("❌ Nombre inválido.")
            continue

        break

    # MOSTRAR AREAS
    print("\nÁREAS DISPONIBLES")

    lista_areas = list(areas.keys())

    for i, area in enumerate(lista_areas, start=1):
        print(f"{i}. {area}")

    try:
        opcion = int(input("\nSeleccione área: "))

        area = lista_areas[opcion - 1]

    except:
        print("❌ Área inválida.")
        return

    # CODIGO AUTOMATICO
    contador += 1
    codigo = f"PAC-{contador:03}"

    # REGISTRO
    areas[area].append(nombre)

    # TIEMPO DE ESPERA
    espera = len(areas[area]) * tiempos[area]

    print("\n✅ PACIENTE REGISTRADO")
    print(f"Código: {codigo}")
    print(f"Área: {area}")
    print(f"⏳ Tiempo estimado: {espera} min")

    verificar_saturacion(area)


# =====================================================
# SATURACION Y RECOMENDACION
# =====================================================

def verificar_saturacion(area):

    cantidad = len(areas[area])

    if cantidad > LIMITE:

        print(f"\n🔴 ALERTA: {area} SATURADA")

        # RECOMENDACION AUTOMATICA
        disponibles = []

        for nombre_area, lista in areas.items():

            if len(lista) < LIMITE and nombre_area != area:
                disponibles.append(nombre_area)

        if disponibles:
            print(f"✅ Redirigir pacientes a: {disponibles[0]}")

    # AREA CRITICA
    if area == "Triaje" and cantidad > LIMITE:
        print("⚠️ Área crítica detectada")


# =====================================================
# ESTADO DE AREAS
# =====================================================

def ver_estado_areas():

    print("\n=== ESTADO DE ÁREAS ===")

    for area, lista in areas.items():

        cantidad = len(lista)

        if cantidad > LIMITE:
            estado = "🔴 SATURADA"

        elif cantidad >= 3:
            estado = "🟡 EN OBSERVACIÓN"

        else:
            estado = "🟢 DISPONIBLE"

        print(f"\nÁrea: {area}")
        print(f"Pacientes: {cantidad}")
        print(f"Estado: {estado}")


# =====================================================
# PACIENTES POR AREA
# =====================================================

def ver_pacientes():

    print("\n=== PACIENTES POR ÁREA ===")

    for area, lista in areas.items():

        print(f"\n📌 {area}")

        if lista:

            for paciente in lista:
                print(f"• {paciente}")

        else:
            print("Sin pacientes")


# =====================================================
# ESTADISTICAS
# =====================================================

def ver_estadisticas():

    total = sum(len(lista) for lista in areas.values())

    print("\n=== ESTADÍSTICAS ===")
    print(f"👥 Total de pacientes: {total}")

    # AREA MAS CONCURRIDA
    mayor = max(areas, key=lambda x: len(areas[x]))

    print(f"🏥 Área más concurrida: {mayor}")

    # AREAS SATURADAS
    saturadas = [a for a, l in areas.items() if len(l) > LIMITE]

    if saturadas:
        print("🔴 Áreas saturadas:")

        for area in saturadas:
            print(f"• {area}")

    else:
        print("🟢 No hay áreas saturadas")


# =====================================================
# MENU PRINCIPAL
# =====================================================

def menu_flujo_pacientes():

    while True:

        print("\n" + "=" * 50)
        print(" SISTEMA INTELIGENTE HOSPITALARIO ")
        print("=" * 50)

        print("1. Registrar paciente")
        print("2. Ver estado de áreas")
        print("3. Ver pacientes por área")
        print("4. Ver estadísticas")
        print("5. Salir")

        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":
            registrar_paciente()

        elif opcion == "2":
            ver_estado_areas()

        elif opcion == "3":
            ver_pacientes()

        elif opcion == "4":
            ver_estadisticas()

        elif opcion == "5":
            print("\nGracias por usar el sistema.")
            break

        else:
            print("❌ Opción inválida")


# =====================================================
# INICIAR SISTEMA
# =====================================================

menu_flujo_pacientes()