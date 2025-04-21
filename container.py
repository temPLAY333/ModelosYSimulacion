from typing import Dict, Any, Union, Literal
from dataclasses import dataclass
from material import Material
from fluid import Fluid

@dataclass
class Shape:
    """
    Representa la forma del contenedor
    
    Attributes:
        type: Tipo de forma (cilíndrica, rectangular, esférica)
        dimensions: Dimensiones de la forma en metros
    """
    type: Literal["cylindrical", "rectangular", "spherical"]
    dimensions: Dict[str, float]  # En metros

class Container:
    """
    Representa un contenedor con propiedades específicas
    
    Attributes:
        volumen: Volumen del contenedor en m³
        forma: Objeto Shape que define la geometría
        fluido: Objeto Fluid que contiene
        material: Objeto Material que compone el contenedor
        wall_thickness: Espesor de la pared del contenedor en metros
        temperatura: Temperatura actual del fluido en Celsius
    """
    
    def __init__(self, 
                 volumen: float, 
                 forma: Shape, 
                 fluido: Fluid, 
                 material: Material,
                 wall_thickness: float = 0.005):
        """
        Inicializa un contenedor con propiedades específicas
        """
        self.volumen: float = volumen
        self.forma: Shape = forma
        self.fluido: Fluid = fluido
        self.material: Material = material
        self.wall_thickness: float = wall_thickness
        
    def get_propiedades(self) -> Dict[str, Any]:
        """
        Retorna las propiedades del contenedor
        
        Returns:
            Diccionario con las propiedades del contenedor
        """
        return {
            'volumen': self.volumen,
            'forma': self.forma,
            'fluido': self.fluido,
            'material': self.material,
            'temperatura': self.temperatura
        }
        
    def get_surface_area(self) -> float:
        """
        Calcula el área de superficie del contenedor basado en su forma
        
        Returns:
            Área de superficie en m²
        """
        if self.forma.type == "cylindrical":
            radius = self.forma.dimensions.get("radius", 0)
            height = self.forma.dimensions.get("height", 0)
            return 2 * 3.14159 * radius * (radius + height)
        
        elif self.forma.type == "rectangular":
            width = self.forma.dimensions.get("width", 0)
            length = self.forma.dimensions.get("length", 0)
            height = self.forma.dimensions.get("height", 0)
            return 2 * (width * length + width * height + length * height)
        
        elif self.forma.type == "spherical":
            radius = self.forma.dimensions.get("radius", 0)
            return 4 * 3.14159 * radius * radius
        
        raise ValueError(f"Forma no soportada: {self.forma.type}")
