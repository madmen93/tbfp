import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from datetime import date, timedelta, datetime

from models.paciente import Paciente
from models.cita import Cita
from models.emo import Emo
import services.gestion_citas as gestion_citas
import services.flujo_pacientes as flujo_pacientes
import services.kpi_operativo as kpi_operativo
from services.gestion_protocolos import (
    construir_protocolo, TIPO_A_OPCION, TIPOS_EXAMEN as PROTO_TIPOS_EXAMEN,
    RIESGOS_DISPONIBLES,
)
from utils.validaciones import (
    validar_dni, validar_solo_letras, validar_hora, validar_edad,
    validar_fecha, validar_nombre_completo, validar_texto_no_vacio,
)


# Paleta
COLOR_BG = "#f3f4f6"
COLOR_CARD = "#ffffff"
COLOR_BORDER = "#d1d5db"
COLOR_BORDER_FOCUS = "#2563eb"
COLOR_TEXT = "#111827"
COLOR_TEXT_MUTED = "#6b7280"
COLOR_PRIMARY = "#2563eb"
COLOR_PRIMARY_HOVER = "#1d4ed8"
COLOR_SECONDARY = "#e5e7eb"
COLOR_DANGER = "#ef4444"
COLOR_SUCCESS = "#10b981"
COLOR_WARNING = "#f59e0b"

SEXOS = ["Masculino", "Femenino"]
TIPOS_EXAMEN = PROTO_TIPOS_EXAMEN  # Ingreso / Anual / Salida / Alto Riesgo (unificado con protocolo)
PERFILES = ["Administrativo", "Operativo", "Mina", "Alto riesgo"]
AREAS = list(flujo_pacientes.areas.keys())


# ============================================================
# Widgets utilitarios
# ============================================================

class LabeledEntry(tk.Frame):
    """Entry con label arriba, mensaje de error inline y validación reactiva."""

    def __init__(self, parent, label, validator=None, error_msg="Valor inválido",
                 placeholder="", required=True, only_digits=False, only_letters=False,
                 max_length=None, **kwargs):
        super().__init__(parent, bg=COLOR_CARD)
        self.validator = validator
        self.error_msg = error_msg
        self.required = required
        self.only_digits = only_digits
        self.only_letters = only_letters
        self.max_length = max_length
        self._valid = False

        self.label = tk.Label(self, text=label, bg=COLOR_CARD, fg=COLOR_TEXT,
                              font=("Segoe UI", 9, "bold"), anchor="w")
        self.label.pack(fill="x", pady=(0, 3))

        self.entry_frame = tk.Frame(self, bg=COLOR_BORDER, highlightthickness=0)
        self.entry_frame.pack(fill="x")
        self.entry = tk.Entry(self.entry_frame, bd=0, relief="flat",
                              font=("Segoe UI", 10), bg=COLOR_CARD,
                              fg=COLOR_TEXT, insertbackground=COLOR_TEXT)
        self.entry.pack(fill="x", padx=8, pady=6)

        if placeholder:
            self._placeholder = placeholder
            self._set_placeholder()
            self.entry.bind("<FocusIn>", self._on_focus_in_ph)
            self.entry.bind("<FocusOut>", self._on_focus_out_ph)
        else:
            self._placeholder = None

        self.entry.bind("<KeyRelease>", self._on_change)
        self.entry.bind("<FocusOut>", self._on_blur, add="+")
        self.entry.bind("<FocusIn>", self._on_focus, add="+")

        if only_digits or only_letters or max_length:
            vcmd = (self.register(self._validate_input), "%P")
            self.entry.configure(validate="key", validatecommand=vcmd)

        self.error_label = tk.Label(self, text="", bg=COLOR_CARD,
                                    fg=COLOR_DANGER, font=("Segoe UI", 8), anchor="w")
        self.error_label.pack(fill="x", pady=(2, 0))

    def _validate_input(self, value):
        if self.max_length and len(value) > self.max_length:
            return False
        if self.only_digits and value and not value.isdigit():
            return False
        if self.only_letters and value and not value.replace(" ", "").isalpha():
            return False
        return True

    def _set_placeholder(self):
        self.entry.insert(0, self._placeholder)
        self.entry.configure(fg=COLOR_TEXT_MUTED)

    def _on_focus_in_ph(self, _e):
        if self.entry.get() == self._placeholder:
            self.entry.delete(0, "end")
            self.entry.configure(fg=COLOR_TEXT)

    def _on_focus_out_ph(self, _e):
        if not self.entry.get():
            self._set_placeholder()

    def _on_focus(self, _e):
        self.entry_frame.configure(bg=COLOR_BORDER_FOCUS)

    def _on_blur(self, _e):
        self.entry_frame.configure(bg=COLOR_BORDER if self._valid or not self.get() else COLOR_DANGER)
        self._on_change()

    def _on_change(self, _e=None):
        value = self.get()
        if not value:
            self._valid = not self.required
            self.error_label.config(text="" if self._valid else "Campo obligatorio")
            self.entry_frame.configure(bg=COLOR_BORDER if self._valid else COLOR_DANGER)
            return
        ok = True if self.validator is None else bool(self.validator(value))
        self._valid = ok
        self.error_label.config(text="" if ok else self.error_msg)
        self.entry_frame.configure(bg=COLOR_BORDER_FOCUS if self.entry.focus_get() == self.entry and ok
                                   else (COLOR_BORDER if ok else COLOR_DANGER))

    def get(self):
        v = self.entry.get()
        if self._placeholder and v == self._placeholder:
            return ""
        return v.strip()

    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)
        self.entry.configure(fg=COLOR_TEXT)
        self._on_change()

    def is_valid(self):
        self._on_change()
        return self._valid


class LabeledCombo(tk.Frame):
    def __init__(self, parent, label, values, default=None):
        super().__init__(parent, bg=COLOR_CARD)
        tk.Label(self, text=label, bg=COLOR_CARD, fg=COLOR_TEXT,
                 font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x", pady=(0, 3))
        self.var = tk.StringVar(value=default or values[0])
        self.combo = ttk.Combobox(self, textvariable=self.var, values=values,
                                  state="readonly", font=("Segoe UI", 10))
        self.combo.pack(fill="x", ipady=3)
        tk.Label(self, text="", bg=COLOR_CARD).pack(fill="x", pady=(2, 0))  # spacer

    def get(self):
        return self.var.get()

    def is_valid(self):
        return bool(self.var.get())


class LabeledSpinbox(tk.Frame):
    def __init__(self, parent, label, from_, to, default):
        super().__init__(parent, bg=COLOR_CARD)
        tk.Label(self, text=label, bg=COLOR_CARD, fg=COLOR_TEXT,
                 font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x", pady=(0, 3))
        self.var = tk.IntVar(value=default)
        self.spin = tk.Spinbox(self, from_=from_, to=to, textvariable=self.var,
                               font=("Segoe UI", 10), bd=1, relief="solid",
                               buttonbackground=COLOR_SECONDARY)
        self.spin.pack(fill="x", ipady=4)
        tk.Label(self, text="", bg=COLOR_CARD).pack(fill="x", pady=(2, 0))

    def get(self):
        try:
            return int(self.var.get())
        except (tk.TclError, ValueError):
            return None

    def is_valid(self):
        return self.get() is not None


def boton_primario(parent, text, command):
    b = tk.Button(parent, text=text, command=command, bg=COLOR_PRIMARY, fg="#ffffff",
                  font=("Segoe UI", 10, "bold"), bd=0, padx=18, pady=8,
                  activebackground=COLOR_PRIMARY_HOVER, activeforeground="#ffffff",
                  cursor="hand2", relief="flat")
    return b


def boton_secundario(parent, text, command):
    b = tk.Button(parent, text=text, command=command, bg=COLOR_SECONDARY, fg=COLOR_TEXT,
                  font=("Segoe UI", 10), bd=0, padx=16, pady=8,
                  activebackground="#d1d5db", cursor="hand2", relief="flat")
    return b


def boton_peligro(parent, text, command):
    b = tk.Button(parent, text=text, command=command, bg=COLOR_DANGER, fg="#ffffff",
                  font=("Segoe UI", 10, "bold"), bd=0, padx=16, pady=8,
                  activebackground="#dc2626", activeforeground="#ffffff",
                  cursor="hand2", relief="flat")
    return b


# ============================================================
# Toast
# ============================================================

def toast(parent, mensaje, tipo="info"):
    colores = {"info": COLOR_PRIMARY, "success": COLOR_SUCCESS,
               "error": COLOR_DANGER, "warn": COLOR_WARNING}
    color = colores.get(tipo, COLOR_PRIMARY)
    t = tk.Toplevel(parent)
    t.overrideredirect(True)
    t.configure(bg=color)
    t.attributes("-topmost", True)
    tk.Label(t, text=mensaje, bg=color, fg="#ffffff",
             font=("Segoe UI", 10, "bold"), padx=16, pady=10).pack()
    parent.update_idletasks()
    x = parent.winfo_rootx() + parent.winfo_width() - t.winfo_reqwidth() - 24
    y = parent.winfo_rooty() + 60
    t.geometry(f"+{x}+{y}")
    t.after(2400, t.destroy)


# ============================================================
# Grilla de horarios
# ============================================================

class GrillaHorarios(tk.Frame):
    """Muestra los horarios disponibles para una fecha, coloreados por ocupación."""

    def __init__(self, parent, on_select=None):
        super().__init__(parent, bg=COLOR_CARD)
        self.on_select = on_select
        self.fecha_actual = None
        self.hora_seleccionada = None
        self.botones = {}
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=COLOR_CARD)
        header.pack(fill="x", pady=(0, 6))
        tk.Label(header, text="Disponibilidad horaria", bg=COLOR_CARD, fg=COLOR_TEXT,
                 font=("Segoe UI", 9, "bold")).pack(side="left")

        leyenda = tk.Frame(header, bg=COLOR_CARD)
        leyenda.pack(side="right")
        for color, txt in [(COLOR_SUCCESS, "libre"), (COLOR_WARNING, "≥50%"), (COLOR_DANGER, "lleno")]:
            chip = tk.Frame(leyenda, bg=COLOR_CARD)
            chip.pack(side="left", padx=6)
            tk.Label(chip, text="●", fg=color, bg=COLOR_CARD,
                     font=("Segoe UI", 12)).pack(side="left")
            tk.Label(chip, text=txt, bg=COLOR_CARD, fg=COLOR_TEXT_MUTED,
                     font=("Segoe UI", 8)).pack(side="left", padx=(2, 0))

        self.grid_frame = tk.Frame(self, bg=COLOR_CARD)
        self.grid_frame.pack(fill="both", expand=True)

        cols = 6
        for i, hora in enumerate(gestion_citas.HORAS_DISPONIBLES):
            r, c = divmod(i, cols)
            cell = tk.Frame(self.grid_frame, bg=COLOR_CARD,
                            highlightbackground=COLOR_BORDER, highlightthickness=1,
                            cursor="hand2")
            cell.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
            self.grid_frame.grid_columnconfigure(c, weight=1, uniform="hora")

            hora_lbl = tk.Label(cell, text=hora, bg=COLOR_CARD, fg=COLOR_TEXT,
                                font=("Segoe UI", 10, "bold"))
            hora_lbl.pack(pady=(6, 0))
            estado_lbl = tk.Label(cell, text="—", bg=COLOR_CARD, fg=COLOR_TEXT_MUTED,
                                  font=("Segoe UI", 8))
            estado_lbl.pack(pady=(0, 6))

            for w in (cell, hora_lbl, estado_lbl):
                w.bind("<Button-1>", lambda _e, h=hora: self._click(h))

            self.botones[hora] = (cell, hora_lbl, estado_lbl)

    def actualizar(self, fecha):
        self.fecha_actual = fecha
        for hora, (cell, hora_lbl, estado_lbl) in self.botones.items():
            ocupadas = gestion_citas.contar_citas_horario(fecha, hora) if fecha else 0
            tope = gestion_citas.TOPE_POR_HORARIO
            pct = ocupadas / tope if tope else 0

            if ocupadas >= tope:
                color = COLOR_DANGER
                bg = "#fee2e2"
                fg = COLOR_DANGER
                cur = "X"
            elif pct >= 0.5:
                color = COLOR_WARNING
                bg = "#fef3c7"
                fg = "#92400e"
                cur = "hand2"
            else:
                color = COLOR_SUCCESS
                bg = "#dcfce7"
                fg = "#065f46"
                cur = "hand2"

            cell.configure(bg=bg, highlightbackground=color, cursor=cur)
            hora_lbl.configure(bg=bg, fg=fg)
            estado_lbl.configure(bg=bg, fg=fg, text=f"{ocupadas}/{tope}")

            if hora == self.hora_seleccionada and ocupadas < tope:
                cell.configure(highlightbackground=COLOR_PRIMARY, highlightthickness=2)

    def _click(self, hora):
        if self.fecha_actual is None:
            return
        ocupadas = gestion_citas.contar_citas_horario(self.fecha_actual, hora)
        if ocupadas >= gestion_citas.TOPE_POR_HORARIO:
            return
        self.hora_seleccionada = hora
        self.actualizar(self.fecha_actual)
        if self.on_select:
            self.on_select(hora)


# ============================================================
# Dialog: Cita
# ============================================================

class FormDialog(tk.Toplevel):
    def __init__(self, parent, title, width=560, height=700):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.transient(parent)
        self.configure(bg=COLOR_BG)
        self.result = None
        self.parent = parent
        self._center(width, height)
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self._build()
        self.update_idletasks()
        self.grab_set()
        self.focus_set()

    def _center(self, w, h):
        self.update_idletasks()
        pw = self.parent.winfo_rootx()
        ph = self.parent.winfo_rooty()
        pw_w = self.parent.winfo_width()
        pw_h = self.parent.winfo_height()
        x = pw + (pw_w - w) // 2
        y = ph + (pw_h - h) // 2
        self.geometry(f"{w}x{h}+{max(x,0)}+{max(y,0)}")

    def _build(self):
        raise NotImplementedError

    def _cancel(self):
        self.result = None
        self.destroy()


def _proximas_fechas(n=14):
    fechas = []
    today = date.today()
    for i in range(0, n + 1):
        d = today + timedelta(days=i)
        fechas.append(d.strftime("%d/%m/%Y"))
    return fechas


def _label_fecha_legible(f_str):
    try:
        d = datetime.strptime(f_str, "%d/%m/%Y").date()
        dias = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
        sufijo = " · HOY" if d == date.today() else ""
        return f"{f_str} ({dias[d.weekday()]}){sufijo}"
    except ValueError:
        return f_str


class CitaDialog(FormDialog):
    def __init__(self, parent, cita=None):
        self.cita_existente = cita
        title = "Editar cita" if cita else "Registrar cita"
        super().__init__(parent, title, width=700, height=720)

    def _build(self):
        wrapper = tk.Frame(self, bg=COLOR_BG)
        wrapper.pack(fill="both", expand=True, padx=20, pady=18)

        tk.Label(wrapper, text="Registrar cita" if not self.cita_existente else "Editar cita",
                 bg=COLOR_BG, fg=COLOR_TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(wrapper, text="Completa los campos. Los campos con borde rojo necesitan corrección.",
                 bg=COLOR_BG, fg=COLOR_TEXT_MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 12))

        # Footer con botones SIEMPRE visible (se packea antes para que quede fijo abajo)
        botones = tk.Frame(wrapper, bg=COLOR_BG)
        botones.pack(side="bottom", fill="x", pady=(10, 0))
        boton_secundario(botones, "Cancelar", self._cancel).pack(side="right", padx=(8, 0))
        self.btn_ok = boton_primario(botones, "Registrar cita" if not self.cita_existente else "Guardar",
                                     self._submit)
        self.btn_ok.pack(side="right")

        # Panel de error inline (arriba del footer, visible)
        self.error_panel = tk.Label(wrapper, text="", bg="#fee2e2", fg=COLOR_DANGER,
                                    font=("Segoe UI", 10, "bold"), anchor="w",
                                    padx=10, pady=6)
        # se packeará solo cuando haya un error

        # Área scrollable para el contenido
        card = tk.Frame(wrapper, bg=COLOR_CARD, highlightbackground=COLOR_BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True)

        self._scroll_canvas = tk.Canvas(card, bg=COLOR_CARD, highlightthickness=0)
        self._scroll_canvas.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(card, orient="vertical", command=self._scroll_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self._scroll_canvas.configure(yscrollcommand=scrollbar.set)

        inner = tk.Frame(self._scroll_canvas, bg=COLOR_CARD)
        self._inner_id = self._scroll_canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_inner_config(_e):
            self._scroll_canvas.configure(scrollregion=self._scroll_canvas.bbox("all"))

        def _on_canvas_config(e):
            self._scroll_canvas.itemconfigure(self._inner_id, width=e.width)

        inner.bind("<Configure>", _on_inner_config)
        self._scroll_canvas.bind("<Configure>", _on_canvas_config)

        def _on_mousewheel(e):
            self._scroll_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        self._scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.bind("<Destroy>", lambda _e: self._scroll_canvas.unbind_all("<MouseWheel>"))

        inner_padding = tk.Frame(inner, bg=COLOR_CARD)
        inner_padding.pack(fill="both", expand=True, padx=18, pady=14)
        inner = inner_padding

        tk.Label(inner, text="DATOS DEL PACIENTE", bg=COLOR_CARD, fg=COLOR_TEXT_MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")

        row1 = tk.Frame(inner, bg=COLOR_CARD)
        row1.pack(fill="x", pady=(6, 0))
        self.f_nombre = LabeledEntry(row1, "Nombre completo", validator=validar_nombre_completo,
                                     error_msg="Mínimo 3 palabras, solo letras",
                                     only_letters=True, max_length=80)
        self.f_nombre.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.f_dni = LabeledEntry(row1, "DNI (8 dígitos)", validator=validar_dni,
                                  error_msg="Debe tener exactamente 8 dígitos",
                                  only_digits=True, max_length=8)
        self.f_dni.pack(side="left", fill="x", expand=True)

        row2 = tk.Frame(inner, bg=COLOR_CARD)
        row2.pack(fill="x", pady=(8, 0))
        self.f_edad = LabeledSpinbox(row2, "Edad", 18, 99, 30)
        self.f_edad.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.f_sexo = LabeledCombo(row2, "Sexo", SEXOS, SEXOS[0])
        self.f_sexo.pack(side="left", fill="x", expand=True)

        self.f_empresa = LabeledEntry(inner, "Empresa / Razón social",
                                      validator=lambda v: validar_texto_no_vacio(v) and len(v) >= 2,
                                      error_msg="No puede estar vacío", max_length=60)
        self.f_empresa.pack(fill="x", pady=(8, 0))

        tk.Label(inner, text="EXAMEN", bg=COLOR_CARD, fg=COLOR_TEXT_MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(14, 0))
        row3 = tk.Frame(inner, bg=COLOR_CARD)
        row3.pack(fill="x", pady=(6, 0))
        self.f_tipo = LabeledCombo(row3, "Tipo de examen", TIPOS_EXAMEN, TIPOS_EXAMEN[0])
        self.f_tipo.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.f_perfil = LabeledCombo(row3, "Perfil", PERFILES, PERFILES[0])
        self.f_perfil.pack(side="left", fill="x", expand=True)
        self.f_tipo.combo.bind("<<ComboboxSelected>>", lambda _e: self._refresh_protocolo_preview())
        self.f_perfil.combo.bind("<<ComboboxSelected>>", lambda _e: self._on_perfil_change())

        # ---- Protocolo (mina + riesgos + preview) ----
        tk.Label(inner, text="PROTOCOLO", bg=COLOR_CARD, fg=COLOR_TEXT_MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(14, 0))

        proto_row = tk.Frame(inner, bg=COLOR_CARD)
        proto_row.pack(fill="x", pady=(6, 0))

        self.mina_var = tk.BooleanVar(value=False)
        tk.Checkbutton(proto_row, text="Personal de Mina", variable=self.mina_var,
                       bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 10),
                       activebackground=COLOR_CARD, selectcolor=COLOR_CARD,
                       command=self._refresh_protocolo_preview).pack(side="left")

        riesgos_label = tk.Label(inner, text="Riesgos asociados (opcional):",
                                 bg=COLOR_CARD, fg=COLOR_TEXT_MUTED,
                                 font=("Segoe UI", 9))
        riesgos_label.pack(anchor="w", pady=(6, 2))
        riesgos_grid = tk.Frame(inner, bg=COLOR_CARD)
        riesgos_grid.pack(fill="x")
        self.riesgos_vars = {}
        for i, r in enumerate(RIESGOS_DISPONIBLES):
            var = tk.BooleanVar(value=False)
            self.riesgos_vars[r] = var
            r_ix, c_ix = divmod(i, 2)
            tk.Checkbutton(riesgos_grid, text=r, variable=var, bg=COLOR_CARD, fg=COLOR_TEXT,
                           font=("Segoe UI", 9), activebackground=COLOR_CARD,
                           selectcolor=COLOR_CARD, anchor="w",
                           command=self._refresh_protocolo_preview).grid(
                row=r_ix, column=c_ix, sticky="w", padx=(0, 8))
            riesgos_grid.grid_columnconfigure(c_ix, weight=1)

        preview_card = tk.Frame(inner, bg="#f9fafb", highlightbackground=COLOR_BORDER, highlightthickness=1)
        preview_card.pack(fill="x", pady=(8, 0))
        self.preview_areas = tk.Label(preview_card, text="", bg="#f9fafb", fg=COLOR_TEXT,
                                       font=("Segoe UI", 9), anchor="w", justify="left",
                                       padx=10, pady=6)
        self.preview_areas.pack(fill="x")
        self.preview_total = tk.Label(preview_card, text="", bg="#f9fafb", fg=COLOR_PRIMARY,
                                       font=("Segoe UI", 10, "bold"), anchor="w",
                                       padx=10, pady=6)
        self.preview_total.pack(fill="x", pady=(0, 6))

        tk.Label(inner, text="PROGRAMACIÓN", bg=COLOR_CARD, fg=COLOR_TEXT_MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(14, 0))

        fecha_row = tk.Frame(inner, bg=COLOR_CARD)
        fecha_row.pack(fill="x", pady=(6, 0))
        tk.Label(fecha_row, text="Fecha", bg=COLOR_CARD, fg=COLOR_TEXT,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        fechas = _proximas_fechas(14)
        self.fecha_var = tk.StringVar(value=fechas[0])
        self.fecha_combo = ttk.Combobox(fecha_row, textvariable=self.fecha_var,
                                        values=[_label_fecha_legible(f) for f in fechas],
                                        state="readonly", font=("Segoe UI", 10))
        self.fecha_combo.current(0)
        self.fecha_combo.pack(fill="x", ipady=3)
        self.fecha_combo.bind("<<ComboboxSelected>>", self._on_fecha_change)
        self._fechas_raw = fechas

        self.fecha_info = tk.Label(fecha_row, text="", bg=COLOR_CARD, fg=COLOR_TEXT_MUTED,
                                   font=("Segoe UI", 8))
        self.fecha_info.pack(anchor="w", pady=(4, 0))

        grilla_holder = tk.Frame(inner, bg=COLOR_CARD)
        grilla_holder.pack(fill="x", pady=(10, 0))
        self.grilla = GrillaHorarios(grilla_holder, on_select=self._on_hora_select)
        self.grilla.pack(fill="x")

        # Si es edición, prellenar
        if self.cita_existente:
            c = self.cita_existente
            self.f_nombre.set(c.paciente.nombre)
            self.f_dni.set(c.paciente.id)
            try:
                self.f_edad.var.set(int(c.paciente.edad))
            except (TypeError, ValueError):
                pass
            if c.paciente.sexo in SEXOS:
                self.f_sexo.var.set(c.paciente.sexo)
            self.f_empresa.set(c.paciente.empresa)
            if c.emo.tipo in TIPOS_EXAMEN:
                self.f_tipo.var.set(c.emo.tipo)
            if c.emo.perfil in PERFILES:
                self.f_perfil.var.set(c.emo.perfil)
            if c.fecha not in self._fechas_raw:
                self.fecha_combo["values"] = [_label_fecha_legible(c.fecha)] + list(self.fecha_combo["values"])
                self._fechas_raw = [c.fecha] + self._fechas_raw
                self.fecha_combo.current(0)
            else:
                idx = self._fechas_raw.index(c.fecha)
                self.fecha_combo.current(idx)
            self.grilla.hora_seleccionada = c.hora

        if self.cita_existente:
            self.mina_var.set(bool(self.cita_existente.es_mina))
            for r in self.cita_existente.riesgos:
                if r in self.riesgos_vars:
                    self.riesgos_vars[r].set(True)

        self._refresh_fecha_info()
        self.grilla.actualizar(self._fechas_raw[self.fecha_combo.current()])
        self._refresh_protocolo_preview()

    def _on_fecha_change(self, _e=None):
        self._refresh_fecha_info()
        self.grilla.hora_seleccionada = None
        self.grilla.actualizar(self._fechas_raw[self.fecha_combo.current()])

    def _on_perfil_change(self):
        if self.f_perfil.get() == "Mina":
            self.mina_var.set(True)
        self._refresh_protocolo_preview()

    def _construir_protocolo_actual(self):
        tipo = self.f_tipo.get()
        opcion = TIPO_A_OPCION.get(tipo)
        if not opcion:
            return None
        riesgos = [r for r, v in self.riesgos_vars.items() if v.get()]
        try:
            return construir_protocolo(opcion, self.mina_var.get(), riesgos)
        except ValueError:
            return None

    def _refresh_protocolo_preview(self):
        proto = self._construir_protocolo_actual()
        if proto is None:
            self.preview_areas.config(text="Selecciona un tipo de examen válido.")
            self.preview_total.config(text="")
            return
        ruta = " → ".join(proto["areas"])
        n_exam = len(proto["items"])
        self.preview_areas.config(text=f"Ruta del paciente:  {ruta}\nExámenes incluidos: {n_exam}")
        self.preview_total.config(text=f"Total a pagar: S/ {proto['total']:.2f}")

    def _refresh_fecha_info(self):
        f = self._fechas_raw[self.fecha_combo.current()]
        total = gestion_citas.contar_citas_fecha(f)
        capacidad_total = gestion_citas.TOPE_POR_HORARIO * len(gestion_citas.HORAS_DISPONIBLES)
        self.fecha_info.config(
            text=f"  Citas ya programadas ese día: {total} / {capacidad_total}"
        )

    def _on_hora_select(self, _hora):
        pass

    def _mostrar_error(self, mensaje, campo=None):
        self.error_panel.config(text="  ⚠  " + mensaje)
        self.error_panel.pack(side="bottom", fill="x", pady=(0, 4), before=None)
        if campo is not None:
            try:
                campo.entry.focus_set()
            except AttributeError:
                pass

    def _limpiar_error(self):
        self.error_panel.config(text="")
        self.error_panel.pack_forget()

    def _submit(self):
        self._limpiar_error()

        if not self.f_nombre.is_valid():
            self._mostrar_error("Nombre inválido: escribe nombre y dos apellidos, solo letras.",
                                self.f_nombre)
            return
        if not self.f_dni.is_valid():
            self._mostrar_error("DNI inválido: debe tener exactamente 8 dígitos.", self.f_dni)
            return
        if not self.f_empresa.is_valid():
            self._mostrar_error("Empresa requerida.", self.f_empresa)
            return
        if self.grilla.hora_seleccionada is None:
            self._mostrar_error("Selecciona una hora en la grilla de horarios (clic en una celda verde).")
            return

        fecha = self._fechas_raw[self.fecha_combo.current()]
        hora = self.grilla.hora_seleccionada
        if not gestion_citas.validar_tope_atenciones(fecha, hora):
            self._mostrar_error(f"El horario {hora} del {fecha} ya está al tope.")
            return

        proto = self._construir_protocolo_actual()
        if proto is None:
            self._mostrar_error("Tipo de examen inválido para generar protocolo.")
            return

        riesgos = [r for r, v in self.riesgos_vars.items() if v.get()]

        self.result = {
            "nombre": self.f_nombre.get().upper(),
            "dni": self.f_dni.get(),
            "edad": self.f_edad.get(),
            "sexo": self.f_sexo.get(),
            "empresa": self.f_empresa.get().upper(),
            "tipo": self.f_tipo.get(),
            "perfil": self.f_perfil.get(),
            "fecha": fecha,
            "hora": hora,
            "es_mina": self.mina_var.get(),
            "riesgos": riesgos,
            "protocolo": proto,
        }
        self.destroy()


# ============================================================
# Dialog: Iniciar flujo desde una cita programada
# ============================================================

class IniciarFlujoDialog(FormDialog):
    """Selecciona una cita 'Programada' para enviarla al flujo de atención."""

    def __init__(self, parent, cita_preseleccionada=None):
        self.cita_preseleccionada = cita_preseleccionada
        super().__init__(parent, "Iniciar atención de cita", width=620, height=520)

    def _build(self):
        wrapper = tk.Frame(self, bg=COLOR_BG)
        wrapper.pack(fill="both", expand=True, padx=20, pady=18)

        tk.Label(wrapper, text="Iniciar atención", bg=COLOR_BG, fg=COLOR_TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(wrapper,
                 text="Selecciona una cita programada para enviarla al flujo. El paciente "
                      "comenzará por la primera área de su protocolo.",
                 bg=COLOR_BG, fg=COLOR_TEXT_MUTED, font=("Segoe UI", 9),
                 wraplength=560, justify="left").pack(anchor="w", pady=(2, 12))

        card = tk.Frame(wrapper, bg=COLOR_CARD, highlightbackground=COLOR_BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True)

        cols = ("ID", "Paciente", "Empresa", "Hora", "Tipo", "Ruta")
        widths = (70, 180, 140, 60, 90, 220)
        self.tree = ttk.Treeview(card, columns=cols, show="headings", height=8, selectmode="browse")
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
        sb = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        sb.pack(side="left", fill="y", pady=6)
        self.tree.configure(yscrollcommand=sb.set)

        self._citas_visibles = []
        self._recargar()

        hint = tk.Label(wrapper, text="Se muestran las citas en estado 'Programada' para hoy y días siguientes.",
                        bg=COLOR_BG, fg=COLOR_TEXT_MUTED, font=("Segoe UI", 8))
        hint.pack(anchor="w", pady=(8, 0))

        botones = tk.Frame(wrapper, bg=COLOR_BG)
        botones.pack(fill="x", pady=(10, 0))
        boton_secundario(botones, "Cancelar", self._cancel).pack(side="right", padx=(8, 0))
        boton_primario(botones, "Iniciar flujo", self._submit).pack(side="right")

    def _recargar(self):
        for it in self.tree.get_children():
            self.tree.delete(it)
        self._citas_visibles = []
        for c in gestion_citas.lista_citas:
            if c.estado != "Programada":
                continue
            ruta = " → ".join(c.protocolo.get("areas", [])) or "—"
            self.tree.insert("", "end", values=(
                c.id_cita, c.paciente.nombre, c.paciente.empresa,
                c.hora, c.emo.tipo, ruta,
            ))
            self._citas_visibles.append(c)
        if self.cita_preseleccionada in self._citas_visibles:
            idx = self._citas_visibles.index(self.cita_preseleccionada)
            children = self.tree.get_children()
            if idx < len(children):
                self.tree.selection_set(children[idx])
                self.tree.see(children[idx])

    def _submit(self):
        sel = self.tree.selection()
        if not sel:
            toast(self, "Selecciona una cita", "warn")
            return
        idx = self.tree.index(sel[0])
        if idx >= len(self._citas_visibles):
            return
        self.result = {"cita": self._citas_visibles[idx]}
        self.destroy()


# ============================================================
# Dialog: Atender paciente
# ============================================================

class AtenderDialog(FormDialog):
    """Selector visual de área + lista de pacientes en cola para escoger a quién atender."""

    def __init__(self, parent, area_sugerida=None):
        self.area_sugerida = area_sugerida
        self._area_buttons = {}
        self._area_actual = None
        super().__init__(parent, "Atender paciente", width=820, height=620)

    def _build(self):
        wrapper = tk.Frame(self, bg=COLOR_BG)
        wrapper.pack(fill="both", expand=True, padx=20, pady=18)

        tk.Label(wrapper, text="Atender paciente", bg=COLOR_BG, fg=COLOR_TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(wrapper,
                 text="1) Elige el área   ·   2) Selecciona el paciente   ·   3) Pulsa Atender.",
                 bg=COLOR_BG, fg=COLOR_TEXT_MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 12))

        # Footer fijo
        botones = tk.Frame(wrapper, bg=COLOR_BG)
        botones.pack(side="bottom", fill="x", pady=(10, 0))
        boton_secundario(botones, "Cancelar", self._cancel).pack(side="right", padx=(8, 0))
        boton_primario(botones, "Atender seleccionado", self._submit).pack(side="right")

        self.error_panel = tk.Label(wrapper, text="", bg="#fee2e2", fg=COLOR_DANGER,
                                    font=("Segoe UI", 10, "bold"), anchor="w",
                                    padx=10, pady=6)

        # --- Selector de área (tarjetas horizontales) ---
        areas_card = tk.Frame(wrapper, bg=COLOR_CARD,
                              highlightbackground=COLOR_BORDER, highlightthickness=1)
        areas_card.pack(fill="x", pady=(0, 10))
        tk.Label(areas_card, text="Áreas", bg=COLOR_CARD, fg=COLOR_TEXT_MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=12, pady=(10, 4))

        areas_row = tk.Frame(areas_card, bg=COLOR_CARD)
        areas_row.pack(fill="x", padx=12, pady=(0, 12))

        for i, a in enumerate(AREAS):
            btn = self._construir_card_area(areas_row, a)
            btn.grid(row=0, column=i, sticky="nsew", padx=4)
            areas_row.grid_columnconfigure(i, weight=1, uniform="areas")

        # --- Lista de pacientes en cola del área ---
        lista_card = tk.Frame(wrapper, bg=COLOR_CARD,
                              highlightbackground=COLOR_BORDER, highlightthickness=1)
        lista_card.pack(fill="both", expand=True)
        header_lista = tk.Frame(lista_card, bg=COLOR_CARD)
        header_lista.pack(fill="x", padx=12, pady=(10, 4))
        self.titulo_lista = tk.Label(header_lista, text="Cola: —", bg=COLOR_CARD, fg=COLOR_TEXT,
                                     font=("Segoe UI", 11, "bold"))
        self.titulo_lista.pack(side="left")

        tree_holder = tk.Frame(lista_card, bg=COLOR_CARD)
        tree_holder.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        cols = ("#", "Cita", "Paciente", "Empresa", "Tipo", "Pendientes")
        widths = (40, 60, 200, 160, 90, 200)
        self.tree = ttk.Treeview(tree_holder, columns=cols, show="headings",
                                 selectmode="browse", height=10)
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="w")
        self.tree.column("#", anchor="center")
        self.tree.column("Cita", anchor="center")
        self.tree.column("Tipo", anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(tree_holder, orient="vertical", command=self.tree.yview)
        sb.pack(side="left", fill="y")
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind("<Double-1>", lambda _e: self._submit())

        # Cargar área inicial
        default = self.area_sugerida if self.area_sugerida in AREAS else AREAS[0]
        self._seleccionar_area(default)

    def _construir_card_area(self, parent, area):
        lista = flujo_pacientes.areas[area]
        cantidad = len(lista)
        if cantidad > flujo_pacientes.LIMITE:
            color_estado = COLOR_DANGER
            bg_card = "#fee2e2"
        elif cantidad >= 3:
            color_estado = COLOR_WARNING
            bg_card = "#fef3c7"
        else:
            color_estado = COLOR_SUCCESS
            bg_card = "#dcfce7"

        cell = tk.Frame(parent, bg=bg_card,
                        highlightbackground=COLOR_BORDER, highlightthickness=1, cursor="hand2")
        nombre = tk.Label(cell, text=area, bg=bg_card, fg=COLOR_TEXT,
                          font=("Segoe UI", 10, "bold"))
        nombre.pack(pady=(8, 0), padx=8)
        conteo = tk.Label(cell, text=f"{cantidad} en cola",
                          bg=bg_card, fg=color_estado, font=("Segoe UI", 9, "bold"))
        conteo.pack(pady=(2, 8), padx=8)

        for w in (cell, nombre, conteo):
            w.bind("<Button-1>", lambda _e, a=area: self._seleccionar_area(a))

        self._area_buttons[area] = (cell, nombre, conteo, bg_card)
        return cell

    def _seleccionar_area(self, area):
        self._area_actual = area
        # Resaltar la tarjeta del área activa
        for a, (cell, nombre, conteo, bg_card) in self._area_buttons.items():
            if a == area:
                cell.configure(highlightbackground=COLOR_PRIMARY, highlightthickness=3)
            else:
                cell.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)

        # Llenar treeview con los pacientes de esa área
        for it in self.tree.get_children():
            self.tree.delete(it)

        lista = flujo_pacientes.areas[area]
        self.titulo_lista.config(text=f"Cola: {area}  ({len(lista)} paciente{'s' if len(lista) != 1 else ''})")

        if not lista:
            return
        for i, cita in enumerate(lista, 1):
            pendientes = " → ".join(cita.areas_pendientes) or "—"
            self.tree.insert("", "end", values=(
                i, cita.id_cita, cita.paciente.nombre, cita.paciente.empresa,
                cita.emo.tipo, pendientes,
            ))
        # Seleccionar el primero por defecto
        first = self.tree.get_children()
        if first:
            self.tree.selection_set(first[0])
            self.tree.focus(first[0])

    def _submit(self):
        if self._area_actual is None:
            self.error_panel.config(text="  ⚠  Selecciona un área.")
            self.error_panel.pack(side="bottom", fill="x", pady=(0, 4))
            return
        lista = flujo_pacientes.areas[self._area_actual]
        if not lista:
            self.error_panel.config(text=f"  ⚠  No hay pacientes en cola en {self._area_actual}.")
            self.error_panel.pack(side="bottom", fill="x", pady=(0, 4))
            return
        sel = self.tree.selection()
        if not sel:
            self.error_panel.config(text="  ⚠  Selecciona un paciente de la lista.")
            self.error_panel.pack(side="bottom", fill="x", pady=(0, 4))
            return
        idx = self.tree.index(sel[0])
        self.result = {"area": self._area_actual, "indice": idx}
        self.destroy()


# ============================================================
# Dialog: Protocolo
# ============================================================

PROTO_TIPOS = [
    ("1", "Examen de Ingreso"),
    ("2", "Examen Anual"),
    ("3", "Examen de Salida"),
    ("4", "Solo Trabajos de Alto Riesgo"),
]
RIESGOS_LISTA = [
    "Trabajo en altura (> 1.80m)",
    "Espacios confinados",
    "Manipulación de Químicos",
    "Operadores de maquinaria pesada",
    "Exposición a Radiaciones",
]


class ProtocoloDialog(FormDialog):
    def __init__(self, parent):
        super().__init__(parent, "Generar protocolo", width=560, height=620)

    def _build(self):
        wrapper = tk.Frame(self, bg=COLOR_BG)
        wrapper.pack(fill="both", expand=True, padx=20, pady=18)
        tk.Label(wrapper, text="Generar protocolo", bg=COLOR_BG, fg=COLOR_TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(wrapper, text="Configura el tipo de examen y los riesgos aplicables.",
                 bg=COLOR_BG, fg=COLOR_TEXT_MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 12))

        card = tk.Frame(wrapper, bg=COLOR_CARD, highlightbackground=COLOR_BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True)
        inner = tk.Frame(card, bg=COLOR_CARD)
        inner.pack(fill="both", expand=True, padx=18, pady=14)

        tk.Label(inner, text="Tipo de examen", bg=COLOR_CARD, fg=COLOR_TEXT,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.tipo_var = tk.StringVar(value=PROTO_TIPOS[0][0])
        for code, label in PROTO_TIPOS:
            tk.Radiobutton(inner, text=label, variable=self.tipo_var, value=code,
                           bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 10),
                           activebackground=COLOR_CARD, selectcolor=COLOR_CARD,
                           anchor="w", padx=4, pady=2).pack(fill="x")

        tk.Label(inner, text="¿Es para personal de Mina?", bg=COLOR_CARD, fg=COLOR_TEXT,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10, 0))
        self.mina_var = tk.BooleanVar(value=False)
        row = tk.Frame(inner, bg=COLOR_CARD)
        row.pack(fill="x")
        for txt, val in [("Sí", True), ("No", False)]:
            tk.Radiobutton(row, text=txt, variable=self.mina_var, value=val,
                           bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 10),
                           activebackground=COLOR_CARD, selectcolor=COLOR_CARD).pack(side="left", padx=8)

        tk.Label(inner, text="Riesgos asociados", bg=COLOR_CARD, fg=COLOR_TEXT,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10, 0))
        self.riesgos_vars = {}
        for r in RIESGOS_LISTA:
            var = tk.BooleanVar(value=False)
            self.riesgos_vars[r] = var
            tk.Checkbutton(inner, text=r, variable=var, bg=COLOR_CARD, fg=COLOR_TEXT,
                           font=("Segoe UI", 10), activebackground=COLOR_CARD,
                           selectcolor=COLOR_CARD, anchor="w").pack(fill="x")

        botones = tk.Frame(wrapper, bg=COLOR_BG)
        botones.pack(fill="x", pady=(14, 0))
        boton_secundario(botones, "Cancelar", self._cancel).pack(side="right", padx=(8, 0))
        boton_primario(botones, "Generar", self._submit).pack(side="right")

    def _submit(self):
        self.result = {
            "opcion": self.tipo_var.get(),
            "es_mina": self.mina_var.get(),
            "riesgos": [r for r, v in self.riesgos_vars.items() if v.get()],
        }
        self.destroy()


# ============================================================
# Confirm dialog (estilo propio en lugar de messagebox)
# ============================================================

class ConfirmDialog(FormDialog):
    def __init__(self, parent, title, mensaje, ok_text="Aceptar", peligro=False):
        self._mensaje = mensaje
        self._ok_text = ok_text
        self._peligro = peligro
        super().__init__(parent, title, width=420, height=200)

    def _build(self):
        wrapper = tk.Frame(self, bg=COLOR_BG)
        wrapper.pack(fill="both", expand=True, padx=20, pady=18)
        tk.Label(wrapper, text=self.title(), bg=COLOR_BG, fg=COLOR_TEXT,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(wrapper, text=self._mensaje, bg=COLOR_BG, fg=COLOR_TEXT,
                 font=("Segoe UI", 10), wraplength=380, justify="left").pack(anchor="w", pady=(8, 0))
        botones = tk.Frame(wrapper, bg=COLOR_BG)
        botones.pack(fill="x", pady=(20, 0))
        boton_secundario(botones, "Cancelar", self._cancel).pack(side="right", padx=(8, 0))
        if self._peligro:
            boton_peligro(botones, self._ok_text, self._ok).pack(side="right")
        else:
            boton_primario(botones, self._ok_text, self._ok).pack(side="right")

    def _ok(self):
        self.result = True
        self.destroy()


def confirmar(parent, title, mensaje, ok_text="Aceptar", peligro=False):
    d = ConfirmDialog(parent, title, mensaje, ok_text=ok_text, peligro=peligro)
    parent.wait_window(d)
    return bool(d.result)


def abrir_dialog(parent, dialog_cls, *args, **kwargs):
    d = dialog_cls(parent, *args, **kwargs)
    parent.wait_window(d)
    return d.result


# ============================================================
# Dialog: Exportar (selector de qué y a qué formato)
# ============================================================

class ExportarDialog(FormDialog):
    """Modal con una lista de opciones de exportación. Cada opción es (label, callback)."""

    def __init__(self, parent, titulo, opciones):
        self._titulo = titulo
        self._opciones = opciones
        super().__init__(parent, titulo, width=520, height=80 + 60 * len(opciones))

    def _build(self):
        wrapper = tk.Frame(self, bg=COLOR_BG)
        wrapper.pack(fill="both", expand=True, padx=20, pady=18)

        tk.Label(wrapper, text=self._titulo, bg=COLOR_BG, fg=COLOR_TEXT,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(wrapper,
                 text="Los archivos se guardarán en la carpeta 'exportaciones' del proyecto.",
                 bg=COLOR_BG, fg=COLOR_TEXT_MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 10))

        # Footer fijo
        footer = tk.Frame(wrapper, bg=COLOR_BG)
        footer.pack(side="bottom", fill="x", pady=(10, 0))
        boton_secundario(footer, "Cerrar", self._cancel).pack(side="right")

        self.error_panel = tk.Label(wrapper, text="", bg="#fee2e2", fg=COLOR_DANGER,
                                    font=("Segoe UI", 9), anchor="w", padx=10, pady=6)

        card = tk.Frame(wrapper, bg=COLOR_CARD,
                        highlightbackground=COLOR_BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True)

        inner = tk.Frame(card, bg=COLOR_CARD)
        inner.pack(fill="both", expand=True, padx=14, pady=12)

        for label, cb in self._opciones:
            color = COLOR_PRIMARY if "PDF" in label.upper() else COLOR_SUCCESS
            btn = tk.Button(inner, text=label, command=lambda c=cb: self._ejecutar(c),
                            bg=color, fg="#ffffff", bd=0, padx=14, pady=10,
                            font=("Segoe UI", 10, "bold"), cursor="hand2", relief="flat",
                            anchor="w")
            btn.pack(fill="x", pady=4)

    def _ejecutar(self, callback):
        self.error_panel.pack_forget()
        try:
            ruta = callback()
            if ruta is None:
                # Usuario canceló el filedialog; no cerramos el dialog
                return
            self.result = {"ruta": ruta}
            self.destroy()
        except Exception as e:
            self.error_panel.config(text=f"  ⚠  No se pudo exportar: {e}")
            self.error_panel.pack(side="bottom", fill="x", pady=(0, 4))
