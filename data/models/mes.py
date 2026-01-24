class Mes:
    def __init__(self, id_mes: int, nombre_mes: str):
        self.id_mes = id_mes
        self.nombre_mes = nombre_mes
    
    def __str__(self):
        return self.nombre_mes
    
    def __post_init__(self):
        pass