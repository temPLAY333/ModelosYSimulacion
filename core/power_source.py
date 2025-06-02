import numpy as np
from typing import List, Dict, Union, Any
from core.container import Container


class PowerSource:
    """
    Representa una fuente de poder que puede calentar un contenedor
    
    Attributes:
        power: Potencia aplicada en vatios
        history: Historial de datos para visualización
    """
    def __init__(self, power: float):
        """
        Inicializa una fuente de poder con una potencia específica
        
        Args:
            power: Potencia de la fuente en vatios
        """        
        self.power: float = power
        self.history: List[Dict[str, float]] = []
        
    def connect_container(self, container: Container, time: float, 
                         current_temperature: float, fluid_volume: float) -> float:
        """
        Calcula la temperatura del fluido en el contenedor durante un tiempo específico
        utilizando propiedades físicas de los materiales y fluidos.
        
        Args:
            container: Objeto de tipo Container
            time: Tiempo en segundos de aplicación de la tensión
            current_temperature: Temperatura actual del fluido en °C
            fluid_volume: Volumen actual del fluido en m³
            
        Returns:
            La temperatura final del fluido en Celsius
        """
        # Cálculo basado en principios físicos de transferencia de calor
        initial_temp = current_temperature
        
        # Resistencia térmica del material
        thermal_resistance = container.material.get_thermal_resistance_factor(container.wall_thickness)
        
        # Área de superficie para transferencia de calor
        surface_area = container.get_surface_area()
        
        # Capacidad de calor del fluido (J/K)
        heat_capacity = container.fluido.heat_capacity_per_volume() * fluid_volume
        
        # Cálculo de la transferencia de calor
        # Suponemos un coeficiente de eficiencia de la transferencia (simplificado)
        efficiency_factor = 0.85
        
        # Potencia efectiva que calienta el fluido
        effective_power = self.power * efficiency_factor
        
        # Incremento de temperatura (ΔT = Q/mC)
        delta_temp = (effective_power * time) / heat_capacity
          # Calcular pérdidas por aislamiento
        thermal_loss_factor = np.exp(-time / (thermal_resistance * heat_capacity))
        delta_temp *= thermal_loss_factor
        
        # Temperatura final
        new_temp = initial_temp + delta_temp
        
        # Registrar datos para visualización
        self.history.append({
            'time': time,
            'temperature': new_temp,
            'power': self.power,
            'effective_power': effective_power,
            'heat_loss': self.power * (1 - thermal_loss_factor)
        })
        
        return new_temp
