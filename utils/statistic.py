import numpy as np
from core.container import Container
from core.power_source import PowerSource
from simulation.simulation import Simulation
from typing import List, Dict, Any

class Statistic:
    """
    Clase para generar distribuciones estadísticas y ejecutar simulaciones con ellas.
    
    Esta clase permite crear conjuntos de parámetros siguiendo distribuciones
    uniformes o normales, y ejecutar múltiples simulaciones para analizar
    el comportamiento del sistema bajo diferentes valores de entrada.
    """
    
    def __init__(self):
        """
        Inicializa la clase de estadísticas
        """
        self.simulation_results = []
        self.parameters = {}
    
    def generate_uniform_distribution(self, param_name: str, min_value: float, 
                                    max_value: float, count: int) -> List[float]:
        """
        Genera una distribución uniforme de valores para un parámetro
        
        Args:
            param_name: Nombre del parámetro
            min_value: Valor mínimo
            max_value: Valor máximo
            count: Número de valores a generar
        
        Returns:
            Lista de valores distribuidos uniformemente
        """
        values = np.random.uniform(min_value, max_value, count)
        self.parameters[param_name] = values
        return values
    
    def generate_normal_distribution(self, param_name: str, mean: float, 
                                   std_dev: float, count: int) -> List[float]:
        """
        Genera una distribución normal de valores para un parámetro
        
        Args:
            param_name: Nombre del parámetro
            mean: Media de la distribución
            std_dev: Desviación estándar
            count: Número de valores a generar
        
        Returns:
            Lista de valores distribuidos normalmente
        """
        values = np.random.normal(mean, std_dev, count)
        self.parameters[param_name] = values
        return values
    
    def run_simulations_with_uniform_resistances(self, simulation: Simulation, 
                                               container: Container,
                                               min_thickness: float, 
                                               max_thickness: float, 
                                               count: int) -> List[Dict[str, Any]]:
        """
        Ejecuta múltiples simulaciones variando el grosor de la pared del contenedor
        según una distribución uniforme (resistencia térmica).
        
        Args:
            simulation: Objeto de simulación base
            container: Contenedor base a modificar
            min_thickness: Grosor mínimo en metros
            max_thickness: Grosor máximo en metros
            count: Número de simulaciones a ejecutar
        
        Returns:
            Lista con los resultados de cada simulación
        """
        # Generar distribución uniforme de grosores (resistencias)
        thicknesses = self.generate_uniform_distribution('wall_thickness', 
                                                      min_thickness, 
                                                      max_thickness, 
                                                      count)
        
        results = []
        
        # Ejecutar simulación para cada valor de grosor
        for i, thickness in enumerate(thicknesses):
            print(f"Simulación {i+1}/{count}: Grosor de pared = {thickness*1000:.3f} mm")
            
            # Crear una copia del contenedor con el nuevo grosor
            modified_container = Container(
                container.forma,
                container.fluido,
                container.material,
                thickness,  # Aplicar el grosor específico
                container.base_thickness,
                container.base_density
            )
            
            # Configurar la simulación
            current_sim = simulation
            current_sim.container = modified_container
            
            # Ejecutar la simulación
            sim_results = current_sim.simulate()
            
            # Almacenar los resultados con metadatos
            results.append({
                'wall_thickness': thickness,
                'wall_thickness_mm': thickness * 1000,  # Convertir a mm para mejor visualización
                'times': [time for time, _ in sim_results],
                'fluid_temperatures': [temp for _, temp in sim_results]
            })
        
        self.simulation_results = results
        return results

    def get_simulation_results(self):
        """
        Obtiene los resultados de las simulaciones ejecutadas
        
        Returns:
            Lista de resultados de simulaciones
        """
        return self.simulation_results
