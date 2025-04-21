import numpy as np
from typing import List, Dict, Union, Any
from container import Container


class PowerSource:
    """
    Representa una fuente de poder que puede calentar un contenedor
    
    Attributes:
        tension: Tensión aplicada en voltios
        current: Corriente en amperios
        history: Historial de datos para visualización
    """
    
    def __init__(self, tension: float, current: float = 1.0):
        """
        Inicializa una fuente de poder con una tensión específica
        
        Args:
            tension: Tensión de la fuente en voltios
            current: Corriente en amperios (por defecto 1.0)
        """
        self.tension: float = tension
        self.current: float = current
        self.history: List[Dict[str, float]] = []
        
    def connect_container(self, container: Container, time: float) -> float:
        """
        Calcula la temperatura del fluido en el contenedor durante un tiempo específico
        utilizando propiedades físicas de los materiales y fluidos.
        
        Args:
            container: Objeto de tipo Container
            time: Tiempo en segundos de aplicación de la tensión
            
        Returns:
            La temperatura final del fluido en Celsius
        """
        # Cálculo basado en principios físicos de transferencia de calor
        initial_temp = container.fluido.temperature
        
        # Potencia eléctrica en vatios (W)
        power = self.tension * self.current
        
        # Resistencia térmica del material
        thermal_resistance = container.material.get_thermal_resistance_factor(container.wall_thickness)
        
        # Área de superficie para transferencia de calor
        surface_area = container.get_surface_area()
        
        # Capacidad de calor del fluido (J/K)
        heat_capacity = container.fluido.heat_capacity_per_volume() * container.volumen
        
        # Cálculo de la transferencia de calor
        # Suponemos un coeficiente de eficiencia de la transferencia (simplificado)
        efficiency_factor = 0.85
        
        # Potencia efectiva que calienta el fluido
        effective_power = power * efficiency_factor
        
        # Incremento de temperatura (ΔT = Q/mC)
        delta_temp = (effective_power * time) / heat_capacity
        
        # Calcular pérdidas por aislamiento
        thermal_loss_factor = np.exp(-time / (thermal_resistance * heat_capacity))
        delta_temp *= thermal_loss_factor
        
        # Temperatura final
        new_temp = initial_temp + delta_temp
        container.fluido.temperature = new_temp
        
        # Registrar datos para visualización
        self.history.append({
            'time': time,
            'temperature': new_temp,
            'power': power,
            'effective_power': effective_power,
            'heat_loss': power * (1 - thermal_loss_factor)
        })
        
        return new_temp
