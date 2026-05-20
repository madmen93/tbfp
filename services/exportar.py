"""Exportar atenciones, KPI y timelines a CSV (Excel) y PDF (reportlab)."""
import csv
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak,
)

import services.flujo_pacientes as flujo
import services.gestion_citas as citas_mod
from services import kpi_operativo


CARPETA_EXPORT = "exportaciones"


def _timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _ruta(nombre, extension):
    os.makedirs(CARPETA_EXPORT, exist_ok=True)
    return os.path.join(CARPETA_EXPORT, f"{nombre}_{_timestamp()}.{extension}")


# ============================================================
# CSV (Excel)
# ============================================================

def exportar_atenciones_csv(ruta=None):
    if ruta is None:
        ruta = _ruta("atenciones", "csv")
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Hora", "Cita", "Paciente", "Empresa", "Tipo examen", "Área",
                    "Tiempo espera (min)", "EMO completada"])
        for a in kpi_operativo.atenciones:
            w.writerow([
                a["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                a.get("cita_id") or "—",
                a["paciente"],
                a.get("empresa") or "—",
                a.get("tipo_examen") or "—",
                a["area"],
                a["tiempo_espera"],
                "Sí" if a.get("completado") else "No",
            ])
    return ruta


def exportar_citas_csv(ruta=None):
    if ruta is None:
        ruta = _ruta("citas", "csv")
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["ID", "Paciente", "DNI", "Empresa", "Edad", "Sexo",
                    "Fecha", "Hora", "Tipo", "Perfil", "Mina", "Riesgos",
                    "Total S/", "Estado", "Ruta", "Áreas completadas"])
        for c in citas_mod.lista_citas:
            w.writerow([
                c.id_cita, c.paciente.nombre, c.paciente.id, c.paciente.empresa,
                c.paciente.edad, c.paciente.sexo,
                c.fecha, c.hora, c.emo.tipo, c.emo.perfil,
                "Sí" if c.es_mina else "No",
                ", ".join(c.riesgos) if c.riesgos else "",
                f"{c.total:.2f}", c.estado,
                " → ".join(c.protocolo.get("areas", [])),
                " → ".join(c.areas_completadas),
            ])
    return ruta


def exportar_kpi_csv(ruta=None):
    if ruta is None:
        ruta = _ruta("kpi_resumen", "csv")
    k = kpi_operativo.calcular_kpi()
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Indicador", "Valor"])
        w.writerow(["Citas totales", k["total_citas"]])
        w.writerow(["Citas programadas", k["citas_programadas"]])
        w.writerow(["Citas en flujo", k["citas_en_flujo"]])
        w.writerow(["Citas atendidas", k["citas_atendidas"]])
        w.writerow(["Atenciones registradas", k["total_atenciones"]])
        w.writerow(["Errores capturados", k["total_errores"]])
        w.writerow(["Promedio espera (min)", f"{k['promedio_espera_atendido']:.2f}"])
        w.writerow(["Espera máxima (min)", k["max_espera_atendido"]])
        w.writerow(["Área cuello de botella", k["area_cuello_botella"] or "—"])
        w.writerow([])
        w.writerow(["Área", "En cola", "Tiempo estimado (min)", "Tiempo atendido (min)"])
        for area in flujo.areas:
            w.writerow([
                area, len(flujo.areas[area]),
                k["tiempo_estimado_por_area"].get(area, 0),
                k["tiempo_atendido_por_area"].get(area, 0),
            ])
        w.writerow([])
        w.writerow(["Empresa", "Atenciones", "Tiempo total (min)"])
        for emp, datos in k["por_empresa"].items():
            w.writerow([emp, datos["atenciones"], datos["tiempo_total"]])
        w.writerow([])
        w.writerow(["Debilidades"])
        for d in kpi_operativo.identificar_debilidades():
            w.writerow([d])
    return ruta


# ============================================================
# PDF (reportlab)
# ============================================================

def _styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle(name="H1Custom", parent=s["Heading1"], fontSize=18, textColor=colors.HexColor("#111827"), spaceAfter=8))
    s.add(ParagraphStyle(name="Sub", parent=s["BodyText"], fontSize=9, textColor=colors.HexColor("#6b7280"), spaceAfter=12))
    s.add(ParagraphStyle(name="H2Custom", parent=s["Heading2"], fontSize=13, textColor=colors.HexColor("#111827"), spaceBefore=10, spaceAfter=6))
    s.add(ParagraphStyle(name="Body", parent=s["BodyText"], fontSize=9, textColor=colors.HexColor("#111827")))
    return s


def _table_style():
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
    ])


def _header(story, titulo, subtitulo=None):
    s = _styles()
    story.append(Paragraph("TBMedic — Salud Ocupacional", s["Sub"]))
    story.append(Paragraph(titulo, s["H1Custom"]))
    if subtitulo:
        story.append(Paragraph(subtitulo, s["Sub"]))
    story.append(Paragraph(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", s["Sub"]))


def exportar_kpi_pdf(ruta=None):
    if ruta is None:
        ruta = _ruta("kpi_resumen", "pdf")
    doc = SimpleDocTemplate(ruta, pagesize=A4, leftMargin=1.5 * cm,
                            rightMargin=1.5 * cm, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    s = _styles()
    story = []
    _header(story, "Reporte KPI operativo",
            "Indicadores macro del flujo de pacientes")

    k = kpi_operativo.calcular_kpi()

    # Resumen
    resumen = [
        ["Indicador", "Valor"],
        ["Citas totales", str(k["total_citas"])],
        ["Programadas", str(k["citas_programadas"])],
        ["En flujo", str(k["citas_en_flujo"])],
        ["Atendidas", str(k["citas_atendidas"])],
        ["Atenciones registradas", str(k["total_atenciones"])],
        ["Errores capturados", str(k["total_errores"])],
        ["Promedio espera (min)", f"{k['promedio_espera_atendido']:.2f}"],
        ["Espera máxima (min)", str(k["max_espera_atendido"])],
        ["Cuello de botella", k["area_cuello_botella"] or "—"],
    ]
    t = Table(resumen, colWidths=[7 * cm, 5 * cm])
    t.setStyle(_table_style())
    story.append(t)

    story.append(Paragraph("Carga por área", s["H2Custom"]))
    rows = [["Área", "En cola", "Tiempo estimado (min)", "Tiempo atendido (min)"]]
    for area in flujo.areas:
        rows.append([
            area, str(len(flujo.areas[area])),
            str(k["tiempo_estimado_por_area"].get(area, 0)),
            str(k["tiempo_atendido_por_area"].get(area, 0)),
        ])
    t = Table(rows, colWidths=[5 * cm, 2.5 * cm, 4.5 * cm, 4.5 * cm])
    t.setStyle(_table_style())
    story.append(t)

    if k["por_empresa"]:
        story.append(Paragraph("Por empresa", s["H2Custom"]))
        rows = [["Empresa", "Atenciones", "Tiempo total (min)"]]
        for emp, datos in k["por_empresa"].items():
            rows.append([emp, str(datos["atenciones"]), str(datos["tiempo_total"])])
        t = Table(rows, colWidths=[8 * cm, 4 * cm, 4.5 * cm])
        t.setStyle(_table_style())
        story.append(t)

    story.append(Paragraph("Debilidades detectadas", s["H2Custom"]))
    for d in kpi_operativo.identificar_debilidades():
        story.append(Paragraph(f"• {d}", s["Body"]))

    doc.build(story)
    return ruta


def exportar_atenciones_pdf(ruta=None):
    if ruta is None:
        ruta = _ruta("atenciones", "pdf")
    doc = SimpleDocTemplate(ruta, pagesize=landscape(A4),
                            leftMargin=1.2 * cm, rightMargin=1.2 * cm,
                            topMargin=1.2 * cm, bottomMargin=1.2 * cm)
    s = _styles()
    story = []
    _header(story, "Historial de atenciones",
            f"Total registradas: {len(kpi_operativo.atenciones)}")

    rows = [["Hora", "Cita", "Paciente", "Empresa", "Tipo", "Área",
             "Espera (min)", "Completada"]]
    for a in kpi_operativo.atenciones:
        rows.append([
            a["timestamp"].strftime("%H:%M:%S"),
            a.get("cita_id") or "—",
            a["paciente"],
            a.get("empresa") or "—",
            a.get("tipo_examen") or "—",
            a["area"],
            str(a["tiempo_espera"]),
            "Sí" if a.get("completado") else "No",
        ])
    if len(rows) == 1:
        rows.append(["—"] * 8)
    t = Table(rows, repeatRows=1,
              colWidths=[2.0 * cm, 1.6 * cm, 5.0 * cm, 4.0 * cm,
                         2.4 * cm, 4.0 * cm, 2.4 * cm, 2.4 * cm])
    t.setStyle(_table_style())
    story.append(t)
    doc.build(story)
    return ruta


def exportar_timeline_paciente_pdf(cita, ruta=None):
    if ruta is None:
        ruta = _ruta(f"timeline_{cita.id_cita}", "pdf")
    doc = SimpleDocTemplate(ruta, pagesize=A4, leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                            topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    s = _styles()
    story = []
    _header(story, f"Timeline del paciente — {cita.paciente.nombre}",
            f"Cita {cita.id_cita} · {cita.paciente.empresa} · {cita.emo.tipo} ({cita.emo.perfil}) · Estado: {cita.estado}")

    # Datos del paciente
    paciente_rows = [
        ["DNI", cita.paciente.id],
        ["Edad", str(cita.paciente.edad)],
        ["Sexo", cita.paciente.sexo],
        ["Empresa", cita.paciente.empresa],
        ["Fecha cita", f"{cita.fecha} {cita.hora}"],
        ["Mina", "Sí" if cita.es_mina else "No"],
        ["Riesgos", ", ".join(cita.riesgos) if cita.riesgos else "—"],
        ["Total a pagar", f"S/ {cita.total:.2f}"],
    ]
    t = Table(paciente_rows, colWidths=[4 * cm, 12 * cm])
    t.setStyle(_table_style())
    story.append(t)

    story.append(Paragraph("Recorrido por áreas", s["H2Custom"]))
    rows = [["#", "Área", "Estado", "Tiempo espera (min)", "Hora ingreso", "Hora atención"]]
    total = 0
    for i, area in enumerate(cita.protocolo.get("areas", []), 1):
        info = cita.tiempos_por_area.get(area, {})
        completada = area in cita.areas_completadas
        en_curso = area == cita.area_actual
        estado = "Completada" if completada else ("En curso" if en_curso else "Pendiente")
        espera = info.get("espera_min", 0)
        if completada:
            total += espera
        ingreso = info["ingreso"].strftime("%H:%M:%S") if info.get("ingreso") else "—"
        atencion = info["atencion"].strftime("%H:%M:%S") if info.get("atencion") else "—"
        rows.append([str(i), area, estado, str(espera) if completada else "—", ingreso, atencion])
    t = Table(rows, colWidths=[1 * cm, 5 * cm, 3 * cm, 3 * cm, 2.5 * cm, 2.5 * cm])
    t.setStyle(_table_style())
    story.append(t)

    story.append(Paragraph(f"Tiempo total registrado: <b>{total} min</b>", s["Body"]))
    doc.build(story)
    return ruta


def exportar_citas_pdf(ruta=None):
    if ruta is None:
        ruta = _ruta("citas", "pdf")
    doc = SimpleDocTemplate(ruta, pagesize=landscape(A4),
                            leftMargin=1.2 * cm, rightMargin=1.2 * cm,
                            topMargin=1.2 * cm, bottomMargin=1.2 * cm)
    s = _styles()
    story = []
    _header(story, "Listado de citas", f"Total: {len(citas_mod.lista_citas)}")

    rows = [["ID", "Paciente", "DNI", "Empresa", "Fecha", "Hora",
             "Tipo", "Total S/", "Estado"]]
    for c in citas_mod.lista_citas:
        rows.append([
            c.id_cita, c.paciente.nombre, c.paciente.id, c.paciente.empresa,
            c.fecha, c.hora, c.emo.tipo, f"{c.total:.2f}", c.estado,
        ])
    t = Table(rows, repeatRows=1,
              colWidths=[1.6 * cm, 5.2 * cm, 2.2 * cm, 4.0 * cm,
                         2.2 * cm, 1.6 * cm, 2.2 * cm, 1.8 * cm, 2.6 * cm])
    t.setStyle(_table_style())
    story.append(t)
    doc.build(story)
    return ruta
