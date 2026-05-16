class Cita:
    def __init__(self, id_cita, paciente, fecha, hora, tipo_examen):
        self.id_cita = id_cita
        self.paciente = paciente
        self.fecha = fecha
        self.hora = hora
        self.tipo_examen = tipo_examen
        self.estado = "Programada"
        
    def mostrar_cita(self):
        print("----CITA MÉDICA----")
        print(f"ID Cita: {self.id_cita}")
        print(f"Paciente: {self.paciente.nombre}")
        print(f"Fecha: {self.fecha}")
        print(f"Hora: {self.hora}")
        print(f"Tipo de Examen: {self.tipo_examen}")
        print(f"Estado: {self.estado}")
                                 