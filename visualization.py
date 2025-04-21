import numpy as np
import matplotlib.pyplot as plt

class Visualization:
    """
    Clase para visualizar los resultados de simulaciones de calentamiento.
    
    Attributes:
        results: Resultados de la simulación a visualizar
    """
    
    def __init__(self, results):
        """
        Inicializa la visualización con los resultados de una simulación
        
        Args:
            results: Diccionario con los resultados de la simulación
        """
        self.results = results
        
    def plot_fluid_temperature_evolution(self, title=None, save_path=None):
        """
        Genera un gráfico de la evolución de temperatura del fluido en el tiempo
        
        Args:
            title: Título opcional para el gráfico
            save_path: Ruta opcional para guardar el gráfico como imagen
        """
        times = self.results['times']
        temperatures = self.results['fluid_temperatures']
        
        plt.figure(figsize=(10, 6))
        plt.plot(times, temperatures, 'r-o')
        
        if title:
            plt.title(title)
        else:
            plt.title('Evolución de la temperatura del fluido')
            
        plt.xlabel('Tiempo (segundos)')
        plt.ylabel('Temperatura (°C)')
        plt.grid(True)
        plt.xticks(times)
        
        # Añadir la temperatura en cada punto
        for i, (x, y) in enumerate(zip(times, temperatures)):
            plt.annotate(f'{y:.1f}°C', (x, y), textcoords="offset points", 
                         xytext=(0,10), ha='center')
        
        if save_path:
            plt.savefig(save_path)
            
        plt.tight_layout()
        plt.show()
