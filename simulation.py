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
        
    def simulate_without_heat_loss(self, time_points):
        """
        Simula el calentamiento del fluido sin considerar pérdida de calor al ambiente.
        
        Args:
            time_points: Array de puntos de tiempo para la simulación (en segundos)
            
        Returns:
            Temperaturas del fluido en cada punto de tiempo
        """
        fluid_temperatures = []
        initial_temp = self.container.fluido.temperature
        
        for t in time_points:
            # Cálculo de temperatura sin considerar pérdida de calor
            # Usa la fuente de poder para calentar el contenedor
            temp = self.power_source.connect_container(self.container, t)
            fluid_temperatures.append(temp)
            
        # Restaurar temperatura inicial
        self.container.fluido.temperature = initial_temp
        
        return fluid_temperatures
        
    def simulate_with_heat_loss(self, time_points, ambient_temp=25, heat_loss_coeff=0.001):
        """
        Simula el calentamiento del fluido considerando pérdida de calor al ambiente.
        
        Args:
            time_points: Array de puntos de tiempo para la simulación (en segundos)
            ambient_temp: Temperatura ambiente (°C)
            heat_loss_coeff: Coeficiente de pérdida de calor
            
        Returns:
            Temperaturas del fluido en cada punto de tiempo
        """
        fluid_temperatures = []
        initial_temp = self.container.fluido.temperature
        current_temp = initial_temp
        
        # Para el primer punto de tiempo, usar temperatura inicial
        if len(time_points) > 0:
            fluid_temperatures.append(current_temp)
            
        # Para cada intervalo de tiempo, calcular la nueva temperatura
        for i in range(1, len(time_points)):
            dt = time_points[i] - time_points[i-1]
            
            # Calor ganado por la fuente de poder
            self.container.fluido.temperature = current_temp
            heated_temp = self.power_source.connect_container(self.container, dt)
            heat_gain = heated_temp - current_temp
            
            # Pérdida de calor al ambiente (Ley de enfriamiento de Newton)
            heat_loss = heat_loss_coeff * dt * (current_temp - ambient_temp)
            
            # Nueva temperatura considerando ganancia y pérdida
            current_temp = current_temp + heat_gain - heat_loss
            fluid_temperatures.append(current_temp)
            
        # Restaurar temperatura inicial
        self.container.fluido.temperature = initial_temp
        
        return fluid_temperatures
    
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
        # Usar el método sin pérdida de calor
        fluid_temperatures = self.simulate_without_heat_loss(time_points)
        
        return {
            'times': time_points,
            'fluid_temperatures': fluid_temperatures,
            'container_name': self.container.material.name,
            'fluid_name': self.container.fluido.name
        }
