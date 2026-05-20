class Cita:
    ESTADO_PROGRAMADA = "Programada"
    ESTADO_EN_FLUJO = "En flujo"
    ESTADO_ATENDIDA = "Atendida"
    ESTADO_CANCELADA = "Cancelada"

    def __init__(self, id_cita, paciente, fecha, hora, emo,
                 es_mina=False, riesgos=None, protocolo=None):
        self.id_cita = id_cita
        self.paciente = paciente
        self.fecha = fecha
        self.hora = hora
        self.emo = emo
        self.es_mina = es_mina
        self.riesgos = list(riesgos or [])

        # Protocolo asociado: dict con items, total, areas, texto
        self.protocolo = protocolo or {"items": [], "total": 0, "areas": [], "texto": ""}

        # Ciclo de vida en el flujo
        self.estado = Cita.ESTADO_PROGRAMADA
        self.areas_pendientes = list(self.protocolo.get("areas", []))
        self.areas_completadas = []
        self.area_actual = None
        # Trazabilidad por área: {area: {"ingreso": dt, "atencion": dt, "espera_min": int}}
        self.tiempos_por_area = {}

    @property
    def total(self):
        return self.protocolo.get("total", 0)

    @property
    def items_protocolo(self):
        return self.protocolo.get("items", [])

    @property
    def texto_protocolo(self):
        return self.protocolo.get("texto", "")

    def mostrar_cita(self):
        print("----CITA MÉDICA----")
        print(f"ID Cita: {self.id_cita}")
        print(f"Paciente: {self.paciente.nombre}")
        print(f"Fecha: {self.fecha}")
        print(f"Hora: {self.hora}")
        print(f"Tipo de Examen: {self.emo.tipo}")
        print(f"Perfil: {self.emo.perfil}")
        print(f"Estado: {self.estado}")
        if self.protocolo.get("areas"):
            print(f"Ruta: {' → '.join(self.protocolo['areas'])}")
        print(f"Total: S/ {self.total:.2f}")
