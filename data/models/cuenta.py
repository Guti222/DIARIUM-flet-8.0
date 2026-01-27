from dataclasses import dataclass
from typing import Optional
from data.models.plan_cuenta import PlanCuenta

@dataclass
class TipoCuenta:
    id_tipo_cuenta: int = 0
    nombre_tipo_cuenta: str = ''
    numero_cuenta: str = ''
    
    def __str__(self):
        return self.nombre_tipo_cuenta

@dataclass
class Rubro:
    id_rubro: int = 0
    id_tipo_cuenta: int = 0
    nombre_rubro: str = ''
    numero_cuenta: str = ''
    tipo_cuenta: Optional[TipoCuenta] = None  # Relación directa
    
    def __str__(self):
        return self.nombre_rubro
    
    def __post_init__(self):
        if self.tipo_cuenta is None:
            self.tipo_cuenta = TipoCuenta()

@dataclass
class Generico:
    id_generico: int = 0
    id_rubro: int = 0
    nombre_generico: str = ''
    numero_cuenta: str = ''
    rubro: Optional[Rubro] = None  # Relación directa
    
    def __str__(self):
        return self.nombre_generico
    
    def __post_init__(self):
        if self.rubro is None:
            self.rubro = Rubro()

@dataclass
class CuentaContable:
    id_cuenta_contable: int = 0
    id_generico: int = 0
    descripcion: str = ''
    nombre_cuenta: str = ''
    codigo_cuenta: str = ''
    generico: Optional[Generico] = None
    id_plan_cuenta: int = 0  # Asumiendo que hay un plan de cuenta relacionado
    
    def __str__(self):
        return f"{self.codigo_cuenta} - {self.nombre_cuenta}"
    
    def __post_init__(self):
        if self.generico is None:
            self.generico = Generico()
            self.plan_cuenta= PlanCuenta()
    
    @property
    def nombre_plan_cuenta(self) -> str:
        """Devuelve el nombre del plan de cuenta asociado (placeholder)"""
        # Aquí podrías implementar la lógica para obtener el nombre del plan de cuenta
        return getattr(self.plan_cuenta, 'nombre_plan_cuenta', '') if self.generico else ''
    
    # Propiedades para acceso fácil a datos relacionados
    @property
    def nombre_generico(self) -> str:
        """Devuelve el nombre del genérico con manejo seguro de None"""
        return getattr(self.generico, 'nombre_generico', '') if self.generico else ''
    
    @property
    def nombre_rubro(self) -> str:
        """Devuelve el nombre del rubro con manejo seguro de None"""
        if self.generico and hasattr(self.generico, 'rubro') and self.generico.rubro:
            return getattr(self.generico.rubro, 'nombre_rubro', '')
        return ''
    
    @property
    def nombre_tipo_cuenta(self) -> str:
        """Devuelve el nombre del tipo de cuenta con manejo seguro de None"""
        if (self.generico and 
            hasattr(self.generico, 'rubro') and self.generico.rubro and 
            hasattr(self.generico.rubro, 'tipo_cuenta') and self.generico.rubro.tipo_cuenta):
            return getattr(self.generico.rubro.tipo_cuenta, 'nombre_tipo_cuenta', '')
        return ''
    
    @property
    def id_rubro(self) -> int:
        """Devuelve el ID del rubro relacionado"""
        if self.generico and hasattr(self.generico, 'rubro') and self.generico.rubro:
            return getattr(self.generico.rubro, 'id_rubro', 0)
        return 0
    
    @property
    def id_tipo_cuenta(self) -> int:
        """Devuelve el ID del tipo de cuenta relacionado"""
        if (self.generico and 
            hasattr(self.generico, 'rubro') and self.generico.rubro and 
            hasattr(self.generico.rubro, 'tipo_cuenta') and self.generico.rubro.tipo_cuenta):
            return getattr(self.generico.rubro.tipo_cuenta, 'id_tipo_cuenta', 0)
        return 0
    
    @property
    def ruta_completa(self) -> str:
        """Devuelve la ruta jerárquica completa de la cuenta"""
        partes = []
        if self.nombre_tipo_cuenta:
            partes.append(self.nombre_tipo_cuenta)
        if self.nombre_rubro:
            partes.append(self.nombre_rubro)
        if self.nombre_generico:
            partes.append(self.nombre_generico)
        if self.nombre_cuenta:
            partes.append(self.nombre_cuenta)
        
        return " > ".join(partes) if partes else "Sin información"
    
    @property
    def ruta_codigos(self) -> str:
        """Devuelve la ruta de códigos jerárquica"""
        partes = []
        if self.codigo_cuenta:
            # Tomar solo las partes principales del código (ej: "1.1.1" de "1.1.1.01")
            codigo_base = '.'.join(self.codigo_cuenta.split('.')[:-1])
            if codigo_base:
                partes.append(codigo_base)
            partes.append(self.codigo_cuenta)
        
        return " > ".join(partes) if partes else self.codigo_cuenta
    
    @property
    def nivel(self) -> int:
        """Calcula el nivel de la cuenta basado en los puntos del código"""
        return self.codigo_cuenta.count('.') + 1 if self.codigo_cuenta else 0
    
    @property
    def es_cuenta_analitica(self) -> bool:
        """Determina si es una cuenta analítica (nivel más bajo)"""
        return self.nivel >= 4  # Ajusta según tu estructura de códigos
    
    @property
    def es_cuenta_sintetica(self) -> bool:
        """Determina si es una cuenta sintética (nivel intermedio)"""
        return 2 <= self.nivel <= 3  # Ajusta según tu estructura
    
    def tiene_relaciones_completas(self) -> bool:
        """Verifica si la cuenta tiene todas sus relaciones cargadas"""
        return (self.generico is not None and 
                self.generico.rubro is not None and 
                self.generico.rubro.tipo_cuenta is not None)
    
    def obtener_info_jerarquica(self) -> dict:
        """Devuelve un diccionario con toda la información jerárquica"""
        return {
            'cuenta': {
                'id': self.id_cuenta_contable,
                'nombre': self.nombre_cuenta,
                'codigo': self.codigo_cuenta,
                'descripcion': self.descripcion,
                'nivel': self.nivel
            },
            'generico': {
                'id': self.generico.id_generico if self.generico else 0,
                'nombre': self.nombre_generico
            },
            'rubro': {
                'id': self.id_rubro,
                'nombre': self.nombre_rubro
            },
            'tipo_cuenta': {
                'id': self.id_tipo_cuenta,
                'nombre': self.nombre_tipo_cuenta
            },
            'ruta_completa': self.ruta_completa
        }
    
    def mostrar_info_detallada(self) -> str:
        """Muestra información detallada de la cuenta"""
        info = f"""
        CUENTA CONTABLE:
        ================
        Código: {self.codigo_cuenta}
        Nombre: {self.nombre_cuenta}
        Descripción: {self.descripcion}
        Nivel: {self.nivel}
        
        JERARQUÍA:
        ==========
        Tipo de Cuenta: {self.nombre_tipo_cuenta}
        Rubro: {self.nombre_rubro}
        Genérico: {self.nombre_generico}
        
        Ruta Completa: {self.ruta_completa}
        """
        return info