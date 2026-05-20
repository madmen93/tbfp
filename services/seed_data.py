"""Datos de demostración para el piloto: 60 citas distribuidas entre 4 empresas."""
import random
from datetime import date, timedelta

from models.paciente import Paciente
from models.cita import Cita
from models.emo import Emo
from services.gestion_protocolos import (
    construir_protocolo, TIPO_A_OPCION, TIPOS_EXAMEN,
)
import services.gestion_citas as gestion_citas


EMPRESAS = [
    {
        "nombre": "MINERA ANDINA SAC",
        "es_mina": True,
        "perfil_default": "Mina",
        "riesgos_tipicos": [
            "Trabajo en altura (> 1.80m)",
            "Exposición a Radiaciones",
            "Operadores de maquinaria pesada",
        ],
    },
    {
        "nombre": "CONSTRUCTORA PERU SA",
        "es_mina": False,
        "perfil_default": "Operativo",
        "riesgos_tipicos": [
            "Trabajo en altura (> 1.80m)",
            "Espacios confinados",
            "Operadores de maquinaria pesada",
        ],
    },
    {
        "nombre": "ENERGIA SUR SAC",
        "es_mina": False,
        "perfil_default": "Operativo",
        "riesgos_tipicos": [
            "Manipulación de Químicos",
            "Exposición a Radiaciones",
            "Espacios confinados",
        ],
    },
    {
        "nombre": "AGRO EXPORT SA",
        "es_mina": False,
        "perfil_default": "Administrativo",
        "riesgos_tipicos": [],
    },
]

NOMBRES = [
    ("JUAN", "PEREZ", "LOPEZ"),
    ("MARIA", "GARCIA", "VARGAS"),
    ("CARLOS", "MENDOZA", "RIOS"),
    ("LUISA", "TORRES", "CASTILLO"),
    ("PEDRO", "RAMIREZ", "FLORES"),
    ("ANA", "MORALES", "SILVA"),
    ("JOSE", "DIAZ", "CHAVEZ"),
    ("CARMEN", "VEGA", "ROJAS"),
    ("MIGUEL", "QUISPE", "HUAMAN"),
    ("ROSA", "CONDORI", "MAMANI"),
    ("ANTONIO", "FERNANDEZ", "MUNOZ"),
    ("LUCIA", "JIMENEZ", "GUTIERREZ"),
    ("ROBERTO", "AGUILAR", "ROMERO"),
    ("PATRICIA", "HERRERA", "MEDINA"),
    ("FERNANDO", "BENITES", "ARIAS"),
    ("SOFIA", "REYES", "VALDIVIA"),
    ("DIEGO", "PAREDES", "GUZMAN"),
    ("ELENA", "SANTOS", "RAMOS"),
    ("MARCO", "CHOQUE", "QUIROZ"),
    ("VALERIA", "CARRILLO", "SOTO"),
    ("JAVIER", "CRUZ", "VELASQUEZ"),
    ("DANIELA", "BAUTISTA", "RIVERA"),
    ("RICARDO", "GUEVARA", "ALARCON"),
    ("ISABEL", "BLANCO", "ESCOBAR"),
    ("ENRIQUE", "DELGADO", "CABRERA"),
    ("CRISTINA", "ROSALES", "PENA"),
    ("OSCAR", "SUAREZ", "VALENCIA"),
    ("MONICA", "CACERES", "MAYTA"),
    ("RAUL", "ARANIBAR", "VILLALBA"),
    ("PAOLA", "ZUNIGA", "ESPINOZA"),
    ("FRANCISCO", "CARDENAS", "TORRES"),
    ("GLORIA", "MAMANI", "QUISPE"),
    ("MARTIN", "ROSAS", "ZEVALLOS"),
    ("VERONICA", "PINEDA", "OCHOA"),
    ("ALONSO", "ALARCON", "LIMACHI"),
    ("CECILIA", "VARGAS", "TORRES"),
    ("ARTURO", "MORALES", "ARANA"),
    ("LILIANA", "CASTILLO", "AYALA"),
    ("EDUARDO", "RIVAS", "MIRANDA"),
    ("BEATRIZ", "ORTEGA", "SALAS"),
    ("ANDRES", "VELASCO", "TICONA"),
    ("KARINA", "ROMERO", "FUENTES"),
    ("HECTOR", "MEZA", "MAMANI"),
    ("CLAUDIA", "OLIVERA", "RIOS"),
    ("WILLIAM", "ROJAS", "QUISPE"),
    ("ALICIA", "FIGUEROA", "ZAPATA"),
    ("LEONARDO", "SALAS", "PALOMINO"),
    ("MARTHA", "QUISPE", "GUTIERREZ"),
    ("CESAR", "VALDIVIA", "TARQUI"),
    ("GABRIELA", "ZAPATA", "ABARCA"),
    ("HUGO", "TICONA", "CALLATA"),
    ("ANDREA", "PEREZ", "CONDORI"),
    ("VICTOR", "CASTILLO", "MERMA"),
    ("CAROLINA", "FLORES", "APAZA"),
    ("RUBEN", "CHAMBI", "CUTIPA"),
    ("FIORELLA", "AYALA", "BUSTAMANTE"),
    ("DAVID", "ESPINOZA", "HUANCA"),
    ("NATALY", "HUAMAN", "GOMEZ"),
    ("KEVIN", "GUZMAN", "PUMA"),
    ("YESSICA", "PUMA", "ANCO"),
]


def cargar_datos_demo(total=60, seed=42):
    """Carga 60 citas de demo para HOY entre 19:00 y 22:00."""
    if gestion_citas.lista_citas:
        return 0

    random.seed(seed)
    fecha_hoy = date.today().strftime("%d/%m/%Y")

    dni_base = 70000000
    creadas = 0
    intentos = 0
    n_nombres = len(NOMBRES)

    while creadas < total and intentos < total * 4:
        intentos += 1
        empresa = EMPRESAS[creadas % len(EMPRESAS)]
        nombre_t = NOMBRES[creadas % n_nombres]
        if creadas >= n_nombres:
            nombre = f"{nombre_t[0]} {nombre_t[1]} {nombre_t[2]}"
        else:
            nombre = " ".join(nombre_t)

        dni = str(dni_base + creadas)
        edad = random.randint(22, 58)
        sexo = "Masculino" if creadas % 2 == 0 else "Femenino"

        tipo = random.choice(TIPOS_EXAMEN)
        opcion = TIPO_A_OPCION[tipo]
        es_mina = empresa["es_mina"]
        riesgos_disp = empresa["riesgos_tipicos"]
        if riesgos_disp:
            n_riesgos = random.randint(0, min(2, len(riesgos_disp)))
            riesgos = random.sample(riesgos_disp, n_riesgos) if n_riesgos else []
        else:
            riesgos = []

        try:
            proto = construir_protocolo(opcion, es_mina, riesgos)
        except ValueError:
            continue

        # Buscar primera hora con cupo del día de hoy
        horas_orden = list(gestion_citas.HORAS_DISPONIBLES)
        random.shuffle(horas_orden)
        hora_libre = None
        for h in horas_orden:
            if gestion_citas.validar_tope_atenciones(fecha_hoy, h):
                hora_libre = h
                break
        if hora_libre is None:
            break  # día lleno

        paciente = Paciente(nombre, dni, edad, sexo, empresa["nombre"])
        emo = Emo(tipo, empresa["perfil_default"])
        cita = Cita(
            gestion_citas.generar_id_cita(),
            paciente, fecha_hoy, hora_libre, emo,
            es_mina=es_mina, riesgos=riesgos, protocolo=proto,
        )
        gestion_citas.lista_citas.append(cita)
        creadas += 1

    return creadas


def reset_demo():
    """Vacía las citas y recarga el demo."""
    gestion_citas.lista_citas.clear()
    return cargar_datos_demo()
