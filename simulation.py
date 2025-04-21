import numpy as np
from container import Container
from power_source import PowerSource

class Simulation:
    """
    Clase para simular el calentamiento de un fluido en un contenedor
    usando una fuente de poder específica.
    
    Attributes:
        container: Contenedor con el fluido a calentar
        power_source: Fuente de poder para calentar el contenedor
    """
    
    def __init__(self, container: Container, power_source: PowerSource):
        """
        Inicializa la simulación con un contenedor y una fuente de poder
        
        Args:
            container: Contenedor con fluido y material definidos
            power_source: Fuente de poder con especificaciones eléctricas
        """
        self.container = container
        self.power_source = power_source
        
    def run_simulation(self, time_points):
        """
        Ejecuta la simulación de calentamiento para los tiempos especificados
        
        Args:
            time_points: Array de puntos de tiempo para la simulación (en segundos)
            
        Returns:
            Dictionary con los resultados de la simulación:
                'times': Tiempos simulados
                'fluid_temperatures': Temperaturas del fluido en cada tiempo
                'container_name': Nombre del contenedor
                'fluid_name': Nombre del fluido
        """
        fluid_temperatures = []
        
        # Guardar temperatura inicial
        initial_temp = self.container.fluido.temperature
        
        # Para cada punto de tiempo, calcular la temperatura
        for t in time_points:
            # Conectar la fuente de poder al contenedor durante ese tiempo
            temp = self.power_source.connect_container(self.container, t)
            fluid_temperatures.append(temp)
            
        # Restaurar la temperatura inicial del contenedor para futuros usos
        self.container.fluido.temperature = initial_temp
        
        return {
            'times': time_points,
            'fluid_temperatures': fluid_temperatures,
            'container_name': self.container.material.name,
            'fluid_name': self.container.fluido.name
        }
