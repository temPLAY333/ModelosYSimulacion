from dataclasses import dataclass


@dataclass
class Material:
    """
    Representa un material con propiedades térmicas.
    
    Attributes:
        name: Nombre del material
        thermal_conductivity: Conductividad térmica en W/(m·K)
        specific_heat: Calor específico en J/(kg·K)
        density: Densidad en kg/m³
    """
    
    def __init__(self, name: str, 
                 thermal_conductivity: float, 
                 specific_heat: float, 
                 density: float):
        """
        Inicializa un material con propiedades térmicas específicas.
        
        Args:
            name: Nombre del material
            thermal_conductivity: Conductividad térmica en W/(m·K)
            specific_heat: Calor específico en J/(kg·K)
            density: Densidad en kg/m³
        """
        self.name = name
        self.thermal_conductivity = thermal_conductivity
        self.specific_heat = specific_heat
        self.density = density
    
    def thermal_diffusivity(self) -> float:
        """
        Calcula la difusividad térmica
        
        Returns:
            Difusividad térmica en m²/s
        """
        return self.thermal_conductivity / (self.density * self.specific_heat)
    
    def get_thermal_resistance_factor(self, thickness: float) -> float:
        """
        Calcula el factor de resistencia térmica (valor R) del material
        para un espesor dado.
        
        Args:
            thickness: Espesor del material en metros
            
        Returns:
            Resistencia térmica en m²·K/W
        """
        return thickness / self.thermal_conductivity
