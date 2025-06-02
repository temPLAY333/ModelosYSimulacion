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
    
    def _get_colors_for_simulation(self, simulation_results, param_name):
        """
        Obtiene colores apropiados para las simulaciones, con lógica especial para TP5E
        
        Args:
            simulation_results: Lista de resultados de simulaciones
            param_name: Nombre del parámetro que varía
            
        Returns:
            list: Lista de colores para cada simulación
        """
        # Para TP5E, usar colores familiares
        if param_name == 'name' and any('simulation_type' in result for result in simulation_results):
            return self._get_tp5e_colors(simulation_results)
        
        # Para otros casos, usar paleta viridis
        return plt.cm.viridis(np.linspace(0, 1, len(simulation_results)))
    
    def _get_tp5e_colors(self, simulation_results):
        """
        Obtiene colores específicos para TP5E con familias de curvas
        
        Args:
            simulation_results: Lista de resultados de simulaciones
            
        Returns:
            list: Lista de colores para cada simulación
        """
        colors = []
        
        # Definir paletas de colores para cada familia
        color_families = {
            'base': '#000000',           # Negro para curva base
            'initial_temp': {            # Rojos para temperatura inicial
                'light': '#FF6B6B',      # Rojo claro (menor temperatura)
                'dark': '#CC1F1F'        # Rojo oscuro (mayor temperatura)
            },
            'ambient_temp': {            # Azules para temperatura ambiente
                'light': '#4ECDC4',      # Azul-verde claro (menor temperatura)
                'dark': '#1A5490'        # Azul oscuro (mayor temperatura)
            },
            'thickness': {               # Verdes para grosor
                'light': '#95E1A3',      # Verde claro (menor grosor)
                'dark': '#2D5016'        # Verde oscuro (mayor grosor)
            },
            'power': {                   # Naranjas para potencia
                'light': '#FFB347',      # Naranja claro (menor potencia)
                'dark': '#FF8C00'        # Naranja oscuro (mayor potencia)
            }
        }
        
        # Asignar colores
        for i, result in enumerate(simulation_results):
            sim_type = result.get('simulation_type', 'unknown')
            
            if sim_type == 'base':
                colors.append(color_families['base'])
            elif sim_type in color_families and isinstance(color_families[sim_type], dict):
                # Para familias con variaciones, determinar si es valor alto o bajo
                if sim_type == 'initial_temp':
                    temp = result.get('initial_temperature', 20)
                    # Comparar con base (20°C)
                    if temp < 20:
                        colors.append(color_families[sim_type]['light'])
                    else:
                        colors.append(color_families[sim_type]['dark'])
                elif sim_type == 'ambient_temp':
                    temp = result.get('ambient_temperature', 20)
                    # Comparar con base (20°C)
                    if temp < 20:
                        colors.append(color_families[sim_type]['light'])
                    else:
                        colors.append(color_families[sim_type]['dark'])
                elif sim_type == 'thickness':
                    thickness = result.get('wall_thickness_mm', 2.0)
                    # Comparar con base (2.0mm)
                    if thickness < 2.0:
                        colors.append(color_families[sim_type]['light'])
                    else:
                        colors.append(color_families[sim_type]['dark'])
                elif sim_type == 'power':
                    power = result.get('power', 1000)
                    # Comparar con base (1000W)
                    if power < 1000:
                        colors.append(color_families[sim_type]['light'])
                    else:
                        colors.append(color_families[sim_type]['dark'])
                else:
                    colors.append('#888888')  # Gris por defecto
            else:
                colors.append('#888888')  # Gris por defecto
        
        return colors
    
    def _get_tp5e_label(self, result):
        """
        Genera etiquetas específicas para TP5E mostrando el parámetro que difiere de la curva base
        
        Args:
            result: Resultado de simulación con datos de TP5E
            
        Returns:
            str: Etiqueta descriptiva para la leyenda
        """
        sim_type = result.get('simulation_type', 'unknown')
        
        if sim_type == 'base':
            return 'Curva Base'
        elif sim_type == 'initial_temp':
            temp = result.get('initial_temperature', 20)
            return f'T. inicial {temp:.0f}°C'
        elif sim_type == 'ambient_temp':
            temp = result.get('ambient_temperature', 20)
            return f'T. ambiente {temp:.0f}°C'
        elif sim_type == 'thickness':
            thickness = result.get('wall_thickness_mm', 2.0)
            return f'Grosor {thickness:.1f}mm'
        elif sim_type == 'power':
            power = result.get('power', 1000)
            return f'Potencia {power:.0f}W'
        else:
            return result.get('name', 'Desconocido')
    
    def _get_colors_for_simulation(self, simulation_results, param_name):
        """
        Obtiene colores apropiados para las simulaciones, con lógica especial para TP5E
        
        Args:
            simulation_results: Lista de resultados de simulaciones
            param_name: Nombre del parámetro que varía
            
        Returns:
            list: Lista de colores para cada simulación
        """
        # Para TP5E, usar colores familiares
        if param_name == 'name' and any('simulation_type' in result for result in simulation_results):
            return self._get_tp5e_colors(simulation_results)
        
        # Para otros casos, usar paleta viridis
        return plt.cm.viridis(np.linspace(0, 1, len(simulation_results)))
    
    def _get_tp5e_colors(self, simulation_results):
        """
        Obtiene colores específicos para TP5E con familias de curvas
        
        Args:
            simulation_results: Lista de resultados de simulaciones
            
        Returns:
            list: Lista de colores para cada simulación
        """
        colors = []
        
        # Definir paletas de colores para cada familia
        color_families = {
            'base': '#000000',           # Negro para curva base
            'initial_temp': {            # Rojos para temperatura inicial
                'light': '#FF6B6B',      # Rojo claro (menor temperatura)
                'dark': '#CC1F1F'        # Rojo oscuro (mayor temperatura)
            },
            'ambient_temp': {            # Azules para temperatura ambiente
                'light': '#4ECDC4',      # Azul-verde claro (menor temperatura)
                'dark': '#1A5490'        # Azul oscuro (mayor temperatura)
            },
            'thickness': {               # Verdes para grosor
                'light': '#95E1A3',      # Verde claro (menor grosor)
                'dark': '#2D5016'        # Verde oscuro (mayor grosor)
            },
            'power': {                   # Naranjas para potencia
                'light': '#FFB347',      # Naranja claro (menor potencia)
                'dark': '#FF8C00'        # Naranja oscuro (mayor potencia)
            }
        }
        
        # Agrupar simulaciones por tipo
        type_groups = {}
        for i, result in enumerate(simulation_results):
            sim_type = result.get('simulation_type', 'unknown')
            if sim_type not in type_groups:
                type_groups[sim_type] = []
            type_groups[sim_type].append((i, result))
        
        # Asignar colores
        for i, result in enumerate(simulation_results):
            sim_type = result.get('simulation_type', 'unknown')
            
            if sim_type == 'base':
                colors.append(color_families['base'])
            elif sim_type in color_families and isinstance(color_families[sim_type], dict):
                # Para familias con variaciones, determinar si es valor alto o bajo
                if sim_type == 'initial_temp':
                    temp = result.get('initial_temperature', 20)
                    # Comparar con base (20°C)
                    if temp < 20:
                        colors.append(color_families[sim_type]['light'])
                    else:
                        colors.append(color_families[sim_type]['dark'])
                elif sim_type == 'ambient_temp':
                    temp = result.get('ambient_temperature', 20)
                    # Comparar con base (20°C)
                    if temp < 20:
                        colors.append(color_families[sim_type]['light'])
                    else:
                        colors.append(color_families[sim_type]['dark'])
                elif sim_type == 'thickness':
                    thickness = result.get('wall_thickness_mm', 2.0)
                    # Comparar con base (2.0mm)
                    if thickness < 2.0:
                        colors.append(color_families[sim_type]['light'])
                    else:
                        colors.append(color_families[sim_type]['dark'])
                elif sim_type == 'power':
                    power = result.get('power', 1000)
                    # Comparar con base (1000W)
                    if power < 1000:
                        colors.append(color_families[sim_type]['light'])
                    else:
                        colors.append(color_families[sim_type]['dark'])
                else:
                    colors.append('#888888')  # Gris por defecto
            else:
                colors.append('#888888')  # Gris por defecto
        
        return colors
        
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
        
        # Sistema de colores especializado para TP5E o paleta general
        colors = self._get_colors_for_simulation(simulation_results, param_name)
        
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
              # Formatear valor para la leyenda basado en el parámetro que varía
            if param_name == 'name' and 'simulation_type' in result:
                # Para TP5E, mostrar el parámetro específico que difiere de la curva base
                label_value = self._get_tp5e_label(result)
            elif param_name == 'wall_thickness_mm' and 'thickness' in result:
                # Para distribución de grosores, mostrar el valor en mm
                label_value = f"{result['thickness']:.1f}mm"
            elif param_name == 'initial_temperature' and 'initial_temperature' in result:
                # Para distribución de temperaturas iniciales
                label_value = f"{result['initial_temperature']:.1f}°C"
            elif param_name == 'ambient_temperature' and 'ambient_temperature' in result:
                # Para distribución de temperaturas ambiente
                label_value = f"{result['ambient_temperature']:.1f}°C"
            elif param_name == 'voltage' and 'voltage' in result:
                # Para distribución de tensiones
                label_value = f"{result['voltage']:.1f}V"
            elif param_name == 'combination' and 'combination' in result:
                # Para combinaciones múltiples, usar el número de combinación
                label_value = f"Comb. {result['combination']}"
            else:
                # Fallback para casos no especificados
                simulation_id = result.get('simulation_id', i + 1)
                label_value = f"Simulación {simulation_id}"

            plt.plot(times, temperatures, '-', color=colors[i], 
                    linewidth=2, label=label_value)
        
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