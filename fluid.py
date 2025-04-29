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
                 volumen: float = 0.0,
                 specific_heat: float = 0.0, 
                 density: float = 0.0, 
                 viscosity: float = 0.0, 
                 thermal_conductivity: float = 0.0,
                 temp: float = 20.0):
        """
        Inicializa un fluido con propiedades térmicas específicas.
        
        Args:
            name: Nombre del fluido
            volumen: Volumen del fluido en m³
            specific_heat: Calor específico en J/(kg·K)
            density: Densidad en kg/m³
            viscosity: Viscosidad en Pa·s
            thermal_conductivity: Conductividad térmica en W/(m·K)
            temp: Temperatura inicial del fluido en °C
        """
        self.name = name
        self.volumen = volumen
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
    
    def add_ice(self, ice_mass, ice_temp=-0.0):
        """
        Añade hielo al fluido y calcula la nueva temperatura resultante
        
        Args:
            ice_mass (float): Masa del hielo en kg
            ice_temp (float): Temperatura del hielo en °C (por defecto: -5°C)
        """
        # Constantes físicas
        latent_heat_fusion = 334000.0  # J/kg (calor latente de fusión del hielo)
        ice_specific_heat = 2108.0     # J/(kg·°C) (calor específico del hielo)
        
        # Calcular masa actual del fluido
        fluid_mass = self.density * self.volumen
        
        # Energía para calentar el hielo hasta 0°C
        energy_to_heat_ice = ice_mass * ice_specific_heat * (0 - ice_temp)
        
        # Energía para derretir el hielo (cambio de fase)
        energy_to_melt_ice = ice_mass * latent_heat_fusion
        
        # Energía total extraída del fluido
        total_energy_required = energy_to_heat_ice + energy_to_melt_ice
        
        # Cambio de temperatura en el fluido original
        temp_change = total_energy_required / (fluid_mass * self.specific_heat)
        new_temp = self.temperature - temp_change
        
        # Actualizar el volumen (el hielo se convierte en agua)
        new_volume = self.volumen + (ice_mass / self.density)
        
        # Actualizar propiedades
        self.volumen = new_volume
        self.temperature = new_temp
        
        return {
            "new_temperature": new_temp,
            "new_volume": new_volume,
            "energy_absorbed": total_energy_required
        }
