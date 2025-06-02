from dataclasses import dataclass


class Fluid:
    """
    Representa un tipo de fluido con propiedades físicas específicas.
    Esta clase define las características intrínsecas del fluido (agua, aceite, etc.)
    sin información contextual como temperatura o volumen específico.
    
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
                 viscosity: float = 0.0, 
                 thermal_conductivity: float = 0.0):
        """
        Inicializa un tipo de fluido con sus propiedades físicas intrínsecas.
        
        Args:
            name: Nombre del fluido (ej: "agua", "aceite", "alcohol")
            specific_heat: Calor específico en J/(kg·K)
            density: Densidad en kg/m³
            viscosity: Viscosidad en Pa·s (opcional)
            thermal_conductivity: Conductividad térmica en W/(m·K) (opcional)
        """
        self.name = name
        self.specific_heat = specific_heat
        self.density = density
        self.viscosity = viscosity
        self.thermal_conductivity = thermal_conductivity
    
    def heat_capacity_per_volume(self) -> float:
        """
        Calcula la capacidad calorífica volumétrica
        
        Returns:
            Capacidad calorífica volumétrica en J/(m³·K)
        """
        return self.specific_heat * self.density

    def calculate_ice_addition_effects(self, current_temp, current_volume, ice_mass, ice_temp=-5.0):
        """
        Calcula los efectos de añadir hielo al fluido (sin modificar el estado del fluido).

        Args:
            current_temp (float): Temperatura actual del fluido en °C
            current_volume (float): Volumen actual del fluido en m³
            ice_mass (float): Masa del hielo en kg
            ice_temp (float): Temperatura del hielo en °C (por defecto: -5°C)
            
        Returns:
            dict: Información sobre la nueva temperatura, volumen y energía absorbida
        """
        # Constantes físicas
        latent_heat_fusion = 334000.0  # J/kg (calor latente de fusión del hielo)
        ice_specific_heat = 2108.0     # J/(kg·°C) (calor específico del hielo)
        
        # Calcular masa actual del fluido
        fluid_mass = self.density * current_volume
        
        # Energía para calentar el hielo hasta 0°C
        energy_to_heat_ice = ice_mass * ice_specific_heat * (0 - ice_temp)
        
        # Energía para derretir el hielo (cambio de fase)
        energy_to_melt_ice = ice_mass * latent_heat_fusion
        
        # Energía total extraída del fluido
        total_energy_required = energy_to_heat_ice + energy_to_melt_ice
        
        # Cambio de temperatura en el fluido original
        temp_change = total_energy_required / (fluid_mass * self.specific_heat)
        new_temp = current_temp - temp_change
        
        # Nuevo volumen (el hielo se convierte en agua)
        new_volume = current_volume + (ice_mass / self.density)
        
        return {
            "new_temperature": new_temp,
            "new_volume": new_volume,
            "energy_absorbed": total_energy_required
        }
