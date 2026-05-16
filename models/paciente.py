class Paciente:
    def __init__(self, nombre, id, edad, sexo, empresa):
        self.nombre = nombre
        self.id = id
        self.edad = edad
        self.sexo = sexo
        self.empresa = empresa

    def mostrar_datos(self):
        print("----Datos del Paciente----")
        print(f"Nombre: {self.nombre}")
        print(f"ID: {self.id}")
        print(f"Edad: {self.edad}")
        print(f"Sexo: {self.sexo}")
        print(f"Empresa: {self.empresa}")