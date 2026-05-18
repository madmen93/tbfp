class Cita:
    def __init__(self, id_cita, paciente, fecha, hora, emo):
        self.id_cita = id_cita
        self.paciente = paciente
        self.fecha = fecha
        self.hora = hora
        self.emo = emo
        self.estado = "Programada"
        
    def mostrar_cita(self):
        print("----CITA MÉDICA----")
        print(f"ID Cita: {self.id_cita}")
        print(f"Paciente: {self.paciente.nombre}")
        print(f"Fecha: {self.fecha}")
        print(f"Hora: {self.hora}")
        print(f"Tipo de Examen: {self.emo.tipo}")
        print(f"Perfil: {self.emo.perfil}")
        print(f"Estado: {self.estado}")
                                 