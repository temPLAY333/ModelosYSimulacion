from dataclasses import dataclass


@dataclass
class Fluid:
    """
    Representa un fluido con propiedades térmicas específicas.
    
    Attributes:
        name: Nombre del fluido
        specific_heat: Calor específico en J/(kg·K)
        density: Densidad en kg/m³
        viscosity: Viscosidad en Pa·s
        thermal_conductivity: Conductividad térmica en W/(m·K)
    """

    
    def __init__(self, name: str, 
                 specific_heat: float, 
                 density: float, 
                 viscosity: float, 
                 thermal_conductivity: float,
                 temp: float = 20.0):
        """
        Inicializa un fluido con propiedades térmicas específicas.
        
        Args:
            name: Nombre del fluido
            specific_heat: Calor específico en J/(kg·K)
            density: Densidad en kg/m³
            viscosity: Viscosidad en Pa·s
            thermal_conductivity: Conductividad térmica en W/(m·K)
        """
        self.name = name
        self.specific_heat = specific_heat
        self.density = density
        self.viscosity = viscosity
        self.thermal_conductivity = thermal_conductivity
        self.temperature = temp  # Temperatura inicial en grados Celsius
    
    def heat_capacity_per_volume(self) -> float:
        """
        Calcula la capacidad calorífica volumétrica
        
        Returns:
            Capacidad calorífica volumétrica en J/(m³·K)
        """
        return self.specific_heat * self.density
