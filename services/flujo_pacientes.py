# =====================================================
# SISTEMA INTELIGENTE DE FLUJO DE PACIENTES
# Las colas contienen objetos Cita.
# El paciente avanza por las áreas que define su protocolo.
# =====================================================
import random
from datetime import datetime

TIEMPO_MIN_ATENCION = 5
TIEMPO_MAX_ATENCION = 20

areas = {
    "Triaje": [],
    "Laboratorio": [],
    "Audiometría": [],
    "Rayos X": [],
    "Medicina Ocupacional": []
}

# Tiempo promedio por atención (en min). Se usa para estimar tiempo en cola.
# El tiempo real es aleatorio entre TIEMPO_MIN_ATENCION y TIEMPO_MAX_ATENCION por persona.
_TIEMPO_PROMEDIO = (TIEMPO_MIN_ATENCION + TIEMPO_MAX_ATENCION) // 2  # 12

tiempos = {
    "Triaje": _TIEMPO_PROMEDIO,
    "Laboratorio": _TIEMPO_PROMEDIO,
    "Audiometría": _TIEMPO_PROMEDIO,
    "Rayos X": _TIEMPO_PROMEDIO,
    "Medicina Ocupacional": _TIEMPO_PROMEDIO,
}

LIMITE = 5


def _quitar_de_todas(cita):
    for area_lista in areas.values():
        if cita in area_lista:
            area_lista.remove(cita)


def iniciar_flujo_desde_cita(cita):
    """Mueve una cita programada al inicio de su ruta de atención."""
    from services import kpi_operativo as kpi
    from models.cita import Cita

    if cita.estado not in (Cita.ESTADO_PROGRAMADA,):
        kpi.registrar_error("flujo", f"Cita {cita.id_cita} no está programada (estado: {cita.estado})")
        return None

    if not cita.areas_pendientes:
        kpi.registrar_error("flujo", f"Cita {cita.id_cita} no tiene áreas pendientes (protocolo vacío)")
        return None

    primer_area = cita.areas_pendientes[0]
    areas[primer_area].append(cita)
    cita.area_actual = primer_area
    cita.estado = Cita.ESTADO_EN_FLUJO
    cita.tiempos_por_area[primer_area] = {"ingreso": datetime.now(), "atencion": None, "espera_min": 0}
    return primer_area


def atender_paciente(area, indice=0):
    """Atiende al paciente del índice indicado en la cola del área (0 = primero).
    Lo mueve al siguiente área de su protocolo o cierra la cita si terminó.
    """
    from services import kpi_operativo as kpi
    from models.cita import Cita

    if area not in areas:
        kpi.registrar_error("flujo", f"Área inválida al atender: {area}")
        return None

    if not areas[area]:
        kpi.registrar_error("flujo", f"Intento de atender en '{area}' sin pacientes en cola.")
        return None

    if indice < 0 or indice >= len(areas[area]):
        kpi.registrar_error("flujo", f"Índice {indice} fuera de rango en cola de '{area}'.")
        return None

    cita = areas[area].pop(indice)
    posicion_al_ingresar = (indice + 1)
    # Tiempo de espera realista: suma de tiempos de atención aleatorios (5-20 min)
    # de cada persona que estaba delante (incluido el propio paciente)
    tiempo_espera = sum(
        random.randint(TIEMPO_MIN_ATENCION, TIEMPO_MAX_ATENCION)
        for _ in range(posicion_al_ingresar)
    )

    if area in cita.areas_pendientes:
        cita.areas_pendientes.remove(area)
    cita.areas_completadas.append(area)

    # Trazabilidad: cerrar la atención del área actual
    paso = cita.tiempos_por_area.setdefault(
        area, {"ingreso": datetime.now(), "atencion": None, "espera_min": 0}
    )
    paso["atencion"] = datetime.now()
    paso["espera_min"] = tiempo_espera

    kpi.registrar_atencion(area, cita.paciente.nombre, tiempo_espera, cita=cita)

    siguiente_area = None
    if cita.areas_pendientes:
        siguiente_area = cita.areas_pendientes[0]
        areas[siguiente_area].append(cita)
        cita.area_actual = siguiente_area
        cita.tiempos_por_area[siguiente_area] = {
            "ingreso": datetime.now(), "atencion": None, "espera_min": 0,
        }
    else:
        cita.area_actual = None
        cita.estado = Cita.ESTADO_ATENDIDA

    return {
        "paciente": cita.paciente.nombre,
        "cita_id": cita.id_cita,
        "empresa": cita.paciente.empresa,
        "area": area,
        "tiempo_espera": tiempo_espera,
        "siguiente_area": siguiente_area,
        "completado": cita.estado == Cita.ESTADO_ATENDIDA,
        "restantes_en_area": len(areas[area]),
        "areas_completadas": list(cita.areas_completadas),
        "areas_pendientes": list(cita.areas_pendientes),
    }


def cancelar_cita_en_flujo(cita):
    """Saca al paciente del flujo. Marca la cita como cancelada."""
    from models.cita import Cita
    _quitar_de_todas(cita)
    cita.area_actual = None
    cita.estado = Cita.ESTADO_CANCELADA


# ----- Helpers para reportes -----

def estado_areas():
    out = []
    for area, lista in areas.items():
        cantidad = len(lista)
        if cantidad > LIMITE:
            estado = "SATURADA"
        elif cantidad >= 3:
            estado = "EN OBSERVACIÓN"
        else:
            estado = "DISPONIBLE"
        out.append({"area": area, "cantidad": cantidad, "estado": estado,
                    "tiempo_estimado": cantidad * tiempos[area]})
    return out


def pacientes_en_area(area):
    return [c.paciente.nombre for c in areas.get(area, [])]


# =====================================================
# CLI (compatibilidad con menus/menu_principal.py)
# =====================================================

def menu_flujo_pacientes():
    while True:
        print("\n" + "=" * 50)
        print(" FLUJO DE PACIENTES ")
        print("=" * 50)
        print("1. Ver estado de áreas")
        print("2. Ver pacientes por área")
        print("3. Salir")

        opcion = input("\nSeleccione una opción: ").strip()
        if opcion == "1":
            for e in estado_areas():
                print(f" {e['area']}: {e['cantidad']} pacientes ({e['estado']}, ~{e['tiempo_estimado']} min)")
        elif opcion == "2":
            for area in areas:
                names = pacientes_en_area(area)
                print(f"\n[{area}]")
                for n in names or ["— Sin pacientes"]:
                    print(f" - {n}")
        elif opcion == "3":
            break
        else:
            print("Opción inválida.")
