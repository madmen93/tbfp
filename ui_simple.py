import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import font as tkfont
from datetime import datetime

from models.paciente import Paciente
from models.cita import Cita
from models.emo import Emo
import services.gestion_citas as gestion_citas
import services.flujo_pacientes as flujo_pacientes
import services.kpi_operativo as kpi_operativo
from services.gestion_protocolos import crear_protocolo, registrar_cotizacion, cotizaciones as cotizaciones_sueltas
from services.grafico_kpi import mostrar_diagrama_pareto
from services.dashboard_kpi import mostrar_dashboard_general, mostrar_timeline_paciente
from ui_dialogs import (
    CitaDialog, IniciarFlujoDialog, AtenderDialog, ProtocoloDialog,
    ExportarDialog, abrir_dialog, confirmar, toast,
)
import services.exportar as exportar_mod


# Paleta
COLOR_BG = "#f3f4f6"
COLOR_SIDEBAR = "#1f2937"
COLOR_SIDEBAR_ACCENT = "#111827"
COLOR_SIDEBAR_HOVER = "#374151"
COLOR_SIDEBAR_ACTIVE = "#2563eb"
COLOR_SIDEBAR_TEXT = "#e5e7eb"
COLOR_SIDEBAR_TITLE = "#ffffff"
COLOR_CARD = "#ffffff"
COLOR_BORDER = "#e5e7eb"
COLOR_TEXT = "#111827"
COLOR_TEXT_MUTED = "#6b7280"
COLOR_PRIMARY = "#2563eb"
COLOR_PRIMARY_HOVER = "#1d4ed8"
COLOR_SECONDARY = "#e5e7eb"
COLOR_DANGER = "#ef4444"
COLOR_SUCCESS = "#10b981"
COLOR_STATUSBAR = "#1f2937"


class TBMedicSimpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TBMedic")
        self.root.geometry("1080x680")
        self.root.minsize(960, 600)
        self.root.configure(bg=COLOR_BG)

        self.fuente_base = tkfont.Font(family="Segoe UI", size=10)
        self.fuente_titulo = tkfont.Font(family="Segoe UI", size=18, weight="bold")
        self.fuente_subtitulo = tkfont.Font(family="Segoe UI", size=10)
        self.fuente_nav = tkfont.Font(family="Segoe UI", size=11)
        self.fuente_logo = tkfont.Font(family="Segoe UI", size=16, weight="bold")
        self.fuente_mono = tkfont.Font(family="Consolas", size=10)

        self._configurar_estilos()

        self.nav_buttons = {}
        self.active_section = None

        self._build_sidebar()
        self._build_main()
        self._build_statusbar()

        self.show_citas_section()

    def _configurar_estilos(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".", background=COLOR_BG, foreground=COLOR_TEXT, font=self.fuente_base)

        style.configure("Card.TFrame", background=COLOR_CARD)
        style.configure("Bg.TFrame", background=COLOR_BG)
        style.configure("Header.TFrame", background=COLOR_BG)

        style.configure("Title.TLabel", background=COLOR_BG, foreground=COLOR_TEXT, font=self.fuente_titulo)
        style.configure("Subtitle.TLabel", background=COLOR_BG, foreground=COLOR_TEXT_MUTED, font=self.fuente_subtitulo)
        style.configure("Card.TLabel", background=COLOR_CARD, foreground=COLOR_TEXT, font=self.fuente_base)
        style.configure("CardTitle.TLabel", background=COLOR_CARD, foreground=COLOR_TEXT,
                        font=tkfont.Font(family="Segoe UI", size=11, weight="bold"))

        style.configure("Primary.TButton",
                        background=COLOR_PRIMARY, foreground="#ffffff",
                        font=self.fuente_base, borderwidth=0, padding=(14, 8))
        style.map("Primary.TButton",
                  background=[("active", COLOR_PRIMARY_HOVER), ("pressed", COLOR_PRIMARY_HOVER)],
                  foreground=[("disabled", "#9ca3af")])

        style.configure("Secondary.TButton",
                        background=COLOR_SECONDARY, foreground=COLOR_TEXT,
                        font=self.fuente_base, borderwidth=0, padding=(12, 7))
        style.map("Secondary.TButton",
                  background=[("active", "#d1d5db"), ("pressed", "#d1d5db")])

        style.configure("Danger.TButton",
                        background=COLOR_DANGER, foreground="#ffffff",
                        font=self.fuente_base, borderwidth=0, padding=(12, 7))
        style.map("Danger.TButton", background=[("active", "#dc2626")])

        style.configure("Treeview",
                        background=COLOR_CARD, fieldbackground=COLOR_CARD,
                        foreground=COLOR_TEXT, rowheight=26,
                        bordercolor=COLOR_BORDER, borderwidth=0, font=self.fuente_base)
        style.configure("Treeview.Heading",
                        background="#f9fafb", foreground=COLOR_TEXT_MUTED,
                        font=tkfont.Font(family="Segoe UI", size=9, weight="bold"),
                        relief="flat", borderwidth=0, padding=(8, 6))
        style.map("Treeview.Heading", background=[("active", "#f3f4f6")])
        style.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", COLOR_TEXT)])

        style.configure("Vertical.TScrollbar", background=COLOR_CARD, troughcolor=COLOR_BG,
                        bordercolor=COLOR_BG, arrowcolor=COLOR_TEXT_MUTED)

        style.configure("Status.TLabel", background=COLOR_STATUSBAR, foreground=COLOR_SIDEBAR_TEXT,
                        font=tkfont.Font(family="Segoe UI", size=9), padding=(10, 4))

    def _build_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg=COLOR_SIDEBAR, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_frame = tk.Frame(self.sidebar, bg=COLOR_SIDEBAR_ACCENT, height=70)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)
        tk.Label(logo_frame, text="TBMedic", bg=COLOR_SIDEBAR_ACCENT, fg=COLOR_SIDEBAR_TITLE,
                 font=self.fuente_logo).pack(side="left", padx=18, pady=18)

        items = [
            ("citas", "Citas", self.show_citas_section),
            ("protocolos", "Protocolos", self.show_protocolos_section),
            ("flujo", "Flujo de pacientes", self.show_flujo_section),
            ("kpi", "KPI / Monitoreo", self.show_kpi_section),
        ]
        nav_frame = tk.Frame(self.sidebar, bg=COLOR_SIDEBAR)
        nav_frame.pack(fill="both", expand=True, pady=(10, 0))

        for key, label, cmd in items:
            btn = tk.Label(nav_frame, text=f"   {label}", anchor="w",
                           bg=COLOR_SIDEBAR, fg=COLOR_SIDEBAR_TEXT,
                           font=self.fuente_nav, padx=18, pady=10, cursor="hand2")
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn, k=key: self._nav_hover(b, k, True))
            btn.bind("<Leave>", lambda e, b=btn, k=key: self._nav_hover(b, k, False))
            btn.bind("<Button-1>", lambda e, c=cmd: c())
            self.nav_buttons[key] = btn

        footer = tk.Label(self.sidebar, text="v1.0  ·  piloto",
                          bg=COLOR_SIDEBAR, fg=COLOR_TEXT_MUTED, font=("Segoe UI", 8))
        footer.pack(side="bottom", pady=10)

    def _nav_hover(self, btn, key, entering):
        if key == self.active_section:
            return
        btn.configure(bg=COLOR_SIDEBAR_HOVER if entering else COLOR_SIDEBAR)

    def _nav_set_active(self, key):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(bg=COLOR_SIDEBAR_ACTIVE, fg="#ffffff")
            else:
                btn.configure(bg=COLOR_SIDEBAR, fg=COLOR_SIDEBAR_TEXT)
        self.active_section = key

    def _build_main(self):
        self.main = tk.Frame(self.root, bg=COLOR_BG)
        self.main.pack(side="left", fill="both", expand=True)

        header = ttk.Frame(self.main, style="Header.TFrame", padding=(24, 18, 24, 8))
        header.pack(fill="x")
        self.section_title = ttk.Label(header, text="", style="Title.TLabel")
        self.section_title.pack(anchor="w")
        self.section_subtitle = ttk.Label(header, text="", style="Subtitle.TLabel")
        self.section_subtitle.pack(anchor="w", pady=(2, 0))

        self.action_bar = tk.Frame(self.main, bg=COLOR_BG)
        self.action_bar.pack(fill="x", padx=24, pady=(4, 12))

        content = tk.Frame(self.main, bg=COLOR_BG)
        content.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # Card izquierda (lista/treeview)
        self.list_card = tk.Frame(content, bg=COLOR_CARD, highlightbackground=COLOR_BORDER, highlightthickness=1)
        self.list_card.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self.list_card_header = tk.Frame(self.list_card, bg=COLOR_CARD)
        self.list_card_header.pack(fill="x", padx=14, pady=(12, 6))
        self.list_card_title = tk.Label(self.list_card_header, text="Listado",
                                        bg=COLOR_CARD, fg=COLOR_TEXT,
                                        font=("Segoe UI", 11, "bold"))
        self.list_card_title.pack(side="left")

        tree_holder = tk.Frame(self.list_card, bg=COLOR_CARD)
        tree_holder.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self.tree = ttk.Treeview(tree_holder, show="headings", selectmode="browse")
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree_scroll = ttk.Scrollbar(tree_holder, orient="vertical", command=self.tree.yview)
        self.tree_scroll.pack(side="left", fill="y")
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree.tag_configure("alt", background="#f9fafb")

        # Card derecha (detalle / output)
        self.detail_card = tk.Frame(content, bg=COLOR_CARD, highlightbackground=COLOR_BORDER, highlightthickness=1,
                                    width=380)
        self.detail_card.pack(side="left", fill="both")
        self.detail_card.pack_propagate(False)

        detail_header = tk.Frame(self.detail_card, bg=COLOR_CARD)
        detail_header.pack(fill="x", padx=14, pady=(12, 6))
        tk.Label(detail_header, text="Detalle", bg=COLOR_CARD, fg=COLOR_TEXT,
                 font=("Segoe UI", 11, "bold")).pack(side="left")

        self.output_text = tk.Text(self.detail_card, wrap="word", state="disabled",
                                   bg=COLOR_CARD, fg=COLOR_TEXT, relief="flat",
                                   highlightthickness=0, padx=14, pady=8,
                                   font=self.fuente_mono)
        self.output_text.pack(fill="both", expand=True, padx=4, pady=(0, 12))

    def _build_statusbar(self):
        self.statusbar = tk.Frame(self.root, bg=COLOR_STATUSBAR, height=26)
        self.statusbar.pack(side="bottom", fill="x")
        self.status_label = tk.Label(self.statusbar, text="Listo", bg=COLOR_STATUSBAR,
                                     fg=COLOR_SIDEBAR_TEXT, font=("Segoe UI", 9),
                                     padx=12)
        self.status_label.pack(side="left")
        self.counter_label = tk.Label(self.statusbar, text="", bg=COLOR_STATUSBAR,
                                      fg=COLOR_SIDEBAR_TEXT, font=("Segoe UI", 9),
                                      padx=12)
        self.counter_label.pack(side="right")
        self._refresh_statusbar()

    def _refresh_statusbar(self):
        en_cola = sum(len(l) for l in flujo_pacientes.areas.values())
        atendidos = len(kpi_operativo.atenciones)
        errores = len(kpi_operativo.errores)
        self.counter_label.config(
            text=f"Citas: {len(gestion_citas.lista_citas)}   ·   En cola: {en_cola}   ·   Atendidos: {atendidos}   ·   Errores: {errores}"
        )

    def _set_status(self, texto):
        self.status_label.config(text=texto)
        self._refresh_statusbar()

    # ---------------- Helpers ----------------

    def _clear_actions(self):
        for w in self.action_bar.winfo_children():
            w.destroy()

    def _add_action(self, label, command, style="Primary.TButton"):
        btn = ttk.Button(self.action_bar, text=label, command=command, style=style)
        btn.pack(side="left", padx=(0, 8))
        return btn

    def _set_tree_columns(self, columns, widths=None, anchors=None):
        self.tree.configure(columns=columns)
        for i, col in enumerate(columns):
            self.tree.heading(col, text=col)
            w = widths[i] if widths else 120
            a = anchors[i] if anchors else "w"
            self.tree.column(col, width=w, anchor=a, stretch=True)

    def _clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def _set_header(self, title, subtitle, list_title="Listado"):
        self.section_title.config(text=title)
        self.section_subtitle.config(text=subtitle)
        self.list_card_title.config(text=list_title)

    def show_message(self, text):
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", text)
        self.output_text.config(state="disabled")

    # ---------------- Citas ----------------

    def show_citas_section(self):
        self._nav_set_active("citas")
        self._set_header("Citas", "Cada cita lleva su protocolo. Inicia el flujo cuando el paciente llegue.",
                         list_title="Citas registradas")
        self._clear_actions()
        self._add_action("Registrar cita", self.add_cita, "Primary.TButton")
        self._add_action("Iniciar flujo", self.iniciar_flujo_desde_seleccion, "Primary.TButton")
        self._add_action("Editar", self.edit_cita, "Secondary.TButton")
        self._add_action("Eliminar", self.delete_cita, "Danger.TButton")
        self._add_action("Detalles", self.show_cita_details, "Secondary.TButton")
        self._add_action("Exportar", self.exportar_citas, "Secondary.TButton")
        self._add_action("Actualizar", self.update_appointments, "Secondary.TButton")

        self._set_tree_columns(
            ("ID", "Paciente", "Empresa", "Fecha", "Hora", "Tipo", "Total S/", "Estado"),
            widths=(60, 170, 130, 90, 60, 90, 70, 90),
            anchors=("w", "w", "w", "center", "center", "w", "e", "center"),
        )
        self.update_appointments()
        self.show_message("Selecciona una cita para ver el detalle del protocolo o iniciar su atención.")
        self._set_status("Sección Citas")

    def update_appointments(self):
        self._clear_tree()
        for i, cita in enumerate(gestion_citas.lista_citas):
            tag = ("alt",) if i % 2 else ()
            self.tree.insert("", "end", values=(
                cita.id_cita, cita.paciente.nombre, cita.paciente.empresa,
                cita.fecha, cita.hora, cita.emo.tipo,
                f"{cita.total:.2f}", cita.estado,
            ), tags=tag)
        self._refresh_statusbar()

    def get_selected_appointment(self):
        sel = self.tree.selection()
        if not sel:
            return None
        idx = self.tree.index(sel[0])
        if idx >= len(gestion_citas.lista_citas):
            return None
        return gestion_citas.lista_citas[idx]

    def add_cita(self):
        data = abrir_dialog(self.root, CitaDialog)
        if data is None:
            return

        cita = Cita(
            gestion_citas.generar_id_cita(),
            Paciente(data["nombre"], data["dni"], data["edad"], data["sexo"], data["empresa"]),
            data["fecha"], data["hora"],
            Emo(data["tipo"], data["perfil"]),
            es_mina=data["es_mina"],
            riesgos=data["riesgos"],
            protocolo=data["protocolo"],
        )
        gestion_citas.registrar_cita(cita)
        self.update_appointments()
        self.show_message(
            f"Cita {cita.id_cita} registrada.\n\n"
            f"Paciente:  {data['nombre']}\n"
            f"DNI:       {data['dni']}\n"
            f"Empresa:   {data['empresa']}\n"
            f"Tipo:      {data['tipo']} ({data['perfil']})\n"
            f"Fecha:     {data['fecha']}  Hora: {data['hora']}\n\n"
            + cita.texto_protocolo
        )
        toast(self.root, f"Cita {cita.id_cita} registrada", "success")
        self._set_status(f"Cita {cita.id_cita} registrada · Total S/ {cita.total:.2f}")

    def load_cita(self):
        cita = self.get_selected_appointment()
        if cita is None:
            toast(self.root, "Selecciona una cita primero", "warn")
            return
        ruta = " → ".join(cita.protocolo.get("areas", [])) or "—"
        completadas = " → ".join(cita.areas_completadas) or "—"
        pendientes = " → ".join(cita.areas_pendientes) or "—"
        info = (
            f"ID:        {cita.id_cita}\n"
            f"Paciente:  {cita.paciente.nombre}\n"
            f"Empresa:   {cita.paciente.empresa}\n"
            f"DNI:       {cita.paciente.id}\n"
            f"Edad:      {cita.paciente.edad}\n"
            f"Sexo:      {cita.paciente.sexo}\n"
            f"Fecha:     {cita.fecha}\n"
            f"Hora:      {cita.hora}\n"
            f"Tipo:      {cita.emo.tipo}\n"
            f"Perfil:    {cita.emo.perfil}\n"
            f"Mina:      {'Sí' if cita.es_mina else 'No'}\n"
            f"Riesgos:   {', '.join(cita.riesgos) if cita.riesgos else '—'}\n"
            f"Estado:    {cita.estado}\n"
            f"Ruta:      {ruta}\n"
            f"Completadas:  {completadas}\n"
            f"Pendientes:   {pendientes}\n"
            f"Área actual:  {cita.area_actual or '—'}\n\n"
            + cita.texto_protocolo
        )
        self.show_message(info)

    def show_cita_details(self):
        self.load_cita()

    def edit_cita(self):
        cita = self.get_selected_appointment()
        if cita is None:
            toast(self.root, "Selecciona una cita primero", "warn")
            return
        if cita.estado != "Programada":
            toast(self.root, f"Solo se editan citas en estado Programada (actual: {cita.estado})", "warn")
            return
        data = abrir_dialog(self.root, CitaDialog, cita=cita)
        if data is None:
            return
        cita.paciente.nombre = data["nombre"]
        cita.paciente.id = data["dni"]
        cita.paciente.edad = data["edad"]
        cita.paciente.sexo = data["sexo"]
        cita.paciente.empresa = data["empresa"]
        cita.emo.tipo = data["tipo"]
        cita.emo.perfil = data["perfil"]
        cita.fecha = data["fecha"]
        cita.hora = data["hora"]
        cita.es_mina = data["es_mina"]
        cita.riesgos = data["riesgos"]
        cita.protocolo = data["protocolo"]
        cita.areas_pendientes = list(data["protocolo"]["areas"])
        cita.areas_completadas = []
        cita.area_actual = None
        self.update_appointments()
        self.show_message(f"Cita {cita.id_cita} actualizada.\n\n" + cita.texto_protocolo)
        toast(self.root, f"Cita {cita.id_cita} actualizada", "success")
        self._set_status(f"Cita {cita.id_cita} editada")

    def iniciar_flujo_desde_seleccion(self):
        cita = self.get_selected_appointment()
        data = abrir_dialog(self.root, IniciarFlujoDialog, cita_preseleccionada=cita)
        if data is None:
            return
        c = data["cita"]
        primer_area = flujo_pacientes.iniciar_flujo_desde_cita(c)
        if primer_area is None:
            toast(self.root, f"No se pudo iniciar el flujo para {c.id_cita}", "error")
            return
        self.update_appointments()
        toast(self.root, f"{c.paciente.nombre} en cola de {primer_area}", "success")
        self.show_message(
            f"Cita {c.id_cita} en flujo.\n"
            f"Paciente: {c.paciente.nombre}\n"
            f"Primera área: {primer_area}\n"
            f"Ruta completa: {' → '.join(c.protocolo.get('areas', []))}"
        )
        self._set_status(f"Cita {c.id_cita} iniciada en {primer_area}")

    def delete_cita(self):
        cita = self.get_selected_appointment()
        if cita is None:
            toast(self.root, "Selecciona una cita primero", "warn")
            return
        if confirmar(self.root, "Eliminar cita",
                     f"¿Eliminar la cita {cita.id_cita} de {cita.paciente.nombre}?\n"
                     f"Si está en flujo, también se le retirará de las colas.",
                     ok_text="Eliminar", peligro=True):
            if cita.estado == "En flujo":
                flujo_pacientes.cancelar_cita_en_flujo(cita)
            gestion_citas.lista_citas.remove(cita)
            self.update_appointments()
            self.show_message(f"Cita {cita.id_cita} eliminada.")
            toast(self.root, f"Cita {cita.id_cita} eliminada", "success")
            self._set_status(f"Cita {cita.id_cita} eliminada")

    # ---------------- Protocolos ----------------

    def show_protocolos_section(self):
        self._nav_set_active("protocolos")
        self._proto_modo = getattr(self, "_proto_modo", "citas")
        subtitulo = ("Protocolos asignados a citas. Cambia a 'Cotizaciones' para ver presupuestos sueltos."
                     if self._proto_modo == "citas"
                     else "Cotizaciones sueltas guardadas. Puedes asignar una a una cita existente.")
        list_title = ("Protocolos de citas" if self._proto_modo == "citas"
                      else "Cotizaciones sueltas")
        self._set_header("Protocolos", subtitulo, list_title=list_title)
        self._clear_actions()
        self._add_action("Cotizar protocolo (sin cita)", self.generate_protocol, "Primary.TButton")
        self._add_action("Ver citas", lambda: self._switch_proto_modo("citas"), "Secondary.TButton")
        self._add_action("Ver cotizaciones",
                         lambda: self._switch_proto_modo("cotizaciones"), "Secondary.TButton")
        self._add_action("Ver detalle", self.show_protocolo_detail, "Secondary.TButton")
        if self._proto_modo == "cotizaciones":
            self._add_action("Asignar a cita", self.asignar_cotizacion_a_cita, "Primary.TButton")

        if self._proto_modo == "citas":
            self._set_tree_columns(("Cita", "Paciente", "Tipo", "Mina", "Riesgos", "Total S/", "Estado"),
                                   widths=(60, 170, 90, 60, 200, 80, 100),
                                   anchors=("w", "w", "w", "center", "w", "e", "center"))
            self._clear_tree()
            for i, c in enumerate(gestion_citas.lista_citas):
                tag = ("alt",) if i % 2 else ()
                self.tree.insert("", "end", values=(
                    c.id_cita, c.paciente.nombre, c.emo.tipo,
                    "Sí" if c.es_mina else "No",
                    ", ".join(c.riesgos) if c.riesgos else "—",
                    f"{c.total:.2f}", c.estado,
                ), tags=tag)
            self.show_message("Selecciona una fila y pulsa 'Ver detalle' para abrir el protocolo completo.")
        else:
            self._set_tree_columns(("ID", "Hora", "Tipo", "Mina", "Riesgos", "Total S/", "Asignada a"),
                                   widths=(80, 80, 90, 60, 220, 80, 110),
                                   anchors=("w", "center", "w", "center", "w", "e", "center"))
            self._clear_tree()
            for i, c in enumerate(cotizaciones_sueltas):
                tag = ("alt",) if i % 2 else ()
                hora = c["timestamp"].strftime("%H:%M:%S")
                riesgos = ", ".join(c.get("riesgos", [])) or "—"
                self.tree.insert("", "end", values=(
                    c["id"], hora, c.get("tipo", "—"),
                    "Sí" if c.get("es_mina") else "No",
                    riesgos, f"{c['total']:.2f}",
                    c.get("cita_asignada") or "—",
                ), tags=tag)
            self.show_message(
                "Cotizaciones guardadas en memoria.\n"
                "Selecciona una y pulsa 'Asignar a cita' para vincularla a una cita registrada."
                if cotizaciones_sueltas else
                "No hay cotizaciones guardadas todavía. Pulsa 'Cotizar protocolo (sin cita)' para generar una."
            )

        self._set_status(f"Sección Protocolos · vista: {self._proto_modo}")

    def _switch_proto_modo(self, modo):
        self._proto_modo = modo
        self.show_protocolos_section()

    def show_protocolo_detail(self):
        sel = self.tree.selection()
        if not sel:
            toast(self.root, "Selecciona un elemento", "warn")
            return
        idx = self.tree.index(sel[0])
        if self._proto_modo == "citas":
            if idx >= len(gestion_citas.lista_citas):
                return
            c = gestion_citas.lista_citas[idx]
            self.show_message(c.texto_protocolo or "Sin protocolo")
        else:
            if idx >= len(cotizaciones_sueltas):
                return
            cot = cotizaciones_sueltas[idx]
            extra = (f"\n\nID cotización: {cot['id']}\n"
                     f"Generada:      {cot['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                     f"Asignada a:    {cot.get('cita_asignada') or '— sin asignar'}")
            self.show_message(cot["texto"] + extra)

    def asignar_cotizacion_a_cita(self):
        sel = self.tree.selection()
        if not sel:
            toast(self.root, "Selecciona una cotización", "warn")
            return
        idx = self.tree.index(sel[0])
        if idx >= len(cotizaciones_sueltas):
            return
        cot = cotizaciones_sueltas[idx]

        citas_programadas = [c for c in gestion_citas.lista_citas if c.estado == "Programada"]
        if not citas_programadas:
            toast(self.root, "No hay citas en estado Programada", "warn")
            return

        opciones = "\n".join(f"  {i+1}. {c.id_cita} - {c.paciente.nombre}" for i, c in enumerate(citas_programadas))
        from tkinter import simpledialog
        eleccion = simpledialog.askinteger(
            "Asignar a cita",
            f"Citas disponibles:\n{opciones}\n\nNúmero a asignar:",
            parent=self.root, minvalue=1, maxvalue=len(citas_programadas),
        )
        if eleccion is None:
            return
        cita = citas_programadas[eleccion - 1]
        cita.protocolo = {k: v for k, v in cot.items() if k in ("items", "total", "areas", "es_mina", "riesgos", "texto")}
        cita.areas_pendientes = list(cita.protocolo.get("areas", []))
        cita.areas_completadas = []
        cita.es_mina = cot.get("es_mina", False)
        cita.riesgos = list(cot.get("riesgos", []))
        cot["cita_asignada"] = cita.id_cita
        toast(self.root, f"Cotización {cot['id']} asignada a {cita.id_cita}", "success")
        self.show_protocolos_section()

    def generate_protocol(self):
        data = abrir_dialog(self.root, ProtocoloDialog)
        if data is None:
            return
        try:
            cot = registrar_cotizacion(data["opcion"], data["es_mina"], data["riesgos"])
        except ValueError:
            kpi_operativo.registrar_error("protocolos", f"Opción inválida: {data['opcion']}")
            toast(self.root, "Opción inválida", "error")
            self._refresh_statusbar()
            return

        # Volver a la sección Protocolos en modo cotizaciones
        self._proto_modo = "cotizaciones"
        self.show_protocolos_section()
        self.show_message(
            cot["texto"]
            + f"\n\nID cotización: {cot['id']}\n"
            + f"Guardada en: Protocolos > Cotizaciones\n"
            + "Para asignarla a una cita usa el botón 'Asignar a cita'."
        )
        toast(self.root, f"Cotización {cot['id']} guardada", "success")
        self._set_status(f"Cotización {cot['id']} guardada")

    # ---------------- Flujo ----------------

    def show_flujo_section(self):
        self._nav_set_active("flujo")
        self._set_header("Flujo de pacientes",
                         "Las colas se alimentan desde citas. Atender mueve al paciente a la siguiente área de su protocolo.",
                         list_title="Estado por área")
        self._clear_actions()
        self._add_action("Iniciar flujo desde cita", self.iniciar_flujo_desde_seleccion, "Primary.TButton")
        self._add_action("Atender siguiente", self.atender_paciente, "Primary.TButton")
        self._add_action("Pacientes por área", self.show_patients_by_area, "Secondary.TButton")
        self._add_action("Estadísticas", self.show_flow_statistics, "Secondary.TButton")

        self._set_tree_columns(("Área", "En cola", "Capacidad", "Tiempo est. (min)", "Estado"),
                               widths=(180, 80, 90, 140, 140),
                               anchors=("w", "center", "center", "center", "center"))
        self._refresh_flujo_tree()
        self.show_message("Selecciona una fila para ver los pacientes en esa área.")
        self.tree.bind("<<TreeviewSelect>>", self._on_area_select)
        self._set_status("Sección Flujo")

    def _refresh_flujo_tree(self):
        self._clear_tree()
        for i, (area, lista) in enumerate(flujo_pacientes.areas.items()):
            cantidad = len(lista)
            estado = "SATURADA" if cantidad > flujo_pacientes.LIMITE else "OBSERVACIÓN" if cantidad >= 3 else "DISPONIBLE"
            tiempo_est = cantidad * flujo_pacientes.tiempos[area]
            tag = ("alt",) if i % 2 else ()
            self.tree.insert("", "end", values=(
                area, cantidad, flujo_pacientes.LIMITE, tiempo_est, estado,
            ), tags=tag)
        self._refresh_statusbar()

    def _on_area_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        area = self.tree.item(sel[0])["values"][0]
        if area not in flujo_pacientes.areas:
            return
        lista = flujo_pacientes.areas[area]
        lines = [f"Área: {area}", f"Pacientes en cola: {len(lista)}", ""]
        if lista:
            for i, cita in enumerate(lista, 1):
                pendientes = " → ".join(cita.areas_pendientes) or "—"
                lines.append(f" {i}. [{cita.id_cita}] {cita.paciente.nombre} ({cita.paciente.empresa})")
                lines.append(f"     Pendiente: {pendientes}")
        else:
            lines.append("Sin pacientes.")
        self.show_message("\n".join(lines))

    def atender_paciente(self):
        area_sugerida = None
        sel = self.tree.selection()
        if sel:
            val = self.tree.item(sel[0])["values"][0]
            if val in flujo_pacientes.areas:
                area_sugerida = val

        data = abrir_dialog(self.root, AtenderDialog, area_sugerida=area_sugerida)
        if data is None:
            return

        resultado = flujo_pacientes.atender_paciente(data["area"], indice=data.get("indice", 0))
        if resultado is None:
            toast(self.root, f"No hay pacientes en {data['area']}", "warn")
            self._refresh_statusbar()
            return

        self.update_appointments()
        self._refresh_flujo_tree()

        siguiente = resultado["siguiente_area"]
        if resultado["completado"]:
            estado_msg = f"EMO COMPLETADA. Cita {resultado['cita_id']} cerrada."
            toast(self.root, f"EMO completada: {resultado['paciente']}", "success")
        else:
            estado_msg = f"Avanza a: {siguiente}"
            toast(self.root, f"{resultado['paciente']} → {siguiente}", "success")

        msg = (
            f"Atención cerrada en {resultado['area']}\n"
            f"Cita:      {resultado['cita_id']}\n"
            f"Paciente:  {resultado['paciente']}\n"
            f"Empresa:   {resultado['empresa']}\n"
            f"Tiempo de espera: {resultado['tiempo_espera']} min\n"
            f"Completadas: {' → '.join(resultado['areas_completadas']) or '—'}\n"
            f"Pendientes:  {' → '.join(resultado['areas_pendientes']) or '—'}\n"
            f"{estado_msg}\n\n"
            + kpi_operativo.mostrar_kpi()
        )
        self.show_message(msg)
        self._set_status(f"Atendido {resultado['paciente']} en {resultado['area']}")

    def show_patients_by_area(self):
        lines = ["Pacientes por área:\n"]
        for area, lista in flujo_pacientes.areas.items():
            lines.append(f"[{area}] ({len(lista)})")
            if lista:
                for i, cita in enumerate(lista, 1):
                    lines.append(f"   {i}. [{cita.id_cita}] {cita.paciente.nombre} - {cita.paciente.empresa}")
            else:
                lines.append("   — Sin pacientes")
            lines.append("")
        self.show_message("\n".join(lines))

    def show_flow_statistics(self):
        total = sum(len(l) for l in flujo_pacientes.areas.values())
        mayor = max(flujo_pacientes.areas, key=lambda x: len(flujo_pacientes.areas[x]))
        self.show_message(
            f"Total de pacientes en cola: {total}\n"
            f"Área más concurrida:         {mayor}\n"
            f"Pacientes en esa área:       {len(flujo_pacientes.areas[mayor])}"
        )

    # ---------------- KPI ----------------

    def show_kpi_section(self):
        self._nav_set_active("kpi")
        self._kpi_modo = getattr(self, "_kpi_modo", "atenciones")
        subtitulo_map = {
            "atenciones": "Historial de atenciones cerradas en cada área.",
            "pacientes": "Selecciona un paciente para ver su timeline en el instituto.",
        }
        list_title_map = {
            "atenciones": "Atenciones registradas",
            "pacientes": "Pacientes (citas) con su recorrido",
        }
        self._set_header("KPI / Monitoreo",
                         subtitulo_map.get(self._kpi_modo, ""),
                         list_title=list_title_map.get(self._kpi_modo, "KPI"))
        self._clear_actions()
        self._add_action("Análisis general", self.show_dashboard, "Primary.TButton")
        if self._kpi_modo == "atenciones":
            self._add_action("Ver pacientes", lambda: self._switch_kpi_modo("pacientes"),
                             "Secondary.TButton")
        else:
            self._add_action("Ver atenciones", lambda: self._switch_kpi_modo("atenciones"),
                             "Secondary.TButton")
            self._add_action("Ver timeline", self.show_timeline_seleccionado, "Primary.TButton")
        self._add_action("Diagrama Pareto", self.show_pareto, "Secondary.TButton")
        self._add_action("Exportar", self.exportar_kpi, "Secondary.TButton")
        self._add_action("Ver errores", self.show_errores, "Secondary.TButton")
        self._add_action("Reiniciar", self.reset_kpi, "Danger.TButton")

        if self._kpi_modo == "atenciones":
            self._set_tree_columns(("Hora", "Área", "Paciente", "Empresa", "Espera (min)", "Cita"),
                                   widths=(80, 150, 200, 160, 100, 70),
                                   anchors=("center", "w", "w", "w", "center", "center"))
            self._refresh_kpi_tree()
        else:
            self._set_tree_columns(("Cita", "Paciente", "Empresa", "Estado",
                                    "Completadas", "Pendientes", "Tiempo (min)"),
                                   widths=(60, 180, 150, 90, 90, 90, 90),
                                   anchors=("center", "w", "w", "center", "center", "center", "center"))
            self._refresh_pacientes_tree()
        self.refresh_kpi()
        self._set_status(f"Sección KPI · vista: {self._kpi_modo}")

    def _switch_kpi_modo(self, modo):
        self._kpi_modo = modo
        self.show_kpi_section()

    def _refresh_kpi_tree(self):
        self._clear_tree()
        for i, a in enumerate(kpi_operativo.atenciones):
            tag = ("alt",) if i % 2 else ()
            self.tree.insert("", "end", values=(
                a["timestamp"].strftime("%H:%M:%S"),
                a["area"], a["paciente"],
                a.get("empresa") or "—",
                a["tiempo_espera"],
                a.get("cita_id") or "—",
            ), tags=tag)
        self._refresh_statusbar()

    def _refresh_pacientes_tree(self):
        self._clear_tree()
        # Solo citas con actividad en el flujo (En flujo o Atendida)
        pacientes_activos = [c for c in gestion_citas.lista_citas
                             if c.estado in ("En flujo", "Atendida")]
        self._pacientes_visibles = pacientes_activos
        for i, c in enumerate(pacientes_activos):
            tag = ("alt",) if i % 2 else ()
            t_total = sum(t.get("espera_min", 0) for t in c.tiempos_por_area.values())
            self.tree.insert("", "end", values=(
                c.id_cita, c.paciente.nombre, c.paciente.empresa, c.estado,
                len(c.areas_completadas), len(c.areas_pendientes),
                t_total,
            ), tags=tag)

    def show_timeline_seleccionado(self):
        sel = self.tree.selection()
        if not sel:
            toast(self.root, "Selecciona un paciente", "warn")
            return
        idx = self.tree.index(sel[0])
        pacientes = getattr(self, "_pacientes_visibles", [])
        if idx >= len(pacientes):
            return
        mostrar_timeline_paciente(self.root, pacientes[idx])

    def show_dashboard(self):
        mostrar_dashboard_general(self.root)

    def refresh_kpi(self):
        self.show_message(kpi_operativo.mostrar_kpi())

    def show_pareto(self):
        mostrar_diagrama_pareto(self.root)

    def show_errores(self):
        if not kpi_operativo.errores:
            self.show_message("Sin errores registrados.")
            return
        lines = ["Errores capturados:\n"]
        for e in kpi_operativo.errores:
            hora = e["timestamp"].strftime("%H:%M:%S")
            lines.append(f" [{hora}] ({e['origen']}) {e['mensaje']}")
        self.show_message("\n".join(lines))

    def reset_kpi(self):
        if confirmar(self.root, "Reiniciar monitoreo",
                     "¿Borrar atenciones y errores acumulados?",
                     ok_text="Reiniciar", peligro=True):
            kpi_operativo.reiniciar()
            self.refresh_kpi()
            toast(self.root, "Monitoreo reiniciado", "success")
            self._set_status("Monitoreo reiniciado")

    # ---------------- Exportación ----------------

    def _pedir_ruta(self, prefijo, extension, descripcion):
        """Abre el filedialog 'Guardar como' y devuelve la ruta elegida (o None)."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        tipos = [(f"{descripcion} (*.{extension})", f"*.{extension}"), ("Todos los archivos", "*.*")]
        return filedialog.asksaveasfilename(
            parent=self.root,
            title=f"Guardar {descripcion} como",
            defaultextension=f".{extension}",
            initialfile=f"{prefijo}_{ts}.{extension}",
            filetypes=tipos,
        ) or None

    def _exportar_con_dialogo(self, prefijo, extension, descripcion, funcion, *args):
        ruta = self._pedir_ruta(prefijo, extension, descripcion)
        if not ruta:
            return None
        return funcion(*args, ruta=ruta)

    def _ejecutar_exportar(self, titulo, opciones):
        resultado = abrir_dialog(self.root, ExportarDialog, titulo=titulo, opciones=opciones)
        if resultado and resultado.get("ruta"):
            toast(self.root, f"Archivo guardado: {resultado['ruta']}", "success")
            self._set_status(f"Exportado a {resultado['ruta']}")

    def exportar_citas(self):
        self._ejecutar_exportar(
            "Exportar listado de citas",
            [
                ("Excel (CSV) — listado completo de citas",
                 lambda: self._exportar_con_dialogo("citas", "csv", "Excel CSV",
                                                    exportar_mod.exportar_citas_csv)),
                ("PDF — listado completo de citas",
                 lambda: self._exportar_con_dialogo("citas", "pdf", "PDF",
                                                    exportar_mod.exportar_citas_pdf)),
            ],
        )

    def exportar_kpi(self):
        opciones = [
            ("Excel (CSV) — atenciones registradas",
             lambda: self._exportar_con_dialogo("atenciones", "csv", "Excel CSV",
                                                 exportar_mod.exportar_atenciones_csv)),
            ("PDF — atenciones registradas",
             lambda: self._exportar_con_dialogo("atenciones", "pdf", "PDF",
                                                 exportar_mod.exportar_atenciones_pdf)),
            ("Excel (CSV) — resumen KPI completo",
             lambda: self._exportar_con_dialogo("kpi_resumen", "csv", "Excel CSV",
                                                 exportar_mod.exportar_kpi_csv)),
            ("PDF — resumen KPI completo",
             lambda: self._exportar_con_dialogo("kpi_resumen", "pdf", "PDF",
                                                 exportar_mod.exportar_kpi_pdf)),
        ]
        # Si está en modo Pacientes y hay uno seleccionado, agregar timeline
        if getattr(self, "_kpi_modo", "atenciones") == "pacientes":
            sel = self.tree.selection()
            pacientes = getattr(self, "_pacientes_visibles", [])
            if sel and pacientes:
                idx = self.tree.index(sel[0])
                if idx < len(pacientes):
                    cita = pacientes[idx]
                    opciones.append((
                        f"PDF — timeline del paciente {cita.paciente.nombre}",
                        lambda c=cita: self._exportar_con_dialogo(
                            f"timeline_{c.id_cita}", "pdf", "PDF",
                            exportar_mod.exportar_timeline_paciente_pdf, c,
                        ),
                    ))
        self._ejecutar_exportar("Exportar KPI / atenciones", opciones)


def launch_simple_app():
    from services.seed_data import cargar_datos_demo
    cargar_datos_demo()
    root = tk.Tk()
    app = TBMedicSimpleApp(root)
    root.mainloop()
