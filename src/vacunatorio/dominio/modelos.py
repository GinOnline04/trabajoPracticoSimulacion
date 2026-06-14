from dataclasses import dataclass


@dataclass
class Paciente:
    id: int
    vacuna: str
    llegada: float
    grupo: int
    estado: str = "Esperando"
    inicio_vacunacion: float = 0.0
