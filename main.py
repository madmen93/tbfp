from models.paciente import Paciente
from models.cita import Cita
from services.gestion_citas import registrar_cita, mostrar_citas
from services.gestion_protocolos import generar_protocolo
from services.flujo_pacientes import menu_flujo_pacientes

paciente1 = Paciente(
    "Juan Pérez",
    "12345678",
    28,
    "Masculino",
    "Empresa ABC"
)

cita1 = Cita(
    "00001",
    paciente1,
    "1/06/2026",
    "07:00",
    "Preocupacional"
)

registrar_cita(cita1)

mostrar_citas()

generar_protocolo()

menu_flujo_pacientes()