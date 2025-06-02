import numpy as np
from core.fluid import Fluid
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
        """        # Generar distribución uniforme de grosores (resistencias)
        thicknesses = self.generate_uniform_distribution('wall_thickness', 
                                                      min_thickness, 
                                                      max_thickness, 
                                                      count)
        
        # Ordenar los grosores de menor a mayor para presentación ordenada
        thicknesses_sorted = sorted(thicknesses)
        
        results = []
        
        # Ejecutar simulación para cada valor de grosor ordenado
        for i, thickness in enumerate(thicknesses_sorted):
            print(f"Simulación {i+1}/{count}: Grosor = {thickness*1000:.3f} mm")
            
            # Crear una copia del fluido para evitar referencias compartidas
            new_fluid = Fluid(
                name=container.fluido.name,
                density=container.fluido.density,
                specific_heat=container.fluido.specific_heat,
                viscosity=container.fluido.viscosity,
                thermal_conductivity=container.fluido.thermal_conductivity
            )
            
            # Crear una copia del contenedor con el nuevo grosor y fluido independiente
            modified_container = Container(
                container.forma,
                new_fluid,  # Usar el fluido independiente
                container.material,
                thickness,  # Aplicar el grosor específico del contenedor
                container.base_density
            )
            
            # Configurar la simulación con un nuevo objeto
            current_sim = Simulation(modified_container, simulation.power_source,
                                   initial_temperature=20.0,  # Use consistent initial temperature
                                   fluid_volume=modified_container.get_standard_fluid_volume())  # Use standard volume for new container
            
            current_sim.configure_simulation(
                target_temp=simulation.target_temp,
                ambient_temp=simulation.ambient_temp,
                time_step=1,
                include_heat_loss=True,  # Incluir pérdida de calor
                correction_factor=simulation.correction_factor
            )
            
            # Ejecutar la simulación
            sim_results = current_sim.simulate(logs=False)
            
            # Calcular estadísticas adicionales para verificar diferencias
            final_temp = sim_results[-1][1] if sim_results else 0
            time_to_target = None
            for time, temp in sim_results:
                if temp >= simulation.target_temp * 0.95:  # 95% del objetivo
                    time_to_target = time
                    break
            
            # Almacenar los resultados con metadatos
            results.append({
                'simulation_id': i + 1,
                'thickness': thickness*1000,  # Grosor en mm
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
    
    def analyze_simulation_variance(self) -> Dict[str, Any]:
        """
        Analiza la varianza en los resultados de las simulaciones para verificar
        que están produciendo resultados diferentes.
        
        Returns:
            Diccionario con estadísticas de varianza
        """
        if not self.simulation_results:
            return {"error": "No hay resultados de simulaciones para analizar"}
        
        # Extraer métricas clave
        final_temps = [result['final_temperature'] for result in self.simulation_results]
        times_to_target = [result['time_to_target'] for result in self.simulation_results if result['time_to_target'] is not None]
        wall_thicknesses = [result['wall_thickness_mm'] for result in self.simulation_results]
        thermal_conductances = [result['thermal_conductance'] for result in self.simulation_results]
        
        # Calcular estadísticas
        analysis = {
            'num_simulations': len(self.simulation_results),
            'wall_thickness': {
                'min_mm': min(wall_thicknesses),
                'max_mm': max(wall_thicknesses),
                'range_mm': max(wall_thicknesses) - min(wall_thicknesses),
                'std_dev_mm': np.std(wall_thicknesses)
            },
            'thermal_conductance': {
                'min': min(thermal_conductances),
                'max': max(thermal_conductances),
                'range': max(thermal_conductances) - min(thermal_conductances),
                'std_dev': np.std(thermal_conductances)
            },
            'final_temperature': {
                'min_celsius': min(final_temps),
                'max_celsius': max(final_temps),
                'range_celsius': max(final_temps) - min(final_temps),
                'std_dev_celsius': np.std(final_temps),
                'mean_celsius': np.mean(final_temps)
            }
        }
        
        if times_to_target:
            analysis['time_to_target'] = {
                'min_seconds': min(times_to_target),
                'max_seconds': max(times_to_target),
                'range_seconds': max(times_to_target) - min(times_to_target),
                'std_dev_seconds': np.std(times_to_target),
                'mean_seconds': np.mean(times_to_target)
            }
        
        # Verificar si hay variación significativa
        temp_variation = analysis['final_temperature']['std_dev_celsius'] > 0.1  # Más de 0.1°C de desviación
        thickness_variation = analysis['wall_thickness']['std_dev_mm'] > 0.01  # Más de 0.01mm de desviación
        
        analysis['has_significant_variation'] = temp_variation and thickness_variation
        analysis['variation_summary'] = f"Temp std: {analysis['final_temperature']['std_dev_celsius']:.3f}°C, Thickness std: {analysis['wall_thickness']['std_dev_mm']:.3f}mm"
        
        return analysis
