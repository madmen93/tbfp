"""Vistas visuales del KPI: dashboard general y timeline por paciente."""
import tkinter as tk
from tkinter import ttk

import services.flujo_pacientes as flujo
import services.gestion_citas as citas_mod
from services import kpi_operativo


COLOR_BG = "#f3f4f6"
COLOR_CARD = "#ffffff"
COLOR_BORDER = "#e5e7eb"
COLOR_TEXT = "#111827"
COLOR_TEXT_MUTED = "#6b7280"
COLOR_PRIMARY = "#2563eb"
COLOR_SUCCESS = "#10b981"
COLOR_WARNING = "#f59e0b"
COLOR_DANGER = "#ef4444"


# Paleta para distinguir áreas en el timeline
COLOR_AREA = {
    "Triaje": "#3b82f6",
    "Laboratorio": "#8b5cf6",
    "Audiometría": "#ec4899",
    "Rayos X": "#f59e0b",
    "Medicina Ocupacional": "#10b981",
}


# ============================================================
# Dashboard general
# ============================================================

def mostrar_dashboard_general(parent):
    win = tk.Toplevel(parent)
    win.title("Dashboard KPI - Análisis general")
    win.geometry("900x640")
    win.configure(bg=COLOR_BG)

    contenedor = tk.Frame(win, bg=COLOR_BG)
    contenedor.pack(fill="both", expand=True, padx=18, pady=14)

    tk.Label(contenedor, text="Análisis general del flujo", bg=COLOR_BG, fg=COLOR_TEXT,
             font=("Segoe UI", 18, "bold")).pack(anchor="w")
    tk.Label(contenedor, text="Indicadores macro del sistema en tiempo real.",
             bg=COLOR_BG, fg=COLOR_TEXT_MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 14))

    k = kpi_operativo.calcular_kpi()

    # === Tarjetas resumen (4 columnas) ===
    cards_frame = tk.Frame(contenedor, bg=COLOR_BG)
    cards_frame.pack(fill="x")

    tarjetas = [
        ("CITAS TOTAL", k["total_citas"], COLOR_PRIMARY, "registradas"),
        ("EN FLUJO", k["citas_en_flujo"], COLOR_WARNING, "actualmente en cola"),
        ("ATENDIDAS", k["citas_atendidas"], COLOR_SUCCESS, "EMOs completadas"),
        ("ERRORES", k["total_errores"], COLOR_DANGER, "capturados"),
    ]
    for i, (titulo, valor, color, sub) in enumerate(tarjetas):
        _tarjeta(cards_frame, titulo, valor, color, sub).grid(row=0, column=i, sticky="nsew", padx=(0, 8) if i < 3 else 0)
        cards_frame.grid_columnconfigure(i, weight=1, uniform="cards")

    # === Tarjetas tiempos (3 columnas) ===
    cards2 = tk.Frame(contenedor, bg=COLOR_BG)
    cards2.pack(fill="x", pady=(10, 0))

    tarjetas2 = [
        ("ATENCIONES", k["total_atenciones"], COLOR_PRIMARY, "registradas"),
        ("PROMEDIO ESPERA", f"{k['promedio_espera_atendido']:.1f} min", COLOR_PRIMARY, "tiempo atendido"),
        ("ESPERA MÁXIMA", f"{k['max_espera_atendido']} min", COLOR_WARNING, "registrada"),
    ]
    for i, (titulo, valor, color, sub) in enumerate(tarjetas2):
        _tarjeta(cards2, titulo, valor, color, sub).grid(row=0, column=i, sticky="nsew", padx=(0, 8) if i < 2 else 0)
        cards2.grid_columnconfigure(i, weight=1, uniform="cards2")

    # === Saturación por área ===
    saturacion_card = tk.Frame(contenedor, bg=COLOR_CARD,
                               highlightbackground=COLOR_BORDER, highlightthickness=1)
    saturacion_card.pack(fill="both", expand=True, pady=(14, 0))

    tk.Label(saturacion_card, text="Saturación de áreas",
             bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 12, "bold"),
             anchor="w").pack(fill="x", padx=18, pady=(14, 4))
    tk.Label(saturacion_card,
             text=f"Capacidad por área: {flujo.LIMITE} pacientes. Barra completa = área en su tope.",
             bg=COLOR_CARD, fg=COLOR_TEXT_MUTED, font=("Segoe UI", 9),
             anchor="w").pack(fill="x", padx=18, pady=(0, 10))

    barras = tk.Frame(saturacion_card, bg=COLOR_CARD)
    barras.pack(fill="both", expand=True, padx=18, pady=(0, 14))

    for i, (area, lista) in enumerate(flujo.areas.items()):
        cantidad = len(lista)
        pct = min(1.0, cantidad / flujo.LIMITE) if flujo.LIMITE else 0
        if cantidad > flujo.LIMITE:
            color = COLOR_DANGER
            estado = "SATURADA"
        elif cantidad >= 3:
            color = COLOR_WARNING
            estado = "EN OBSERVACIÓN"
        else:
            color = COLOR_SUCCESS
            estado = "DISPONIBLE"

        fila = tk.Frame(barras, bg=COLOR_CARD)
        fila.pack(fill="x", pady=4)
        tk.Label(fila, text=area, bg=COLOR_CARD, fg=COLOR_TEXT,
                 font=("Segoe UI", 10, "bold"), width=22, anchor="w").pack(side="left")

        bar_holder = tk.Frame(fila, bg="#f3f4f6", height=24, width=400)
        bar_holder.pack(side="left", fill="x", expand=True, padx=(0, 10))
        bar_holder.pack_propagate(False)

        # canvas para la barra (se redimensiona)
        c = tk.Canvas(bar_holder, bg="#f3f4f6", highlightthickness=0, height=24)
        c.pack(fill="both", expand=True)
        def _redibujar_barra(_e, canvas=c, pct=pct, color=color):
            canvas.delete("all")
            w = canvas.winfo_width()
            h = canvas.winfo_height()
            canvas.create_rectangle(0, 4, w, h - 4, fill="#e5e7eb", outline="")
            canvas.create_rectangle(0, 4, int(w * pct), h - 4, fill=color, outline="")
        c.bind("<Configure>", _redibujar_barra)

        tk.Label(fila, text=f"{cantidad}/{flujo.LIMITE}",
                 bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 10, "bold"),
                 width=8, anchor="e").pack(side="left")
        tk.Label(fila, text=estado, bg=COLOR_CARD, fg=color,
                 font=("Segoe UI", 9, "bold"), width=18, anchor="w").pack(side="left", padx=(8, 0))

    # === Pie con debilidades ===
    debs_card = tk.Frame(contenedor, bg=COLOR_CARD,
                         highlightbackground=COLOR_BORDER, highlightthickness=1)
    debs_card.pack(fill="x", pady=(14, 0))
    tk.Label(debs_card, text="Debilidades detectadas",
             bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 11, "bold"),
             anchor="w").pack(fill="x", padx=14, pady=(10, 4))
    for d in kpi_operativo.identificar_debilidades():
        tk.Label(debs_card, text=f"  •  {d}", bg=COLOR_CARD, fg=COLOR_TEXT,
                 font=("Segoe UI", 9), anchor="w", justify="left",
                 wraplength=820).pack(fill="x", padx=14)
    tk.Label(debs_card, text="", bg=COLOR_CARD).pack(pady=(0, 8))

    boton_cerrar = tk.Button(contenedor, text="Cerrar", command=win.destroy,
                             bg="#e5e7eb", fg=COLOR_TEXT, bd=0, padx=16, pady=6,
                             font=("Segoe UI", 10), cursor="hand2", relief="flat")
    boton_cerrar.pack(pady=(12, 0))

    return win


def _tarjeta(parent, titulo, valor, color, sub=""):
    card = tk.Frame(parent, bg=COLOR_CARD,
                    highlightbackground=COLOR_BORDER, highlightthickness=1)
    tk.Label(card, text=titulo, bg=COLOR_CARD, fg=COLOR_TEXT_MUTED,
             font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=14, pady=(12, 0))
    tk.Label(card, text=str(valor), bg=COLOR_CARD, fg=color,
             font=("Segoe UI", 26, "bold")).pack(anchor="w", padx=14)
    if sub:
        tk.Label(card, text=sub, bg=COLOR_CARD, fg=COLOR_TEXT_MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=14, pady=(0, 12))
    return card


# ============================================================
# Timeline por paciente
# ============================================================

def mostrar_timeline_paciente(parent, cita):
    win = tk.Toplevel(parent)
    win.title(f"Timeline - {cita.paciente.nombre} ({cita.id_cita})")
    win.geometry("860x520")
    win.configure(bg=COLOR_BG)

    contenedor = tk.Frame(win, bg=COLOR_BG)
    contenedor.pack(fill="both", expand=True, padx=18, pady=14)

    # Cabecera con datos del paciente
    tk.Label(contenedor, text=cita.paciente.nombre, bg=COLOR_BG, fg=COLOR_TEXT,
             font=("Segoe UI", 16, "bold")).pack(anchor="w")
    tk.Label(contenedor,
             text=f"Cita {cita.id_cita}  ·  {cita.paciente.empresa}  ·  "
                  f"{cita.emo.tipo} ({cita.emo.perfil})  ·  Estado: {cita.estado}",
             bg=COLOR_BG, fg=COLOR_TEXT_MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 12))

    # Tarjeta principal: el timeline
    card = tk.Frame(contenedor, bg=COLOR_CARD,
                    highlightbackground=COLOR_BORDER, highlightthickness=1)
    card.pack(fill="both", expand=True)

    tk.Label(card, text="Recorrido por áreas",
             bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 11, "bold"),
             anchor="w").pack(fill="x", padx=18, pady=(14, 4))
    tk.Label(card,
             text="Cada barra representa el tiempo del paciente en esa área (min).",
             bg=COLOR_CARD, fg=COLOR_TEXT_MUTED, font=("Segoe UI", 9),
             anchor="w").pack(fill="x", padx=18, pady=(0, 10))

    canvas = tk.Canvas(card, bg="white", highlightthickness=0, height=260)
    canvas.pack(fill="both", expand=True, padx=18, pady=(0, 10))

    pasos = []
    total_min = 0
    for area in cita.protocolo.get("areas", []):
        info = cita.tiempos_por_area.get(area, {})
        espera = info.get("espera_min", 0)
        completada = area in cita.areas_completadas
        en_curso = (area == cita.area_actual)
        pendiente = (area in cita.areas_pendientes and not en_curso)
        pasos.append({
            "area": area, "espera": espera,
            "completada": completada, "en_curso": en_curso, "pendiente": pendiente,
        })
        if completada:
            total_min += espera

    def _redibujar(_e=None):
        _dibujar_timeline(canvas, pasos)
    canvas.bind("<Configure>", _redibujar)
    win.after(50, _redibujar)

    # Resumen abajo
    resumen = tk.Frame(card, bg=COLOR_CARD)
    resumen.pack(fill="x", padx=18, pady=(0, 14))

    completadas_n = sum(1 for p in pasos if p["completada"])
    total_pasos = len(pasos)
    tk.Label(resumen,
             text=f"Áreas completadas: {completadas_n} de {total_pasos}",
             bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 10)).pack(side="left")
    tk.Label(resumen,
             text=f"Tiempo acumulado en instituto: {total_min} min",
             bg=COLOR_CARD, fg=COLOR_PRIMARY, font=("Segoe UI", 11, "bold")).pack(side="right")

    boton_cerrar = tk.Button(contenedor, text="Cerrar", command=win.destroy,
                             bg="#e5e7eb", fg=COLOR_TEXT, bd=0, padx=16, pady=6,
                             font=("Segoe UI", 10), cursor="hand2", relief="flat")
    boton_cerrar.pack(pady=(12, 0))

    return win


def _dibujar_timeline(canvas, pasos):
    canvas.delete("all")
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    if w < 50 or h < 50 or not pasos:
        if w >= 50 and h >= 50:
            canvas.create_text(w / 2, h / 2, text="Sin recorrido todavía", fill=COLOR_TEXT_MUTED,
                               font=("Segoe UI", 10))
        return

    margen_izq = 160
    margen_der = 30
    margen_sup = 20
    margen_inf = 20

    area_w = w - margen_izq - margen_der
    area_h = h - margen_sup - margen_inf

    n = len(pasos)
    if n == 0:
        return

    fila_h = area_h / n
    bar_h = min(28, fila_h - 8)

    # Calcular escala de tiempo en base al máximo
    max_min = max((p["espera"] for p in pasos), default=0) or 1

    # Eje base
    canvas.create_line(margen_izq, margen_sup, margen_izq, h - margen_inf,
                       fill="#9ca3af", width=1)

    for i, paso in enumerate(pasos):
        y_centro = margen_sup + fila_h * (i + 0.5)
        y0 = y_centro - bar_h / 2
        y1 = y_centro + bar_h / 2

        # Label del área
        canvas.create_text(margen_izq - 8, y_centro, text=paso["area"], anchor="e",
                           fill=COLOR_TEXT, font=("Segoe UI", 9, "bold"))

        # Estado
        if paso["completada"]:
            color = COLOR_AREA.get(paso["area"], COLOR_PRIMARY)
            etiqueta_estado = "✓"
        elif paso["en_curso"]:
            color = COLOR_WARNING
            etiqueta_estado = "actual"
        else:
            color = "#d1d5db"
            etiqueta_estado = "pendiente"

        ancho_barra = (paso["espera"] / max_min) * area_w if paso["espera"] else 4
        x0 = margen_izq
        x1 = margen_izq + max(ancho_barra, 6)

        canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

        # Texto dentro/derecha
        if paso["completada"]:
            txt = f"{paso['espera']} min"
            canvas.create_text(x1 + 8, y_centro, text=txt, anchor="w",
                               fill=COLOR_TEXT, font=("Segoe UI", 9, "bold"))
        else:
            canvas.create_text(x1 + 8, y_centro, text=etiqueta_estado, anchor="w",
                               fill=COLOR_TEXT_MUTED, font=("Segoe UI", 9, "italic"))
