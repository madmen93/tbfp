import tkinter as tk
from tkinter import ttk

from services import kpi_operativo


COLOR_BARRA = "#3a7bd5"
COLOR_BARRA_ALERTA = "#d9534f"
COLOR_LINEA = "#f0ad4e"
COLOR_EJE = "#444444"
COLOR_GRID = "#dddddd"
COLOR_TEXTO = "#222222"


def mostrar_diagrama_pareto(parent=None, titulo="Pareto - Tiempo de espera por área"):
    kpi = kpi_operativo.calcular_kpi()
    estimado = kpi["tiempo_estimado_por_area"]
    atendido = kpi["tiempo_atendido_por_area"]

    # Total = espera estimada en cola + espera real registrada en atenciones cerradas
    combinado = {a: estimado.get(a, 0) + atendido.get(a, 0) for a in set(list(estimado) + list(atendido))}
    datos = sorted(combinado.items(), key=lambda x: x[1], reverse=True)

    if parent is None:
        win = tk.Tk()
    else:
        win = tk.Toplevel(parent)
    win.title(titulo)
    win.geometry("780x540")
    win.minsize(700, 480)

    contenedor = ttk.Frame(win, padding=10)
    contenedor.pack(fill="both", expand=True)

    ttk.Label(contenedor, text=titulo, font=(None, 13, "bold")).pack(anchor="w")
    ttk.Label(
        contenedor,
        text="Barras: tiempo total por área (atendido + en cola). Línea: % acumulado.",
        foreground="#666",
    ).pack(anchor="w", pady=(0, 6))

    canvas = tk.Canvas(contenedor, bg="white", highlightthickness=1, highlightbackground="#cccccc")
    canvas.pack(fill="both", expand=True)

    debilidades = kpi_operativo.identificar_debilidades()
    panel = ttk.LabelFrame(contenedor, text="Debilidades detectadas", padding=6)
    panel.pack(fill="x", pady=(8, 0))
    for d in debilidades:
        ttk.Label(panel, text=f"• {d}", wraplength=720, justify="left").pack(anchor="w")

    ttk.Button(contenedor, text="Cerrar", command=win.destroy).pack(pady=(8, 0))

    def _redibujar(event=None):
        _dibujar_pareto(canvas, datos)

    canvas.bind("<Configure>", _redibujar)
    win.after(50, _redibujar)
    return win


def _dibujar_pareto(canvas, datos):
    canvas.delete("all")
    ancho = canvas.winfo_width()
    alto = canvas.winfo_height()
    if ancho < 50 or alto < 50:
        return

    margen_izq = 60
    margen_der = 60
    margen_sup = 30
    margen_inf = 60

    area_w = ancho - margen_izq - margen_der
    area_h = alto - margen_sup - margen_inf

    total = sum(v for _, v in datos)

    if total == 0:
        canvas.create_text(
            ancho / 2, alto / 2,
            text="Sin datos de cola: registre pacientes para visualizar el Pareto.",
            fill=COLOR_TEXTO, font=(None, 11),
        )
        return

    max_val = max(v for _, v in datos)

    canvas.create_line(margen_izq, margen_sup, margen_izq, alto - margen_inf, fill=COLOR_EJE, width=1)
    canvas.create_line(margen_izq, alto - margen_inf, ancho - margen_der, alto - margen_inf, fill=COLOR_EJE, width=1)
    canvas.create_line(ancho - margen_der, margen_sup, ancho - margen_der, alto - margen_inf, fill=COLOR_EJE, width=1)

    pasos = 5
    for i in range(pasos + 1):
        y = alto - margen_inf - (area_h * i / pasos)
        valor_izq = max_val * i / pasos
        valor_der = 100 * i / pasos
        canvas.create_line(margen_izq, y, ancho - margen_der, y, fill=COLOR_GRID, dash=(2, 3))
        canvas.create_text(margen_izq - 6, y, text=f"{valor_izq:.0f}", anchor="e", fill=COLOR_TEXTO, font=(None, 8))
        canvas.create_text(ancho - margen_der + 6, y, text=f"{valor_der:.0f}%", anchor="w", fill=COLOR_TEXTO, font=(None, 8))

    canvas.create_text(margen_izq - 6, margen_sup - 14, text="min", anchor="e", fill=COLOR_TEXTO, font=(None, 8, "italic"))
    canvas.create_text(ancho - margen_der + 6, margen_sup - 14, text="acum.", anchor="w", fill=COLOR_TEXTO, font=(None, 8, "italic"))

    n = len(datos)
    if n == 0:
        return
    ancho_barra = (area_w / n) * 0.65
    paso = area_w / n

    acumulado = 0
    puntos_linea = []

    for i, (area, valor) in enumerate(datos):
        cx = margen_izq + paso * (i + 0.5)
        x0 = cx - ancho_barra / 2
        x1 = cx + ancho_barra / 2
        altura = (valor / max_val) * area_h if max_val > 0 else 0
        y0 = alto - margen_inf - altura
        y1 = alto - margen_inf

        color = COLOR_BARRA_ALERTA if valor == max_val and valor > 0 else COLOR_BARRA
        canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
        canvas.create_text(cx, y0 - 8, text=f"{valor}", fill=COLOR_TEXTO, font=(None, 9, "bold"))

        etiqueta = area if len(area) <= 14 else area[:13] + "…"
        canvas.create_text(cx, alto - margen_inf + 14, text=etiqueta, fill=COLOR_TEXTO, font=(None, 9))

        acumulado += valor
        pct = (acumulado / total) * 100
        py = alto - margen_inf - (pct / 100) * area_h
        puntos_linea.append((cx, py, pct))

    if len(puntos_linea) >= 2:
        for i in range(len(puntos_linea) - 1):
            x1, y1, _ = puntos_linea[i]
            x2, y2, _ = puntos_linea[i + 1]
            canvas.create_line(x1, y1, x2, y2, fill=COLOR_LINEA, width=2)

    for cx, py, pct in puntos_linea:
        canvas.create_oval(cx - 3, py - 3, cx + 3, py + 3, fill=COLOR_LINEA, outline="")
        canvas.create_text(cx + 6, py - 8, text=f"{pct:.0f}%", fill=COLOR_LINEA, font=(None, 8, "bold"), anchor="w")

    y_80 = alto - margen_inf - 0.8 * area_h
    canvas.create_line(margen_izq, y_80, ancho - margen_der, y_80, fill=COLOR_LINEA, dash=(4, 3))
    canvas.create_text(ancho - margen_der - 4, y_80 - 6, text="80%", fill=COLOR_LINEA, font=(None, 8, "italic"), anchor="e")
