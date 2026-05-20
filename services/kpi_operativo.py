from datetime import datetime

import services.flujo_pacientes as flujo
import services.gestion_citas as citas


UMBRAL_ESPERA_MIN = 30
UMBRAL_SATURACION_PCT = 80


atenciones = []
errores = []


def registrar_atencion(area, paciente, tiempo_espera_min, cita=None):
    atenciones.append({
        "area": area,
        "paciente": paciente,
        "tiempo_espera": tiempo_espera_min,
        "timestamp": datetime.now(),
        "cita_id": cita.id_cita if cita else None,
        "empresa": cita.paciente.empresa if cita else None,
        "tipo_examen": cita.emo.tipo if cita else None,
        "completado": (cita is not None and not cita.areas_pendientes),
    })


def registrar_error(origen, mensaje):
    errores.append({
        "origen": origen,
        "mensaje": mensaje,
        "timestamp": datetime.now(),
    })


def _tiempo_estimado_por_area():
    return {
        area: len(lista) * flujo.tiempos[area]
        for area, lista in flujo.areas.items()
    }


def _tiempo_atendido_por_area():
    acumulado = {area: 0 for area in flujo.areas}
    for evento in atenciones:
        acumulado[evento["area"]] = acumulado.get(evento["area"], 0) + evento["tiempo_espera"]
    return acumulado


def _atenciones_por_area():
    conteo = {area: 0 for area in flujo.areas}
    for evento in atenciones:
        conteo[evento["area"]] = conteo.get(evento["area"], 0) + 1
    return conteo


def _por_empresa():
    out = {}
    for evento in atenciones:
        emp = evento.get("empresa") or "— sin asignar"
        ref = out.setdefault(emp, {"atenciones": 0, "tiempo_total": 0})
        ref["atenciones"] += 1
        ref["tiempo_total"] += evento["tiempo_espera"]
    return out


def _examenes_completados():
    return sum(1 for c in citas.lista_citas if c.estado == "Atendida")


def calcular_kpi():
    estimado = _tiempo_estimado_por_area()
    atendido = _tiempo_atendido_por_area()
    conteo_at = _atenciones_por_area()

    total_pacientes_cola = sum(len(l) for l in flujo.areas.values())
    pacientes_unicos_cola = len({id(c) for lista in flujo.areas.values() for c in lista})
    total_atenciones = len(atenciones)
    total_citas = len(citas.lista_citas)
    citas_programadas = sum(1 for c in citas.lista_citas if c.estado == "Programada")
    citas_en_flujo = sum(1 for c in citas.lista_citas if c.estado == "En flujo")
    citas_atendidas = _examenes_completados()
    total_errores = len(errores)

    tiempo_total_cola = sum(estimado.values())
    promedio_cola = tiempo_total_cola / pacientes_unicos_cola if pacientes_unicos_cola else 0

    tiempos_at = [a["tiempo_espera"] for a in atenciones]
    promedio_atendido = sum(tiempos_at) / len(tiempos_at) if tiempos_at else 0
    max_atendido = max(tiempos_at) if tiempos_at else 0

    area_cuello = max(estimado, key=estimado.get) if estimado else None
    saturadas = [a for a, lista in flujo.areas.items() if len(lista) > flujo.LIMITE]

    return {
        "total_pacientes_cola": total_pacientes_cola,
        "pacientes_unicos_cola": pacientes_unicos_cola,
        "total_atenciones": total_atenciones,
        "total_citas": total_citas,
        "citas_programadas": citas_programadas,
        "citas_en_flujo": citas_en_flujo,
        "citas_atendidas": citas_atendidas,
        "total_errores": total_errores,
        "tiempo_total_cola": tiempo_total_cola,
        "promedio_espera_cola": promedio_cola,
        "promedio_espera_atendido": promedio_atendido,
        "max_espera_atendido": max_atendido,
        "area_cuello_botella": area_cuello,
        "areas_saturadas": saturadas,
        "tiempo_estimado_por_area": estimado,
        "tiempo_atendido_por_area": atendido,
        "atenciones_por_area": conteo_at,
        "por_empresa": _por_empresa(),
    }


def identificar_debilidades():
    kpi = calcular_kpi()
    debilidades = []

    for area in flujo.areas:
        ocupacion_pct = (len(flujo.areas[area]) / flujo.LIMITE) * 100 if flujo.LIMITE else 0
        if ocupacion_pct >= UMBRAL_SATURACION_PCT:
            debilidades.append(
                f"Área '{area}' al {ocupacion_pct:.0f}% de su capacidad ({len(flujo.areas[area])}/{flujo.LIMITE})."
            )

    if kpi["area_cuello_botella"] and kpi["tiempo_estimado_por_area"][kpi["area_cuello_botella"]] > 0:
        debilidades.append(
            f"Cuello de botella: '{kpi['area_cuello_botella']}' acumula "
            f"{kpi['tiempo_estimado_por_area'][kpi['area_cuello_botella']]} min estimados de espera."
        )

    if kpi["max_espera_atendido"] > UMBRAL_ESPERA_MIN:
        debilidades.append(
            f"Espera máxima registrada de {kpi['max_espera_atendido']} min supera el umbral de {UMBRAL_ESPERA_MIN} min."
        )

    if kpi["total_errores"] > 0:
        debilidades.append(f"{kpi['total_errores']} errores capturados durante la operación.")

    if kpi["citas_programadas"] > 0 and kpi["citas_atendidas"] == 0 and kpi["citas_en_flujo"] == 0:
        debilidades.append(
            f"{kpi['citas_programadas']} citas programadas sin iniciar flujo. "
            f"Considera iniciar la atención desde el módulo Citas."
        )

    estimado = kpi["tiempo_estimado_por_area"]
    if estimado:
        valores = list(estimado.values())
        if max(valores) > 0 and (max(valores) - min(valores)) / max(valores) >= 0.6:
            debilidades.append(
                "Desbalance de carga entre áreas (diferencia mayor al 60% entre la más y la menos cargada)."
            )

    if not debilidades:
        debilidades.append("Sin debilidades detectadas con los umbrales actuales.")

    return debilidades


def mostrar_kpi():
    k = calcular_kpi()
    debilidades = identificar_debilidades()

    lines = [
        "=========== KPI OPERATIVO ===========",
        f"Citas: {k['total_citas']}  ·  Programadas: {k['citas_programadas']}  ·  En flujo: {k['citas_en_flujo']}  ·  Atendidas: {k['citas_atendidas']}",
        f"Pacientes únicos en cola: {k['pacientes_unicos_cola']}",
        f"Atenciones registradas:   {k['total_atenciones']}",
        f"Errores capturados:       {k['total_errores']}",
        "",
        f"Tiempo total estimado en cola: {k['tiempo_total_cola']} min",
        f"Promedio espera (cola):        {k['promedio_espera_cola']:.2f} min",
        f"Promedio espera (atendidos):   {k['promedio_espera_atendido']:.2f} min",
        f"Espera máxima registrada:      {k['max_espera_atendido']} min",
        "",
        f"Área cuello de botella: {k['area_cuello_botella'] or '—'}",
        f"Áreas saturadas:        {', '.join(k['areas_saturadas']) if k['areas_saturadas'] else 'ninguna'}",
    ]

    if k["por_empresa"]:
        lines.append("")
        lines.append("Por empresa:")
        for emp, datos in k["por_empresa"].items():
            lines.append(f"  - {emp}: {datos['atenciones']} atenciones, {datos['tiempo_total']} min")

    lines.append("")
    lines.append("Debilidades detectadas:")
    lines.extend(f"  - {d}" for d in debilidades)
    lines.append("=====================================")
    return "\n".join(lines)


def reiniciar():
    atenciones.clear()
    errores.clear()
