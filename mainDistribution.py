"""
Programa principal para generar distribuciones estadísticas según el TP5.

Este script permite al usuario seleccionar entre diferentes tipos de distribuciones
para generar familias de curvas con parámetros variables.
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from core.container import Container
from core.shape import CylindricalShape, create_shape
from core.fluid import Fluid
from core.material import Material
from core.power_source import PowerSource
from simulation.simulation import Simulation
from utils.visualization import Visualization
from utils.statistic import Statistic

def crear_objetos_base():
    """
    Crea y devuelve los objetos base necesarios para las simulaciones.
    
    Returns:
        tuple: (container, power_source, simulation)
    """
    # Crear forma cilíndrica
    radius = 0.1  # 10 cm
    height = 0.15  # 15 cm
    shape = CylindricalShape(radius, height)
      # Crear fluido (agua)
    water = Fluid(name="water", density=1000, specific_heat=4186)  # Just the intrinsic properties
    
    # Crear material (acero)
    steel = Material(name="steel", thermal_conductivity=15, specific_heat=502.0, density=7900.0)  # Acero

    # Crear contenedor base
    base_density = 7800  # kg/m³ (acero)
    container = Container(shape, water, steel, 0.002, base_density)
    
    # Crear fuente de poder
    power = 1000  # 1000W (1kW)
    power_source = PowerSource(power)    # Crear la simulación base con temperatura inicial y volumen estándar
    simulation = Simulation(container, power_source,
                          initial_temperature=20.0,  # 20°C initial temp
                          fluid_volume=container.get_standard_fluid_volume())  # 2/3 of container volume
    
    simulation.configure_simulation(
        target_temp=60,      # Calentar hasta 60°C
        ambient_temp=20,     # Temperatura ambiente 20°C
        time_step=1.0,       # Paso de tiempo de 1 segundo
        include_heat_loss=True,
        correction_factor=1.0
    )
    
    return container, power_source, simulation

def distribucion_uniforme_resistencias():
    """
    TP 5.A: Distribución uniforme de 5 valores próximos de resistencias.
    """
    print("\nTP 5.A: Distribución uniforme de 5 valores próximos de resistencias")
    print("="*70)
    
    # Crear objetos base
    container, power_source, simulation = crear_objetos_base()

    # Crear objeto para estadísticas
    stats = Statistic()
    
    # Obtener parámetros del usuario para la distribución
    print("\nParámetros para la distribución uniforme de resistencias (grosor de pared):")

    while True:
        try:
            user_input = input("Ingrese el grosor mínimo en mm (recomendado 0.8): ")
            if user_input.strip() == "":
                min_thickness = 0.8  # Default value
            else:
                min_thickness = float(user_input)
            if min_thickness <= 0:
                print("El grosor debe ser un valor positivo.")
                continue
            min_thickness = min_thickness / 1000  # Convertir a metros
            break
        except ValueError:
            print("Por favor ingrese un número válido.")

    while True:
        try:
            user_input = input("Ingrese el grosor máximo en mm (recomendado 5.0): ")
            if user_input.strip() == "":
                max_thickness = 5.0  # Default value
            else:
                max_thickness = float(user_input)
            if max_thickness <= min_thickness * 1000:
                print(f"El grosor máximo debe ser mayor que el mínimo ({min_thickness*1000} mm).")
                continue
            max_thickness = max_thickness / 1000  # Convertir a metros
            break
        except ValueError:
            print("Por favor ingrese un número válido.")

    num_simulations = 5  # Fijo en 5 según el enunciado del TP

    # Ejecutar simulaciones con distribución uniforme de resistencias (grosores)
    print(f"\nEjecutando {num_simulations} simulaciones con diferentes grosores de pared...\n")

    # Ejecutar las simulaciones
    results = stats.run_simulations_with_uniform_resistances(
        simulation, 
        container,
        min_thickness, 
        max_thickness, 
        num_simulations
    )

    # Crear directorio para guardar resultados si no existe
    os.makedirs("results/images", exist_ok=True)    # Mostrar resultados en formato tabular
    print("\nResultados de las simulaciones (temperaturas en °C):")
    print("="*70)
    print("Tiempo (s)\t" + "\t".join([f"Sim {i+1}" for i in range(num_simulations)]))
    
    # Encontrar la longitud mínima de todas las simulaciones para evitar errores de índice
    min_length = min(len(result['times']) for result in results)
    
    for i in range(0, min_length, 10):  # Mostrar cada 10 segundos
        # Verificar que el índice esté dentro del rango para todas las simulaciones
        if i < min_length:
            row = [f"{results[0]['times'][i]:.1f}"]
            for j in range(num_simulations):
                if i < len(results[j]['fluid_temperatures']):
                    row.append(f"{results[j]['fluid_temperatures'][i]:.2f}")
                else:
                    row.append("N/A")  # Si no hay datos para esta simulación en este tiempo
            print("\t".join(row))

    # Verificar que las simulaciones generen diferentes resultados
    unique_temperatures = any(
        results[i]['fluid_temperatures'] != results[j]['fluid_temperatures']
        for i in range(num_simulations) for j in range(i + 1, num_simulations)
    )
    if not unique_temperatures:
        print("\nAdvertencia: Todas las simulaciones generaron los mismos resultados. Verifique los parámetros de entrada.")

    # Visualizar los resultados
    print("\nGenerando visualización de resultados...")
    viz = Visualization({})  # Inicializamos con un diccionario vacío

    # Crear y mostrar el gráfico
    viz.plot_distribution_results(
        results, 
        'wall_thickness_mm',  # Usamos los valores en mm para mejor legibilidad
        title='TP 5.A: Efecto de la resistencia térmica en el calentamiento del fluido',
        save_path='results/images/tp5a_resistencias.png',
        legend_title='Grosor de pared',
        x_label='Tiempo (segundos)',
        y_label='Temperatura (°C)'
    )

    print(f"\nResultados guardados en 'results/images/tp5a_resistencias.png'")

    # Mostrar estadísticas
    mostrar_estadisticas_resistencias(results)

    input("\nPresione Enter para volver al menú principal...")

def distribucion_normal_temperaturas_iniciales():
    """
    TP 5.B: Distribución normal de 5 temperaturas iniciales del agua. 
    Media 10, desvío standard=5
    """
    print("\nTP 5.B: Distribución normal de temperaturas iniciales del agua")
    print("="*70)
    
    # Crear objetos base
    container, power_source, simulation = crear_objetos_base()
    
    # Crear objeto para estadísticas
    stats = Statistic()
    
    # Obtener parámetros del usuario para la distribución
    print("\nParámetros para la distribución normal de temperaturas iniciales:")
    
    # Según el enunciado del TP, la media es 10 y la desviación estándar es 5
    mean_temp = 10
    std_dev = 5
    count = 5  # Fijo en 5 según el enunciado del TP
    
    print(f"Media: {mean_temp}°C")
    print(f"Desviación estándar: {std_dev}°C")
    print(f"Número de valores: {count}")
    
    # Generar los valores de temperatura usando el método de la clase Statistic
    initial_temps = stats.generate_normal_distribution('initial_temperature', mean_temp, std_dev, count)
    print(f"\nTemperaturas iniciales generadas: {[f'{temp:.1f}°C' for temp in initial_temps]}")
    
    results = []
    
    # Ejecutar simulación para cada temperatura inicial
    for i, temp in enumerate(initial_temps):
        print(f"\nSimulación {i+1}/{count}: Temperatura inicial = {temp:.1f}°C")
          # Crear un nuevo fluido (solo propiedades intrínsecas)
        water = Fluid(name="water", density=1000, specific_heat=4186)
        
        # Crear nuevo contenedor con el fluido actualizado
        modified_container = Container(
            container.forma,
            water,
            container.material,
            container.thickness,
            container.base_density
        )        # Actualizar la simulación con temperatura inicial específica
        current_sim = Simulation(modified_container, power_source,
                                initial_temperature=temp,  # Usar la temperatura específica
                                fluid_volume=modified_container.get_standard_fluid_volume())  # 2/3 of container volume
        current_sim.configure_simulation(
            target_temp=60,
            ambient_temp=20,
            time_step=1.0,
            include_heat_loss=True,
            correction_factor=1.0
        )
        
        # Ejecutar simulación
        sim_results = current_sim.simulate(logs=False)  # Desactivar logs para evitar ruido
        
        # Almacenar resultados
        results.append({
            'initial_temperature': temp,
            'times': [time for time, _ in sim_results],
            'fluid_temperatures': [temp for _, temp in sim_results]
        })
    
    # Crear directorio para guardar resultados si no existe
    os.makedirs("results/images", exist_ok=True)
    
    # Visualizar resultados
    viz = Visualization({})
    viz.plot_distribution_results(
        results,
        'initial_temperature',
        title='TP 5.B: Efecto de la temperatura inicial en el calentamiento del fluido',
        save_path='results/images/tp5b_temperaturas_iniciales.png',
        legend_title='Temperatura inicial (°C)',
        x_label='Tiempo (segundos)',
        y_label='Temperatura (°C)'
    )
    
    print(f"\nResultados guardados en 'results/images/tp5b_temperaturas_iniciales.png'")
    
    input("\nPresione Enter para volver al menú principal...")

def distribucion_uniforme_temperaturas_ambiente():
    """
    TP 5.C: Distribución uniforme de 5 temperaturas iniciales del ambiente,
    entre -20 y 50 grados.
    """
    print("\nTP 5.C: Distribución uniforme de temperaturas ambiente")
    print("="*70)
    
    # Crear objetos base
    container, power_source, simulation = crear_objetos_base()
    
    # Crear objeto para estadísticas
    stats = Statistic()
    
    # Según el enunciado, rango de -20°C a 50°C y 5 valores
    min_temp = -20
    max_temp = 50
    count = 5
    
    print(f"\nRango de temperatura ambiente: {min_temp}°C a {max_temp}°C")
    print(f"Número de valores: {count}")
    
    # Generar distribución uniforme de temperaturas ambiente
    ambient_temps = stats.generate_uniform_distribution('ambient_temperature', min_temp, max_temp, count)
    print(f"\nTemperaturas ambiente generadas: {[f'{temp:.1f}°C' for temp in ambient_temps]}")
    
    results = []
    
    # Ejecutar simulación para cada temperatura ambiente
    for i, temp in enumerate(ambient_temps):
        print(f"\nSimulación {i+1}/{count}: Temperatura ambiente = {temp:.1f}°C")        # Actualizar la simulación con temperatura ambiente específica
        current_sim = Simulation(container, power_source,
                                initial_temperature=20.0,  # 20°C initial temp
                                fluid_volume=container.get_standard_fluid_volume())  # 2/3 of container volume
        current_sim.configure_simulation(
            target_temp=60,
            ambient_temp=temp,  # Usar la temperatura ambiente específica
            time_step=1.0,
            include_heat_loss=True,
            correction_factor=1.0
        )
        
        # Ejecutar simulación
        sim_results = current_sim.simulate()
        
        # Almacenar resultados
        results.append({
            'ambient_temperature': temp,
            'times': [time for time, _ in sim_results],
            'fluid_temperatures': [temp for _, temp in sim_results]
        })
    
    # Crear directorio para guardar resultados si no existe
    os.makedirs("results/images", exist_ok=True)
    
    # Visualizar resultados
    viz = Visualization({})
    viz.plot_distribution_results(
        results,
        'ambient_temperature',
        title='TP 5.C: Efecto de la temperatura ambiente en el calentamiento del fluido',
        save_path='results/images/tp5c_temperaturas_ambiente.png',
        legend_title='Temperatura ambiente (°C)',
        x_label='Tiempo (segundos)',
        y_label='Temperatura (°C)'
    )
    
    print(f"\nResultados guardados en 'results/images/tp5c_temperaturas_ambiente.png'")
    
    input("\nPresione Enter para volver al menú principal...")

def distribucion_normal_tension_alimentacion():
    """
    TP 5.D: Distribución normal de 5 valores de tensión de alimentación
    Media 12 SD:4 o Media 220, SD 40.
    """
    print("\nTP 5.D: Distribución normal de valores de tensión de alimentación")
    print("="*70)
    
    # Crear objetos base
    container, power_source, simulation = crear_objetos_base()
    
    # Crear objeto para estadísticas
    stats = Statistic()
    
    # Preguntar qué distribución usar
    print("Seleccione la distribución de tensión:")
    print("1. Media 12V, SD 4V (corriente continua)")
    print("2. Media 220V, SD 40V (corriente alterna)")
    
    choice = ""
    while choice not in ["1", "2"]:
        choice = input("Opción (1/2): ")
        if choice not in ["1", "2"]:
            print("Opción no válida. Por favor ingrese 1 o 2.")
    
    # Configurar según la opción
    if choice == "2":
        mean_voltage = 220
        std_dev = 40
        voltage_type = "AC"
    else:
        mean_voltage = 12
        std_dev = 4
        voltage_type = "DC"
    
    # Número fijo de valores según el enunciado
    count = 5
    
    print(f"\nDistribución normal de tensión {voltage_type}:")
    print(f"Media: {mean_voltage}V")
    print(f"Desviación estándar: {std_dev}V")
    print(f"Número de valores: {count}")
    
    # Generar valores de tensión
    voltages = stats.generate_normal_distribution('voltage', mean_voltage, std_dev, count)
    print(f"\nTensiones generadas: {[f'{v:.1f}V' for v in voltages]}")
    
    # Potencia nominal a tensión nominal
    nominal_power = power_source.power
    nominal_voltage = mean_voltage
    
    results = []
    
    # Ejecutar simulación para cada valor de tensión
    for i, voltage in enumerate(voltages):
        print(f"\nSimulación {i+1}/{count}: Tensión = {voltage:.1f}V")
        
        # Calcular el factor de potencia (P ∝ V²)
        power_factor = (voltage / nominal_voltage) ** 2
        
        # Crear fuente de poder con potencia ajustada
        adjusted_power = nominal_power * power_factor
        modified_power_source = PowerSource(adjusted_power)        # Actualizar simulación con potencia específica
        current_sim = Simulation(container, modified_power_source,
                                initial_temperature=20.0,  # 20°C initial temp
                                fluid_volume=container.get_standard_fluid_volume())  # 2/3 of container volume
        current_sim.configure_simulation(
            target_temp=60,
            ambient_temp=20,
            time_step=1.0,
            include_heat_loss=True,
            correction_factor=1.0
        )
        
        # Ejecutar simulación
        sim_results = current_sim.simulate()
        
        # Almacenar resultados
        results.append({
            'voltage': voltage,
            'power': adjusted_power,
            'times': [time for time, _ in sim_results],
            'fluid_temperatures': [temp for _, temp in sim_results]
        })
    
    # Crear directorio para guardar resultados si no existe
    os.makedirs("results/images", exist_ok=True)
    
    # Visualizar resultados
    viz = Visualization({})
    viz.plot_distribution_results(
        results,
        'voltage',
        title=f'TP 5.D: Efecto de la tensión ({voltage_type}) en el calentamiento del fluido',
        save_path='results/images/tp5d_tension_alimentacion.png',
        legend_title='Tensión (V)',
        x_label='Tiempo (segundos)',
        y_label='Temperatura (°C)'
    )
    
    print(f"\nResultados guardados en 'results/images/tp5d_tension_alimentacion.png'")
    
    input("\nPresione Enter para volver al menú principal...")

def simulacion_todas_distribuciones():
    """
    TP 5.E: Simulación con curva base y variaciones sistemáticas de parámetros.
    """
    print("\nTP 5.E: Simulación con curva base y variaciones de parámetros")
    print("="*70)
    
    # Crear objetos base
    container_base, power_source_base, simulation_base = crear_objetos_base()
    
    # Parámetros de la curva base
    base_params = {
        'initial_temperature': 20.0,    # °C
        'ambient_temperature': 20.0,    # °C  
        'wall_thickness': 0.002,        # 2.0 mm
        'voltage': 220.0,               # V (que da 1000W)
        'power': 1000.0                 # W
    }
    
    print(f"\nParámetros de la curva base:")
    print(f"  - Temperatura inicial: {base_params['initial_temperature']}°C")
    print(f"  - Temperatura ambiente: {base_params['ambient_temperature']}°C")
    print(f"  - Grosor de pared: {base_params['wall_thickness']*1000}mm")
    print(f"  - Tensión: {base_params['voltage']}V")
    print(f"  - Potencia: {base_params['power']}W")
    
    # Definir las variaciones a simular
    simulations_config = [
        # Curva base
        {
            'name': 'Curva Base',
            'initial_temp': base_params['initial_temperature'],
            'ambient_temp': base_params['ambient_temperature'],
            'thickness': base_params['wall_thickness'],
            'power': base_params['power']
        },
        # Variaciones de temperatura inicial (10°C y 30°C)
        {
            'name': 'T. inicial 10°C',
            'initial_temp': 10.0,
            'ambient_temp': base_params['ambient_temperature'],
            'thickness': base_params['wall_thickness'],
            'power': base_params['power']
        },
        {
            'name': 'T. inicial 30°C',
            'initial_temp': 30.0,
            'ambient_temp': base_params['ambient_temperature'],
            'thickness': base_params['wall_thickness'],
            'power': base_params['power']
        },
        # Variaciones de temperatura ambiente (10°C y 40°C)
        {
            'name': 'T. ambiente 10°C',
            'initial_temp': base_params['initial_temperature'],
            'ambient_temp': 10.0,
            'thickness': base_params['wall_thickness'],
            'power': base_params['power']
        },
        {
            'name': 'T. ambiente 40°C',
            'initial_temp': base_params['initial_temperature'],
            'ambient_temp': 40.0,
            'thickness': base_params['wall_thickness'],
            'power': base_params['power']
        },
        # Variaciones de grosor (0.8mm y 5.0mm)
        {
            'name': 'Grosor 0.8mm',
            'initial_temp': base_params['initial_temperature'],
            'ambient_temp': base_params['ambient_temperature'],
            'thickness': 0.0008,  # 0.8mm
            'power': base_params['power']
        },
        {
            'name': 'Grosor 5.0mm',
            'initial_temp': base_params['initial_temperature'],
            'ambient_temp': base_params['ambient_temperature'],
            'thickness': 0.005,   # 5.0mm
            'power': base_params['power']
        },
        # Variaciones de potencia (mayor y menor a 1000W)
        {
            'name': 'Potencia 600W',
            'initial_temp': base_params['initial_temperature'],
            'ambient_temp': base_params['ambient_temperature'],
            'thickness': base_params['wall_thickness'],
            'power': 600.0
        },
        {
            'name': 'Potencia 1500W',
            'initial_temp': base_params['initial_temperature'],
            'ambient_temp': base_params['ambient_temperature'],
            'thickness': base_params['wall_thickness'],
            'power': 1500.0
        }
    ]
    
    results = []
    
    # Ejecutar cada simulación
    for i, config in enumerate(simulations_config):
        print(f"\nEjecutando {config['name']}:")
        print(f"  - Temperatura inicial: {config['initial_temp']}°C")
        print(f"  - Temperatura ambiente: {config['ambient_temp']}°C") 
        print(f"  - Grosor de pared: {config['thickness']*1000:.1f}mm")
        print(f"  - Potencia: {config['power']}W")
        
        # Crear fluido (solo propiedades intrínsecas)
        water = Fluid(name="water", density=1000, specific_heat=4186)
        
        # Crear contenedor con grosor específico
        custom_container = Container(
            container_base.forma,
            water,
            container_base.material,
            config['thickness'],
            container_base.base_density
        )
        
        # Crear fuente de poder con potencia específica
        custom_power_source = PowerSource(config['power'])
        
        # Crear simulación con parámetros específicos
        custom_sim = Simulation(custom_container, custom_power_source,
                              initial_temperature=config['initial_temp'],
                              fluid_volume=custom_container.get_standard_fluid_volume())
        
        custom_sim.configure_simulation(
            target_temp=60,
            ambient_temp=config['ambient_temp'],
            time_step=1.0,
            include_heat_loss=True,
            correction_factor=1.0
        )
        
        # Ejecutar simulación
        sim_results = custom_sim.simulate(logs=False)
        
        # Almacenar resultados
        results.append({
            'name': config['name'],
            'simulation_type': get_simulation_type(config, base_params),
            'initial_temperature': config['initial_temp'],
            'ambient_temperature': config['ambient_temp'],
            'wall_thickness_mm': config['thickness'] * 1000,
            'power': config['power'],
            'times': [time for time, _ in sim_results],
            'fluid_temperatures': [temp for _, temp in sim_results]
        })
    
    # Crear directorio para guardar resultados si no existe
    os.makedirs("results/images", exist_ok=True)
    
    # Visualizar resultados
    viz = Visualization({})
    viz.plot_distribution_results(
        results,
        'name',
        title='TP 5.E: Curva base con variaciones sistemáticas de parámetros',
        save_path='results/images/tp5e_curva_base_variaciones.png',
        legend_title='Configuración',
        x_label='Tiempo (segundos)',
        y_label='Temperatura (°C)'
    )
    
    print(f"\nResultados guardados en 'results/images/tp5e_curva_base_variaciones.png'")
    
    # Mostrar estadísticas
    mostrar_estadisticas_curva_base(results)
    
    input("\nPresione Enter para volver al menú principal...")

def get_simulation_type(config, base_params):
    """
    Determina el tipo de simulación basándose en qué parámetro difiere de la curva base
    
    Args:
        config: Configuración de la simulación actual
        base_params: Parámetros de la curva base
        
    Returns:
        str: Tipo de simulación ("base", "initial_temp", "ambient_temp", "thickness", "power")
    """
    if (config['initial_temp'] == base_params['initial_temperature'] and
        config['ambient_temp'] == base_params['ambient_temperature'] and
        config['thickness'] == base_params['wall_thickness'] and
        config['power'] == base_params['power']):
        return "base"
    elif config['initial_temp'] != base_params['initial_temperature']:
        return "initial_temp"
    elif config['ambient_temp'] != base_params['ambient_temperature']:
        return "ambient_temp"
    elif config['thickness'] != base_params['wall_thickness']:
        return "thickness"
    elif config['power'] != base_params['power']:
        return "power"
    else:
        return "unknown"

def mostrar_estadisticas_resistencias(results):
    """
    Muestra estadísticas de los resultados de la distribución de resistencias
    
    Args:
        results: Lista de resultados de simulaciones
    """
    print("\nResumen de valores de resistencia utilizados:")
    print("-" * 60)
    print(f"{'#':<3} {'Grosor (mm)':<15} {'Tiempo hasta 60°C (s)':<25}")
    print("-" * 60)
    
    for i, result in enumerate(results):
        thickness = result['thickness']
        
        # Encontrar el tiempo que tardó en alcanzar la temperatura objetivo
        temp_target = 60
        times = np.array(result['times'])
        temps = np.array(result['fluid_temperatures'])
        
        # Encontrar el índice donde la temperatura supera o iguala el objetivo
        target_indices = np.where(temps >= temp_target)[0]
        if len(target_indices) > 0:
            time_to_target = times[target_indices[0]]
        else:
            time_to_target = "No alcanzado"
        
        print(f"{i+1:<3} {thickness:<15.3f} {time_to_target}")

def mostrar_estadisticas_combinaciones(results):
    """
    Muestra estadísticas de los resultados de las simulaciones combinadas
    
    Args:
        results: Lista de resultados de simulaciones combinadas
    """
    print("\nResumen de combinaciones:")
    print("-" * 100)
    print(f"{'#':<3} {'Grosor (mm)':<12} {'T. Inicial (°C)':<15} {'T. Ambiente (°C)':<16} {'Tensión (V)':<12} {'Tiempo 60°C (s)':<15}")
    print("-" * 100)
    
    for result in results:
        combo = result['combination']
        thickness = result['wall_thickness_mm']
        init_temp = result['initial_temperature']
        ambient_temp = result['ambient_temperature']
        voltage = result['voltage']
        
        # Encontrar el tiempo que tardó en alcanzar la temperatura objetivo
        temp_target = 60
        times = np.array(result['times'])
        temps = np.array(result['fluid_temperatures'])
        
        # Encontrar el índice donde la temperatura supera o iguala el objetivo
        target_indices = np.where(temps >= temp_target)[0]
        if len(target_indices) > 0:
            time_to_target = times[target_indices[0]]
        else:
            time_to_target = "No alcanzado"
        print(f"{combo:<3} {thickness:<12.2f} {init_temp:<15.1f} {ambient_temp:<16.1f} {voltage:<12.1f} {time_to_target}")

def mostrar_estadisticas_curva_base(results):
    """
    Muestra estadísticas detalladas de las simulaciones con curva base y variaciones
    
    Args:
        results: Lista de resultados de simulaciones
    """
    print("\nEstadísticas de simulaciones con curva base:")
    print("=" * 90)
    
    # Buscar la curva base para comparaciones
    base_result = None
    for result in results:
        if "Base" in result['name']:
            base_result = result
            break
    
    if base_result is None:
        print("Error: No se encontró la curva base")
        return
    
    # Calcular tiempo que tardó la curva base en alcanzar 60°C
    temp_target = 60
    base_times = np.array(base_result['times'])
    base_temps = np.array(base_result['fluid_temperatures'])
    base_target_indices = np.where(base_temps >= temp_target)[0]
    if len(base_target_indices) > 0:
        base_time_to_target = base_times[base_target_indices[0]]
        base_final_temp = base_temps[-1]
    else:
        base_time_to_target = None
        base_final_temp = base_temps[-1]
    
    print(f"\nCurva Base (Referencia):")
    print(f"  - Tiempo hasta 60°C: {base_time_to_target:.1f} segundos" if base_time_to_target else "  - No alcanzó 60°C")
    print(f"  - Temperatura final: {base_final_temp:.1f}°C")
    print(f"  - Tiempo total de simulación: {base_times[-1]:.1f} segundos")
    
    print(f"\nComparación de variaciones:")
    print("-" * 90)
    print(f"{'Variación':<25} {'Parámetro':<15} {'Tiempo 60°C (s)':<15} {'Diferencia (%)':<15} {'Temp. Final (°C)':<15}")
    print("-" * 90)
    
    for result in results:
        if "Base" in result['name']:
            continue  # Skip base curve
            
        # Calcular tiempo para alcanzar 60°C
        times = np.array(result['times'])
        temps = np.array(result['fluid_temperatures'])
        target_indices = np.where(temps >= temp_target)[0]
        
        if len(target_indices) > 0:
            time_to_target = times[target_indices[0]]
            time_difference_pct = ((time_to_target - base_time_to_target) / base_time_to_target * 100) if base_time_to_target else 0
        else:
            time_to_target = None
            time_difference_pct = 0
        
        final_temp = temps[-1]
        
        # Determinar qué parámetro cambió
        param_changed = "Desconocido"
        if "inicial" in result['name']:
            param_changed = f"{result['initial_temperature']}°C"
        elif "ambiente" in result['name']:
            param_changed = f"{result['ambient_temperature']}°C"
        elif "Grosor" in result['name']:
            param_changed = f"{result['wall_thickness_mm']:.1f}mm"
        elif "Potencia" in result['name']:
            param_changed = f"{result['power']:.0f}W"
        
        time_str = f"{time_to_target:.1f}" if time_to_target else "No alcanzó"
        diff_str = f"{time_difference_pct:+.1f}%" if time_to_target and base_time_to_target else "N/A"
        
        print(f"{result['name']:<25} {param_changed:<15} {time_str:<15} {diff_str:<15} {final_temp:<15.1f}")
    
    # Análisis por tipo de variación
    print(f"\nAnálisis por tipo de parámetro:")
    print("-" * 60)
    
    variations_by_type = {}
    for result in results:
        if "Base" in result['name']:
            continue
            
        sim_type = result['simulation_type']
        if sim_type not in variations_by_type:
            variations_by_type[sim_type] = []
        variations_by_type[sim_type].append(result)
    
    type_names = {
        'initial_temp': 'Temperatura Inicial',
        'ambient_temp': 'Temperatura Ambiente', 
        'thickness': 'Grosor de Pared',
        'power': 'Potencia'
    }
    
    for var_type, type_results in variations_by_type.items():
        print(f"\n{type_names.get(var_type, var_type)}:")
        
        # Calcular rangos de variación
        if var_type == 'initial_temp':
            values = [r['initial_temperature'] for r in type_results]
            unit = "°C"
        elif var_type == 'ambient_temp':
            values = [r['ambient_temperature'] for r in type_results]
            unit = "°C"
        elif var_type == 'thickness':
            values = [r['wall_thickness_mm'] for r in type_results]
            unit = "mm"
        elif var_type == 'power':
            values = [r['power'] for r in type_results]
            unit = "W"
        else:
            values = []
            unit = ""
        
        if values:
            print(f"  - Rango: {min(values):.1f} - {max(values):.1f} {unit}")
            
            # Calcular tiempos para cada variación
            times_to_target = []
            for r in type_results:
                times = np.array(r['times'])
                temps = np.array(r['fluid_temperatures'])
                target_indices = np.where(temps >= temp_target)[0]
                if len(target_indices) > 0:
                    times_to_target.append(times[target_indices[0]])
            
            if times_to_target and base_time_to_target:
                min_time = min(times_to_target)
                max_time = max(times_to_target)
                print(f"  - Tiempo más rápido: {min_time:.1f}s ({((min_time - base_time_to_target) / base_time_to_target * 100):+.1f}%)")
                print(f"  - Tiempo más lento: {max_time:.1f}s ({((max_time - base_time_to_target) / base_time_to_target * 100):+.1f}%)")

def menu_principal():
    """
    Muestra el menú principal de la aplicación
    """
    while True:
        print("\n" + "="*50)
        print("SIMULACIÓN DE DISTRIBUCIONES ESTADÍSTICAS - TP5")
        print("="*50)
        print("\nSeleccione una opción:")
        print("1. TP 5.A: Distribución uniforme de resistencias")
        print("2. TP 5.B: Distribución normal de temperaturas iniciales")
        print("3. TP 5.C: Distribución uniforme de temperaturas ambiente")
        print("4. TP 5.D: Distribución normal de tensión de alimentación")
        print("5. TP 5.E: Simulación con todas las distribuciones combinadas")
        print("0. Salir")
        
        opcion = input("\nIngrese su opción: ")
        
        if opcion == "1":
            distribucion_uniforme_resistencias()
        elif opcion == "2":
            distribucion_normal_temperaturas_iniciales()
        elif opcion == "3":
            distribucion_uniforme_temperaturas_ambiente()
        elif opcion == "4":
            distribucion_normal_tension_alimentacion()
        elif opcion == "5":
            simulacion_todas_distribuciones()
        elif opcion == "0":
            print("\n¡Gracias por utilizar el programa!")
            break
        else:
            print("\nOpción no válida. Por favor ingrese un número del 0 al 5.")

if __name__ == "__main__":
    menu_principal()