import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

from models.paciente import Paciente
from models.cita import Cita
from models.emo import Emo

from services import gestion_citas

from utils.validaciones import (
    validar_texto_no_vacio,
    validar_solo_letras,
    validar_nombre_completo,
    validar_dni,
    validar_edad,
    validar_fecha,
    validar_hora
)


class SistemaMedicoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Médico Ocupacional")
        self.root.geometry("850x550")

        self.frame = ttk.Frame(root, padding=10)
        self.frame.pack(fill="both", expand=True)

        self.lista = None

        self.mostrar_menu_principal()

    def limpiar_pantalla(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def mostrar_menu_principal(self):
        self.limpiar_pantalla()

        ttk.Label(
            self.frame,
            text="Menú Principal",
            font=("Arial", 16, "bold")
        ).pack(pady=20)

        ttk.Button(
            self.frame,
            text="Gestión de citas",
            command=self.mostrar_menu_citas
        ).pack(pady=5)

        ttk.Button(
            self.frame,
            text="Flujo de pacientes",
            command=self.mostrar_menu_flujo
        ).pack(pady=5)

        ttk.Button(
            self.frame,
            text="Protocolos",
            command=self.mostrar_menu_protocolos
        ).pack(pady=5)

        ttk.Button(
            self.frame,
            text="Salir",
            command=self.root.destroy
        ).pack(pady=20)

    def mostrar_menu_citas(self):
        self.limpiar_pantalla()

        ttk.Label(
            self.frame,
            text="Gestión de Citas Médicas",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        botones = ttk.Frame(self.frame)
        botones.pack(pady=10)

        ttk.Button(botones, text="Registrar cita", command=self.registrar_cita).pack(side="left", padx=5)
        ttk.Button(botones, text="Actualizar lista", command=self.actualizar_lista).pack(side="left", padx=5)
        ttk.Button(botones, text="Editar cita", command=self.editar_cita).pack(side="left", padx=5)
        ttk.Button(botones, text="Eliminar cita", command=self.eliminar_cita).pack(side="left", padx=5)
        ttk.Button(botones, text="Volver", command=self.mostrar_menu_principal).pack(side="left", padx=5)

        self.lista = tk.Listbox(self.frame, height=18)
        self.lista.pack(fill="both", expand=True, pady=10)

        self.actualizar_lista()

    def mostrar_menu_flujo(self):
        self.limpiar_pantalla()

        ttk.Label(
            self.frame,
            text="Flujo de Pacientes",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        self.lista = tk.Listbox(self.frame, height=18)
        self.lista.pack(fill="both", expand=True, pady=10)

        self.lista.insert("end", "=== FLUJO DE PACIENTES ===")
        self.lista.insert("end", "1. Recepción del paciente")
        self.lista.insert("end", "2. Verificación de datos personales")
        self.lista.insert("end", "3. Validación de cita programada")
        self.lista.insert("end", "4. Evaluación médica ocupacional")
        self.lista.insert("end", "5. Registro de resultados")
        self.lista.insert("end", "6. Emisión del informe médico")

        ttk.Button(
            self.frame,
            text="Volver al menú principal",
            command=self.mostrar_menu_principal
        ).pack(pady=10)

    def mostrar_menu_protocolos(self):
        self.limpiar_pantalla()

        ttk.Label(
            self.frame,
            text="Protocolos Médicos",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        self.lista = tk.Listbox(self.frame, height=18)
        self.lista.pack(fill="both", expand=True, pady=10)

        self.lista.insert("end", "=== PROTOCOLOS MÉDICOS ===")
        self.lista.insert("end", "PREOCUPACIONAL: evaluación antes del ingreso laboral.")
        self.lista.insert("end", "PERIÓDICO: evaluación durante la relación laboral.")
        self.lista.insert("end", "RETIRO: evaluación al finalizar el vínculo laboral.")
        self.lista.insert("end", "OTRO: evaluación médica según requerimiento específico.")

        ttk.Button(
            self.frame,
            text="Volver al menú principal",
            command=self.mostrar_menu_principal
        ).pack(pady=10)

    def pedir_texto_validado(self, titulo, mensaje, funcion_validacion, mensaje_error):
        while True:
            valor = simpledialog.askstring(titulo, mensaje, parent=self.root)

            if valor is None:
                return None

            valor = valor.strip().upper()

            if funcion_validacion(valor):
                return valor

            messagebox.showerror("Dato inválido", mensaje_error, parent=self.root)

    def registrar_cita(self):
        empresa = self.pedir_texto_validado(
            "Empresa",
            "Razón social:",
            validar_texto_no_vacio,
            "La razón social no puede estar vacía."
        )
        if empresa is None:
            return

        nombre = self.pedir_texto_validado(
            "Paciente",
            "Nombre completo del paciente:",
            lambda x: validar_texto_no_vacio(x)
            and validar_solo_letras(x)
            and validar_nombre_completo(x),
            "El nombre debe tener al menos 3 palabras y no contener números."
        )
        if nombre is None:
            return

        dni = self.pedir_texto_validado(
            "DNI",
            "Documento de identidad:",
            validar_dni,
            "El DNI debe contener 8 dígitos."
        )
        if dni is None:
            return

        edad = self.pedir_texto_validado(
            "Edad",
            "Edad del paciente:",
            validar_edad,
            "La edad debe ser válida."
        )
        if edad is None:
            return

        edad = int(edad)

        sexo = self.pedir_texto_validado(
            "Sexo",
            "Sexo del paciente: MASCULINO / FEMENINO",
            lambda x: x in ["MASCULINO", "FEMENINO"],
            "Debe ingresar MASCULINO o FEMENINO."
        )
        if sexo is None:
            return

        tipo = self.pedir_texto_validado(
            "Tipo de examen",
            "Tipo: PREOCUPACIONAL / PERIÓDICO / RETIRO / OTRO",
            lambda x: x in ["PREOCUPACIONAL", "PERIÓDICO", "RETIRO", "OTRO"],
            "Tipo de examen inválido."
        )
        if tipo is None:
            return

        perfil = self.pedir_texto_validado(
            "Perfil",
            "Perfil: ADMINISTRATIVO / OPERATIVO / MINA / ALTO RIESGO",
            lambda x: x in ["ADMINISTRATIVO", "OPERATIVO", "MINA", "ALTO RIESGO"],
            "Perfil inválido."
        )
        if perfil is None:
            return

        while True:
            fecha = self.pedir_texto_validado(
                "Fecha",
                "Fecha de cita (dd/mm/aaaa):",
                validar_fecha,
                "La fecha debe tener formato dd/mm/aaaa y ser desde mañana."
            )
            if fecha is None:
                return

            hora = self.pedir_texto_validado(
                "Hora",
                "Hora de cita (HH:MM):",
                validar_hora,
                "La hora debe estar en el rango permitido."
            )
            if hora is None:
                return

            if gestion_citas.validar_tope_atenciones(fecha, hora):
                break

            messagebox.showerror(
                "Tope alcanzado",
                "Ese horario ya alcanzó el tope máximo de atenciones. Ingrese otra fecha u hora.",
                parent=self.root
            )

        paciente = Paciente(nombre, dni, edad, sexo, empresa)
        emo = Emo(tipo, perfil)

        id_cita = gestion_citas.generar_id_cita()
        cita = Cita(id_cita, paciente, fecha, hora, emo)

        gestion_citas.registrar_cita(cita)

        messagebox.showinfo(
            "Registro exitoso",
            f"Cita {id_cita} registrada correctamente.",
            parent=self.root
        )

        self.actualizar_lista()

    def actualizar_lista(self):
        if self.lista is None:
            return

        self.lista.delete(0, "end")

        if len(gestion_citas.lista_citas) == 0:
            self.lista.insert("end", "No hay citas registradas.")
            return

        for cita in gestion_citas.lista_citas:
            self.lista.insert(
                "end",
                f"{cita.id_cita} | {cita.paciente.nombre} | {cita.fecha} | {cita.hora} | {cita.emo.tipo} | {cita.emo.perfil}"
            )

    def obtener_cita_seleccionada(self):
        if self.lista is None:
            return None

        seleccion = self.lista.curselection()

        if not seleccion:
            return None

        indice = seleccion[0]

        if indice >= len(gestion_citas.lista_citas):
            return None

        return gestion_citas.lista_citas[indice]

    def editar_cita(self):
        cita = self.obtener_cita_seleccionada()

        if cita is None:
            messagebox.showwarning(
                "Seleccionar cita",
                "Seleccione una cita válida.",
                parent=self.root
            )
            return

        nueva_fecha = self.pedir_texto_validado(
            "Editar fecha",
            "Nueva fecha de cita (dd/mm/aaaa):",
            validar_fecha,
            "La fecha debe tener formato dd/mm/aaaa y ser desde mañana."
        )

        if nueva_fecha is None:
            return

        nueva_hora = self.pedir_texto_validado(
            "Editar hora",
            "Nueva hora de cita (HH:MM):",
            validar_hora,
            "La hora debe estar en el rango permitido."
        )

        if nueva_hora is None:
            return

        if not gestion_citas.validar_tope_atenciones(nueva_fecha, nueva_hora):
            messagebox.showerror(
                "Tope alcanzado",
                "Ese horario ya alcanzó el tope máximo de atenciones.",
                parent=self.root
            )
            return

        cita.fecha = nueva_fecha
        cita.hora = nueva_hora

        self.actualizar_lista()

        messagebox.showinfo(
            "Cita actualizada",
            "La cita fue actualizada correctamente.",
            parent=self.root
        )

    def eliminar_cita(self):
        cita = self.obtener_cita_seleccionada()

        if cita is None:
            messagebox.showwarning(
                "Seleccionar cita",
                "Seleccione una cita válida.",
                parent=self.root
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Desea eliminar la cita {cita.id_cita}?",
            parent=self.root
        )

        if confirmar:
            gestion_citas.lista_citas.remove(cita)
            self.actualizar_lista()
            messagebox.showinfo(
                "Eliminado",
                "Cita eliminada correctamente.",
                parent=self.root
            )


def iniciar_app():
    root = tk.Tk()
    app = SistemaMedicoApp(root)
    root.mainloop()