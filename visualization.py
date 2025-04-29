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
        plt.plot(times, temperatures, 'r-')  # Cambiado de 'r-o' a 'r-' para mostrar solo línea continua
        
        if title:
            plt.title(title)
        else:
            plt.title('Evolución de la temperatura del fluido')
            
        plt.xlabel('Tiempo (segundos)')
        plt.ylabel('Temperatura (°C)')
        plt.grid(True)
        
        # Definir intervalos adecuados para el eje X (tiempo)
        max_time = max(times)
        if max_time <= 60:  # Si el tiempo máximo es menor a un minuto
            x_interval = max(1, max_time // 10)  # Al menos 10 divisiones o cada segundo
        elif max_time <= 360:  # Si es menor a 5 minutos
            x_interval = 30  # Cada 30 segundos
        elif max_time <= 1800:  # Si es menor a 30 minutos
            x_interval = 60  # Cada minuto
        elif max_time <= 3600:  # Si es menor a una hora
            x_interval = 300  # Cada 5 minutos
        else:  # Para tiempos más largos
            x_interval = 3600  # Cada hora
        
        x_ticks = np.arange(0, max_time + x_interval, x_interval)
        plt.xticks(x_ticks)
        
        # Definir intervalos adecuados para el eje Y (temperatura)
        min_temp = min(temperatures)
        max_temp = max(temperatures)
        temp_range = max_temp - min_temp
        
        if temp_range <= 5:
            y_interval = 0.5
        elif temp_range <= 20:
            y_interval = 2
        elif temp_range <= 50:
            y_interval = 5
        else:
            y_interval = 10
            
        # Calcular límites para el eje Y que sean múltiplos del intervalo
        y_min = (min_temp // y_interval) * y_interval
        y_max = ((max_temp // y_interval) + 1) * y_interval
        y_ticks = np.arange(y_min, y_max + y_interval, y_interval)
        plt.yticks(y_ticks)
        
        # Nota: Se eliminaron las anotaciones de temperatura para mostrar solo la línea
        
        if save_path:
            plt.savefig(save_path)
        
        plt.tight_layout()
        plt.show()