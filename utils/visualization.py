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
        
    def plot_distribution_results(self, simulation_results, param_name, title=None, save_path=None, 
                                legend_title=None, x_label="Tiempo (segundos)", y_label="Temperatura (°C)"):
        """
        Visualiza los resultados de múltiples simulaciones con diferentes valores de parámetros
        
        Args:
            simulation_results: Lista de diccionarios con resultados de simulaciones
            param_name: Nombre del parámetro que varía (para leyenda)
            title: Título opcional para el gráfico
            save_path: Ruta opcional para guardar el gráfico
            legend_title: Título para la leyenda
            x_label: Etiqueta para el eje X
            y_label: Etiqueta para el eje Y
        """
        plt.figure(figsize=(12, 7))
        
        # Paleta de colores para diferenciar mejor las líneas
        colors = plt.cm.viridis(np.linspace(0, 1, len(simulation_results)))
        
        # Encontrar límites globales para los ejes
        all_times = []
        all_temps = []
        
        for sim_result in simulation_results:
            all_times.extend(sim_result['times'])
            all_temps.extend(sim_result['fluid_temperatures'])
        
        min_time, max_time = min(all_times), max(all_times)
        min_temp, max_temp = min(all_temps), max(all_temps)
        
        # Graficar cada resultado
        for i, result in enumerate(simulation_results):
            times = result['times']
            temperatures = result['fluid_temperatures']
            param_value = result[param_name]
            
            # Formatear valor para la leyenda
            if isinstance(param_value, float):
                if param_value < 0.1:  # Si es un valor pequeño como grosor en metros
                    label_value = f"{param_value*1000:.2f} mm"
                else:
                    label_value = f"{param_value:.2f}"
            else:
                label_value = str(param_value)
                
            plt.plot(times, temperatures, '-', color=colors[i], 
                    linewidth=2, label=f"{legend_title or param_name}: {label_value}")
        
        # Configurar gráfico
        if title:
            plt.title(title, fontsize=14, fontweight='bold')
        else:
            plt.title(f'Evolución de temperatura para diferentes valores de {param_name}', 
                    fontsize=14, fontweight='bold')
            
        plt.xlabel(x_label, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Leyenda
        plt.legend(loc='best', frameon=True, framealpha=0.95, shadow=True)
        
        # Intervalos para eje X
        if max_time <= 60:
            x_interval = max(1, int(max_time / 6))
        elif max_time <= 300:
            x_interval = 30
        elif max_time <= 1800:
            x_interval = 60
        else:
            x_interval = max(1, int(max_time / 10))
        
        x_ticks = np.arange(0, max_time + x_interval, x_interval)
        plt.xticks(x_ticks)
        
        # Intervalos para eje Y
        temp_range = max_temp - min_temp
        
        if temp_range <= 5:
            y_interval = 0.5
        elif temp_range <= 20:
            y_interval = 2
        elif temp_range <= 50:
            y_interval = 5
        else:
            y_interval = 10
            
        y_min = (min_temp // y_interval) * y_interval
        y_max = ((max_temp // y_interval) + 1) * y_interval
        y_ticks = np.arange(y_min, y_max + y_interval, y_interval)
        plt.yticks(y_ticks)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.tight_layout()
        plt.show()