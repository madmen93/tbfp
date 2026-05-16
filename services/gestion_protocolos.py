def generar_protocolo():
    print("=" * 50)
    print("      SISTEMA DE GENERACIÓN DE PROTOCOLOS      ")
    print("=" * 50)

    print("\nSeleccione el tipo de examen:")
    print("1. Examen de Ingreso")
    print("2. Examen Anual")
    print("3. Examen de Salida")
    print("4. Solo Trabajos de Alto Riesgo")

    opcion = input("Ingrese una opción (1-4): ").strip()

    es_mina = False
    if opcion in ["1", "2", "3"]:
        mina_input = input("\n¿El examen es para personal de Mina? (S/N): ").strip().upper()
        es_mina = mina_input == "S"

    items_protocolo = []
    total = 0

    if opcion == "1":
        print("\n--- PROCESANDO: PROTOCOLO EXAMEN DE INGRESO ---")
        items_protocolo.append(("Médica Ocupacional", 50))
        items_protocolo.append(("Evaluación Visual", 40))
        items_protocolo.append(("Audiométrica", 75))
        items_protocolo.append(("Evaluación Laboratorio", 100))

        if es_mina:
            items_protocolo.append(("Espirometría (Condición Mina)", 120))

    elif opcion == "2":
        print("\n--- PROCESANDO: PROTOCOLO EXAMEN ANUAL ---")
        items_protocolo.append(("Médica Ocupacional", 50))
        items_protocolo.append(("Evaluación Laboratorio", 100))
        items_protocolo.append(("Radiográfica de Tórax", 60))
        items_protocolo.append(("Audiometría", 75))

        if es_mina:
            items_protocolo.append(("Espirometría (Condición Mina)", 120))

    elif opcion == "3":
        print("\n--- PROCESANDO: PROTOCOLO EXAMEN DE SALIDA ---")
        items_protocolo.append(("Enfermedades Ocupacionales", 210))
        items_protocolo.append(("Audiometría", 75))
        items_protocolo.append(("Medicina General", 80))

        if es_mina:
            items_protocolo.append(("Espirometría (Condición Mina)", 120))

    elif opcion == "4":
        print("\n--- PROCESANDO: PROTOCOLO SOLO ALTO RIESGO ---")

    else:
        print("\n[!] Opción inválida.")
        return

    print("\n--- EVALUACIÓN DE TRABAJOS DE ALTO RIESGO ---")
    print("Seleccione las actividades de alto riesgo que aplican:")
    print("1. Trabajo en altura (> 1.80m)")
    print("2. Espacios confinados")
    print("3. Manipulación de Químicos")
    print("4. Operadores de maquinaria pesada")
    print("5. Exposición a Radiaciones")
    print("0. Ninguno / No aplica")

    riesgos_input = input("Ingrese opciones separadas por comas: ").strip()

    lista_riesgos_seleccionados = []

    if riesgos_input != "0" and riesgos_input != "":
        opciones_riesgo = [r.strip() for r in riesgos_input.split(",")]

        dicc_riesgos = {
            "1": "Trabajo en altura (> 1.80m)",
            "2": "Espacios confinados",
            "3": "Manipulación de Químicos",
            "4": "Operadores de maquinaria pesada",
            "5": "Exposición a Radiaciones"
        }

        for op in opciones_riesgo:
            if op in dicc_riesgos:
                lista_riesgos_seleccionados.append(dicc_riesgos[op])

    for riesgo in lista_riesgos_seleccionados:
        items_protocolo.append((f"Alto Riesgo: {riesgo}", 420))

    print("\n" + "=" * 50)
    print("         PROTOCOLO MÉDICO Y COTIZACIÓN          ")
    print("=" * 50)

    if es_mina:
        print("TIPO: ENTORNO MINERO")
    else:
        print("TIPO: PLANTA / GENERAL")

    print("-" * 50)

    for descripcion, precio in items_protocolo:
        print(f" - {descripcion:<35} S/ {precio:>6.2f}")
        total += precio

    print("-" * 50)
    print(f" TOTAL A PAGAR:{'':<20} S/ {total:>6.2f}")
    print("=" * 50)
    print("Documento listo para su emisión directa.")
    print("=" * 50)