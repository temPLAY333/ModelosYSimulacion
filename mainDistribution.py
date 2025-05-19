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
    water = Fluid(name="water", density=1000, specific_heat=4186, volumen=0.001, temp=20)  # 1 litro, 20°C
    
    # Crear material (acero)
    steel = Material(name="steel", thermal_conductivity=15)  # Acero
    
    # Crear contenedor base
    base_thickness = 0.002  # Grosor base: 2 mm
    wall_thickness = 0.002  # Grosor pared: 2 mm
    base_density = 7800  # kg/m³ (acero)
    container = Container(shape, water, steel, wall_thickness, base_thickness, base_density)
    
    # Crear fuente de poder
    power = 1000  # 1000W (1kW)
    power_source = PowerSource(power)
    
    # Crear la simulación base
    simulation = Simulation(container, power_source)
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
            min_thickness = float(input("Ingrese el grosor mínimo en mm (recomendado 0.8): "))
            if min_thickness <= 0:
                print("El grosor debe ser un valor positivo.")
                continue
            min_thickness = min_thickness / 1000  # Convertir a metros
            break
        except ValueError:
            print("Por favor ingrese un número válido.")
    
    while True:
        try:
            max_thickness = float(input("Ingrese el grosor máximo en mm (recomendado 5.0): "))
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
    os.makedirs("results/images", exist_ok=True)
    
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
        
        # Crear un nuevo fluido con la temperatura específica
        water = Fluid(name="water", density=1000, specific_heat=4186, volumen=0.001, temp=temp)
        
        # Crear nuevo contenedor con el fluido actualizado
        modified_container = Container(
            container.forma,
            water,
            container.material,
            container.wall_thickness,
            container.base_thickness,
            container.base_density
        )
        
        # Actualizar la simulación
        current_sim = Simulation(modified_container, power_source)
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
    TP 5.C: Distribución uniforme de 8 temperaturas iniciales del ambiente,
    entre -20 y 50 grados.
    """
    print("\nTP 5.C: Distribución uniforme de temperaturas ambiente")
    print("="*70)
    
    # Crear objetos base
    container, power_source, simulation = crear_objetos_base()
    
    # Crear objeto para estadísticas
    stats = Statistic()
    
    # Según el enunciado, rango de -20°C a 50°C y 8 valores
    min_temp = -20
    max_temp = 50
    count = 8
    
    print(f"\nRango de temperatura ambiente: {min_temp}°C a {max_temp}°C")
    print(f"Número de valores: {count}")
    
    # Generar distribución uniforme de temperaturas ambiente
    ambient_temps = stats.generate_uniform_distribution('ambient_temperature', min_temp, max_temp, count)
    print(f"\nTemperaturas ambiente generadas: {[f'{temp:.1f}°C' for temp in ambient_temps]}")
    
    results = []
    
    # Ejecutar simulación para cada temperatura ambiente
    for i, temp in enumerate(ambient_temps):
        print(f"\nSimulación {i+1}/{count}: Temperatura ambiente = {temp:.1f}°C")
        
        # Actualizar la simulación
        current_sim = Simulation(container, power_source)
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
        modified_power_source = PowerSource(adjusted_power)
        
        # Actualizar simulación
        current_sim = Simulation(container, modified_power_source)
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
    TP 5.E: Simulaciones que contengan todas las familias de curvas previas.
    """
    print("\nTP 5.E: Simulaciones con todas las distribuciones combinadas")
    print("="*70)
    
    # Crear objetos base
    container_base, power_source_base, simulation_base = crear_objetos_base()
    
    # Crear objeto para estadísticas
    stats = Statistic()
    
    # Definir parámetros para las distribuciones según TP
    # Resistencias (grosor de pared)
    min_thickness = 0.0008  # 0.8 mm
    max_thickness = 0.005   # 5 mm
    
    # Temperaturas iniciales
    mean_init_temp = 10     # °C
    std_dev_temp = 5        # °C
    
    # Temperaturas ambiente
    min_ambient = -20       # °C
    max_ambient = 50        # °C
    
    # Tensiones
    mean_voltage = 220      # V
    std_dev_voltage = 40    # V
    
    # Nominal power para cálculos
    nominal_power = power_source_base.power
    nominal_voltage = mean_voltage
    
    # Preguntar cuántas combinaciones generar
    while True:
        try:
            num_combinations = int(input("\nIngrese el número de combinaciones a simular (recomendado 5): "))
            if num_combinations <= 0:
                print("El número debe ser positivo.")
                continue
            break
        except ValueError:
            print("Por favor ingrese un número entero válido.")
    
    results = []
    
    # Para reproducibilidad
    np.random.seed(42)
    
    for i in range(num_combinations):
        # Generar valores aleatorios para cada parámetro
        wall_thickness = np.random.uniform(min_thickness, max_thickness)         # Resistencia
        initial_temp = np.random.normal(mean_init_temp, std_dev_temp)            # Temp. inicial
        ambient_temp = np.random.uniform(min_ambient, max_ambient)               # Temp. ambiente
        voltage = np.random.normal(mean_voltage, std_dev_voltage)                # Tensión
        
        # Calcular potencia basada en la tensión
        power_factor = (voltage / nominal_voltage) ** 2
        adjusted_power = nominal_power * power_factor
        
        # Crear fluido con temperatura específica
        water = Fluid(name="water", density=1000, specific_heat=4186, volumen=0.001, temp=initial_temp)
        
        # Crear contenedor con fluido y grosor específicos
        custom_container = Container(
            container_base.forma,
            water,
            container_base.material,
            wall_thickness,
            container_base.base_thickness,
            container_base.base_density
        )
        
        # Crear fuente de poder con potencia ajustada
        custom_power_source = PowerSource(adjusted_power)
        
        # Crear simulación con todos los parámetros
        custom_sim = Simulation(custom_container, custom_power_source)
        custom_sim.configure_simulation(
            target_temp=60,
            ambient_temp=ambient_temp,
            time_step=1.0,
            include_heat_loss=True,
            correction_factor=1.0
        )
        
        # Ejecutar simulación
        print(f"\nSimulación {i+1}/{num_combinations}:")
        print(f"  - Grosor de pared: {wall_thickness*1000:.2f} mm")
        print(f"  - Temperatura inicial: {initial_temp:.1f}°C")
        print(f"  - Temperatura ambiente: {ambient_temp:.1f}°C")
        print(f"  - Tensión: {voltage:.1f}V (Potencia: {adjusted_power:.1f}W)")
        
        sim_results = custom_sim.simulate()
        
        # Almacenar resultados
        results.append({
            'combination': i+1,
            'wall_thickness': wall_thickness,
            'wall_thickness_mm': wall_thickness * 1000,
            'initial_temperature': initial_temp,
            'ambient_temperature': ambient_temp,
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
        'combination',
        title='TP 5.E: Simulación con todas las distribuciones combinadas',
        save_path='results/images/tp5e_todas_distribuciones.png',
        legend_title='Combinación',
        x_label='Tiempo (segundos)',
        y_label='Temperatura (°C)'
    )
    
    print(f"\nResultados guardados en 'results/images/tp5e_todas_distribuciones.png'")
    
    # Mostrar detalles de cada combinación
    mostrar_estadisticas_combinaciones(results)
    
    input("\nPresione Enter para volver al menú principal...")

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
        thickness_mm = result['wall_thickness_mm']
        
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
        
        print(f"{i+1:<3} {thickness_mm:<15.3f} {time_to_target}")

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