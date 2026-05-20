from datetime import datetime

TIPOS_EXAMEN = ["Ingreso", "Anual", "Salida", "Alto Riesgo"]

# Cotizaciones sueltas (no asignadas a cita) registradas durante la sesión
cotizaciones = []


def registrar_cotizacion(opcion, es_mina, riesgos_seleccionados):
    proto = construir_protocolo(opcion, es_mina, riesgos_seleccionados)
    proto["id"] = f"COT-{len(cotizaciones) + 1:03d}"
    proto["timestamp"] = datetime.now()
    proto["tipo"] = OPCION_A_TIPO.get(opcion, opcion)
    proto["cita_asignada"] = None
    cotizaciones.append(proto)
    return proto

TIPO_A_OPCION = {
    "Ingreso": "1",
    "Anual": "2",
    "Salida": "3",
    "Alto Riesgo": "4",
}

OPCION_A_TIPO = {v: k for k, v in TIPO_A_OPCION.items()}

# Orden lógico del flujo. El paciente recorre las áreas en este orden.
ORDEN_AREAS = ["Triaje", "Laboratorio", "Audiometría", "Rayos X", "Medicina Ocupacional"]

# Mapeo descripción de examen -> área del flujo
EXAMEN_A_AREA = {
    "Médica Ocupacional": "Medicina Ocupacional",
    "Evaluación Visual": "Triaje",
    "Audiométrica": "Audiometría",
    "Audiometría": "Audiometría",
    "Evaluación Laboratorio": "Laboratorio",
    "Radiográfica de Tórax": "Rayos X",
    "Espirometría": "Laboratorio",
    "Enfermedades Ocupacionales": "Medicina Ocupacional",
    "Medicina General": "Medicina Ocupacional",
}

RIESGOS_DISPONIBLES = [
    "Trabajo en altura (> 1.80m)",
    "Espacios confinados",
    "Manipulación de Químicos",
    "Operadores de maquinaria pesada",
    "Exposición a Radiaciones",
]


def _items_por_opcion(opcion, es_mina, riesgos_seleccionados):
    items = []

    if opcion == "1":
        items.extend([
            ("Médica Ocupacional", 50),
            ("Evaluación Visual", 40),
            ("Audiométrica", 75),
            ("Evaluación Laboratorio", 100),
        ])
        if es_mina:
            items.append(("Espirometría (Condición Mina)", 120))

    elif opcion == "2":
        items.extend([
            ("Médica Ocupacional", 50),
            ("Evaluación Laboratorio", 100),
            ("Radiográfica de Tórax", 60),
            ("Audiometría", 75),
        ])
        if es_mina:
            items.append(("Espirometría (Condición Mina)", 120))

    elif opcion == "3":
        items.extend([
            ("Enfermedades Ocupacionales", 210),
            ("Audiometría", 75),
            ("Medicina General", 80),
        ])
        if es_mina:
            items.append(("Espirometría (Condición Mina)", 120))

    elif opcion == "4":
        items.append(("Alto riesgo - evaluación complementaria", 0))

    else:
        raise ValueError("Opción inválida")

    riesgo_map = {r: f"Alto Riesgo: {r}" for r in RIESGOS_DISPONIBLES}
    for riesgo in riesgos_seleccionados or []:
        etiqueta = riesgo_map.get(riesgo)
        if etiqueta:
            items.append((etiqueta, 420))

    return items


def items_a_areas(items):
    """Convierte la lista de exámenes a áreas del flujo, en orden lógico."""
    areas_requeridas = set()
    for desc, _ in items:
        matched = False
        for clave, area in EXAMEN_A_AREA.items():
            if desc.startswith(clave):
                areas_requeridas.add(area)
                matched = True
                break
        if not matched and (desc.startswith("Alto Riesgo:") or desc.startswith("Alto riesgo")):
            areas_requeridas.add("Medicina Ocupacional")
    # Siempre comienza por Triaje
    areas_requeridas.add("Triaje")
    return [a for a in ORDEN_AREAS if a in areas_requeridas]


def construir_protocolo(opcion, es_mina, riesgos_seleccionados):
    """Devuelve un dict con items, total, texto formateado y áreas a recorrer."""
    items = _items_por_opcion(opcion, es_mina, riesgos_seleccionados)
    total = sum(p for _, p in items)
    areas = items_a_areas(items)

    lines = [
        "=" * 50,
        "         PROTOCOLO MÉDICO Y COTIZACIÓN          ",
        "=" * 50,
        "TIPO: ENTORNO MINERO" if es_mina else "TIPO: PLANTA / GENERAL",
        "-" * 50,
    ]
    for descripcion, precio in items:
        lines.append(f" - {descripcion:<35} S/ {precio:>6.2f}")
    lines.append("-" * 50)
    lines.append(f" TOTAL A PAGAR:{'':<20} S/ {total:>6.2f}")
    lines.append("-" * 50)
    lines.append(" RUTA DEL PACIENTE:")
    lines.append("   " + " → ".join(areas))
    lines.append("=" * 50)

    return {
        "items": items,
        "total": total,
        "areas": areas,
        "es_mina": es_mina,
        "riesgos": list(riesgos_seleccionados or []),
        "texto": "\n".join(lines),
    }


def crear_protocolo(opcion, es_mina, riesgos_seleccionados):
    """Compatibilidad: retorna solo el texto formateado."""
    return construir_protocolo(opcion, es_mina, riesgos_seleccionados)["texto"]


def generar_protocolo():
    print("=" * 50)
    print("      SISTEMA DE GENERACIÓN DE PROTOCOLOS      ")
    print("=" * 50)
    print("\nSeleccione el tipo de examen:")
    for code, label in OPCION_A_TIPO.items():
        print(f"{code}. Examen {label}")
    opcion = input("Ingrese una opción (1-4): ").strip()

    es_mina = False
    if opcion in ["1", "2", "3"]:
        mina_input = input("\n¿El examen es para personal de Mina? (S/N): ").strip().upper()
        es_mina = mina_input == "S"

    riesgos_input = ""
    if opcion in ["1", "2", "3", "4"]:
        print("\n--- EVALUACIÓN DE TRABAJOS DE ALTO RIESGO ---")
        for i, r in enumerate(RIESGOS_DISPONIBLES, 1):
            print(f"{i}. {r}")
        print("0. Ninguno / No aplica")
        riesgos_input = input("Ingrese opciones separadas por comas: ").strip()

    lista_riesgos = []
    if riesgos_input and riesgos_input != "0":
        opciones = [r.strip() for r in riesgos_input.split(",")]
        for op in opciones:
            try:
                idx = int(op) - 1
                if 0 <= idx < len(RIESGOS_DISPONIBLES):
                    lista_riesgos.append(RIESGOS_DISPONIBLES[idx])
            except ValueError:
                pass

    try:
        texto = crear_protocolo(opcion, es_mina, lista_riesgos)
    except ValueError:
        print("\n[!] Opción inválida.")
        return
    print(texto)
