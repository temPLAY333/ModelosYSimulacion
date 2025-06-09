"""
Programa principal para probar simulaciones con eventos aleatorios.

Este script permite al usuario simular el calentamiento de agua con la posibilidad
de que ocurran eventos aleatorios que afecten la temperatura del sistema.
Incluye todas las distribuciones del TP5 con soporte para eventos aleatorios.
"""
import os
import time
import numpy as np

from core.fluid import Fluid
from core.shape import create_shape, CylindricalShape
from core.material import Material
from core.container import Container
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
    agua = Fluid(name="Agua", specific_heat=4186.0, density=997.0, 
                 viscosity=0.001, thermal_conductivity=0.6)
    
    # Crear material (acero inoxidable)
    acero = Material(name="Acero Inoxidable", thermal_conductivity=15.0, 
                     specific_heat=502.0, density=7900.0)
    
    # Crear contenedor base
    base_density = 8000.0  # kg/m³ (acero)
    contenedor = Container(shape, agua, acero, 0.0025, base_density)  # 2.5mm de grosor
    
    # Crear fuente de poder
    fuente_poder = PowerSource(power=1100.0)  # 1100W (220V * 5A)
    
    # Crear la simulación base con temperatura inicial y volumen estándar
    simulacion = Simulation(contenedor, fuente_poder,
                          initial_temperature=20.0,  # 20°C initial temp
                          fluid_volume=contenedor.get_standard_fluid_volume())  # 2/3 of container volume
    
    simulacion.configure_simulation(
        target_temp=60,      # Calentar hasta 60°C
        ambient_temp=20,     # Temperatura ambiente 20°C
        time_step=1.0,       # Paso de tiempo de 1 segundo
        include_heat_loss=True,
        correction_factor=0.90
    )
    
    return contenedor, fuente_poder, simulacion


def simulacion_normal():
    """
    Ejecuta una simulación normal sin eventos aleatorios.
    """
    print("\nSIMULACION NORMAL (Sin eventos aleatorios)")
    print("="*70)
    
    # Crear objetos base
    contenedor, fuente_poder, simulacion = crear_objetos_base()
    
    # Configurar simulación básica
    temperatura_objetivo = 60.0
    temperatura_ambiente = 20.0
    
    simulacion.configure_simulation(
        target_temp=temperatura_objetivo,
        ambient_temp=temperatura_ambiente,
        time_step=1.0,
        include_heat_loss=True,
        correction_factor=0.90
    )
    
    print(f"Temperatura objetivo: {temperatura_objetivo}°C")
    print(f"Temperatura ambiente: {temperatura_ambiente}°C")
    print(f"Potencia: {fuente_poder.power}W")
    print(f"Volumen del fluido: {contenedor.get_standard_fluid_volume()*1e6:.1f}cm³")
    
    # Ejecutar simulación
    print("\nEjecutando simulación...")
    resultados = simulacion.simulate(logs=False)
    
    # Crear directorio para resultados si no existe
    os.makedirs("results/images", exist_ok=True)
    
    # Procesar resultados para visualización
    tiempos, temperaturas = zip(*resultados)
    resultados_formateados = {
        'times': tiempos,
        'fluid_temperatures': temperaturas
    }
    
    # Graficar la evolución de la temperatura del fluido
    vis = Visualization(results=resultados_formateados)
    vis.plot_fluid_temperature_evolution(
        title="Simulación Normal - Evolución de temperatura",
        save_path="results/images/simulacion_normal.png"
    )    # Mostrar estadísticas
    tiempo_final = tiempos[-1]
    temp_final = temperaturas[-1]
    print(f"\nResultados:")
    print(f"   Tiempo total: {tiempo_final:.1f} segundos ({tiempo_final/60:.1f} minutos)")
    print(f"   Temperatura final: {temp_final:.2f}°C")
    print(f"   Objetivo alcanzado: {'Si' if temp_final >= temperatura_objetivo else 'No'}")
    print(f"   Grafico guardado en: results/images/simulacion_normal.png")
    
    return resultados


def simulacion_con_eventos_aleatorios():
    """
    Ejecuta una simulación con eventos aleatorios habilitados.
    """
    print("\nSIMULACION CON EVENTOS ALEATORIOS")
    print("="*70)
    
    # Crear objetos base
    contenedor, fuente_poder, simulacion = crear_objetos_base()
    
    # Solicitar parámetros del evento aleatorio
    print("Configuración de eventos aleatorios:")
    print("Los eventos tienen probabilidad FIJA de 1/300 por segundo (≈0.33%)")
    print("NUEVA IMPLEMENTACIÓN:")
    print("- Temperatura total: Chi-cuadrada (favorece números pequeños)")
    print("- Duración: Normal (mínimo 10 segundos)")
    print("- Aplicación: Distribución normal desordenada por segundo")
    print()
      # Obtener parámetros de las distribuciones
    while True:
        try:
            temp_total_media = float(input("Media de temperatura total del evento (°C) [default: 5.0]: ") or "5.0")
            if temp_total_media >= 0.0 and temp_total_media <= 45.0:
                break
            print("La media de temperatura total debe estar entre 0.0 y 45.0 °C")
        except ValueError:
            print("Por favor ingrese un número válido.")
    
    while True:
        try:
            duracion_media = float(input("Media de duración del evento (segundos) [default: 5.0]: ") or "5.0")
            if duracion_media >= 1.0 and duracion_media <= 60.0:
                break
            print("La media de duración debe estar entre 1.0 y 60 segundos")
        except ValueError:
            print("Por favor ingrese un número válido.")
    
    # Mostrar estimaciones
    print(f"\nEstimaciones basadas en las medias:")
    print(f"   Descenso total medio esperado: {temp_total_media:.1f}°C")
    print(f"   Duración media esperada: {duracion_media:.1f}s")
    print(f"   Intensidad promedio: {temp_total_media/duracion_media:.2f}°C/s")
    print(f"   Cada evento tendrá parámetros únicos generados aleatoriamente")
    
    # Configurar simulación básica
    temperatura_objetivo = 60.0
    temperatura_ambiente = 20.0
    
    simulacion.configure_simulation(
        target_temp=temperatura_objetivo,
        ambient_temp=temperatura_ambiente,
        time_step=1.0,
        include_heat_loss=True,
        correction_factor=0.90
    )
    
    # Configurar eventos aleatorios
    simulacion.configure_evento_aleatorio(
        include_random_events=True,
        descenso_temp_total_media=temp_total_media,
        duracion_segundos_media=duracion_media
    )
    
    print(f"\nParametros de simulacion:")
    print(f"   Temperatura objetivo: {temperatura_objetivo}°C")
    print(f"   Temperatura ambiente: {temperatura_ambiente}°C")
    print(f"   Potencia: {fuente_poder.power}W")
    print(f"   Volumen del fluido: {contenedor.get_standard_fluid_volume()*1e6:.1f}cm³")
    print(f"   Eventos aleatorios: HABILITADOS (nueva implementación)")
    print(f"   Probabilidad: 1/300 por segundo (≈{(1/300)*100:.3f}%/s)")
    print(f"   Media de temperatura total: {temp_total_media}°C")
    print(f"   Media de duración: {duracion_media}s")
    
    # Ejecutar simulación
    print("\nEjecutando simulacion con eventos aleatorios...")
    print("   (Los eventos se mostraran cuando ocurran)")
    resultados = simulacion.simulate(logs=False)
    
    # Crear directorio para resultados si no existe
    os.makedirs("results/images", exist_ok=True)
    
    # Procesar resultados para visualización
    tiempos, temperaturas = zip(*resultados)
    resultados_formateados = {
        'times': tiempos,
        'fluid_temperatures': temperaturas
    }
    
    # Graficar la evolución de la temperatura del fluido
    vis = Visualization(results=resultados_formateados)
    vis.plot_fluid_temperature_evolution(
        title="Simulación con Eventos Aleatorios - Evolución de temperatura",
        save_path="results/images/simulacion_eventos_aleatorios.png"
    )
    
    # Mostrar estadísticas
    tiempo_final = tiempos[-1]
    temp_final = temperaturas[-1]
    
    # Obtener información de eventos ocurridos
    eventos_ocurridos = simulacion.evento_aleatorio.get_eventos_ocurridos() if simulacion.evento_aleatorio else []
    
    print(f"\nResultados:")
    print(f"   Tiempo total: {tiempo_final:.1f} segundos ({tiempo_final/60:.1f} minutos)")
    print(f"   Temperatura final: {temp_final:.2f}°C")
    print(f"   Objetivo alcanzado: {'Si' if temp_final >= temperatura_objetivo else 'No'}")
    print(f"   Eventos aleatorios ocurridos: {len(eventos_ocurridos)}")
    
    if eventos_ocurridos:
        print(f"\nDetalle de eventos aleatorios:")
        for i, evento in enumerate(eventos_ocurridos, 1):
            print(f"   Evento {i}:")
            print(f"     Tiempo: {evento['tiempo_inicio']:.1f}s")
            print(f"     Temperatura inicial: {evento['temperatura_inicial']:.2f}°C")
            print(f"     Descenso total: {evento['descenso_total']:.1f}°C en {evento['duracion']:.1f}s")
            if 'distribucion_stats' in evento:
                stats = evento['distribucion_stats']
                print(f"     Media aplicación: {stats['media_descensos']:.2f}°C/s")
                print(f"     Rango aplicación: {stats['min_descenso']:.2f} - {stats['max_descenso']:.2f}°C/s")
    
    print(f"   Grafico guardado en: results/images/simulacion_eventos_aleatorios.png")
    
    # Mostrar eventos registrados en la simulación
    eventos_simulacion = simulacion.get_simulation_events()
    if eventos_simulacion:
        print(f"\nEventos registrados en la simulacion:")
        for tiempo, evento in eventos_simulacion.items():
            print(f"   t={tiempo:.1f}s: {evento}")
    
    return resultados


def comparar_simulaciones():
    """
    Ejecuta ambas simulaciones y permite compararlas.
    """
    print("\nCOMPARACION DE SIMULACIONES")
    print("="*70)
    print("Se ejecutaran ambas simulaciones para comparar resultados.")
    
    input("\nPresione Enter para continuar...")
    
    # Ejecutar simulación normal
    print("\n1. Ejecutando simulacion normal...")
    resultados_normal = simulacion_normal()
    
    input("\nPresione Enter para continuar con la simulacion con eventos...")
    
    # Ejecutar simulación con eventos
    print("\n2. Ejecutando simulacion con eventos aleatorios...")
    resultados_eventos = simulacion_con_eventos_aleatorios()
    
    # Comparar resultados
    tiempo_normal = resultados_normal[-1][0]
    temp_normal = resultados_normal[-1][1]
    tiempo_eventos = resultados_eventos[-1][0]    
    temp_eventos = resultados_eventos[-1][1]
    
    print(f"\nCOMPARACION FINAL:")
    print(f"{'Simulacion':<25} {'Tiempo (s)':<12} {'Temp Final (°C)':<15} {'Objetivo':<10}")
    print("-" * 70)
    print(f"{'Normal':<25} {tiempo_normal:<12.1f} {temp_normal:<15.2f} {'Si' if temp_normal >= 60 else 'No':<10}")
    print(f"{'Con eventos aleatorios':<25} {tiempo_eventos:<12.1f} {temp_eventos:<15.2f} {'Si' if temp_eventos >= 60 else 'No':<10}")
    
    diferencia_tiempo = tiempo_eventos - tiempo_normal
    diferencia_temp = temp_eventos - temp_normal
    
    print(f"\nDiferencias:")
    print(f"   Tiempo: {diferencia_tiempo:+.1f}s ({diferencia_tiempo/60:+.1f} min)")
    print(f"   Temperatura final: {diferencia_temp:+.2f}°C")
    
    if diferencia_tiempo > 0:
        print(f"   Los eventos aleatorios retrasaron la simulacion en {diferencia_tiempo:.1f} segundos")
    elif diferencia_tiempo < 0:
        print(f"   Los eventos aleatorios aceleraron la simulacion en {abs(diferencia_tiempo):.1f} segundos")
    else:
        print(f"   Los eventos aleatorios no afectaron significativamente el tiempo")


def probar_evento_con_curva_base():
    """
    Prueba el sistema de eventos aleatorios con una simulación de curva base.
    Esta opción permite ver cómo funcionan los eventos con la nueva implementación.
    """
    print("\nPROBAR EVENTO ALEATORIO CON CURVA BASE")
    print("="*70)
    print("Esta opción muestra una simulación con eventos aleatorios usando")
    print("la nueva implementación basada en temperatura total y distribuciones.")
    print()
    
    # Crear objetos base
    contenedor, fuente_poder, simulacion = crear_objetos_base()
    
    # Solicitar parámetros del evento aleatorio
    print("Configuración de eventos aleatorios:")
    print("Los eventos tienen probabilidad FIJA de 1/300 por segundo (≈0.33%)")
    print("NUEVA IMPLEMENTACIÓN:")
    print("- Temperatura total: Chi-cuadrada (favorece números pequeños)")
    print("- Duración: Normal (mínimo 10 segundos)")
    print("- Aplicación: Distribución normal desordenada por segundo")
    print()
    
    # Obtener parámetros de las distribuciones
    while True:
        try:
            temp_total_media = float(input("Media de temperatura total del evento (°C) [default: 5.0]: ") or "5.0")
            if temp_total_media >= 0.0 and temp_total_media <= 45.0:
                break
            print("La media de temperatura total debe estar entre 0.0 y 45.0 °C")
        except ValueError:
            print("Por favor ingrese un número válido.")
    
    while True:
        try:
            duracion_media = float(input("Media de duración del evento (segundos) [default: 5.0]: ") or "5.0")
            if duracion_media >= 1.0 and duracion_media <= 60.0:
                break
            print("La media de duración debe estar entre 1.0 y 60 segundos")
        except ValueError:
            print("Por favor ingrese un número válido.")
    
    # Mostrar estimaciones
    print(f"\nEstimaciones basadas en las medias:")
    print(f"   Descenso total medio esperado: {temp_total_media:.1f}°C")
    print(f"   Duración media esperada: {duracion_media:.1f}s")
    print(f"   Intensidad promedio: {temp_total_media/duracion_media:.2f}°C/s")
    print(f"   Cada evento tendrá parámetros únicos generados aleatoriamente")
    
    # Configurar simulación básica
    temperatura_objetivo = 60.0
    temperatura_ambiente = 20.0
    
    simulacion.configure_simulation(
        target_temp=temperatura_objetivo,
        ambient_temp=temperatura_ambiente,
        time_step=1.0,
        include_heat_loss=True,
        correction_factor=0.90
    )
    
    # Configurar eventos aleatorios
    simulacion.configure_evento_aleatorio(
        include_random_events=True,
        descenso_temp_total_media=temp_total_media,
        duracion_segundos_media=duracion_media
    )
    
    print(f"\nParametros de simulacion:")
    print(f"   Temperatura objetivo: {temperatura_objetivo}°C")
    print(f"   Temperatura ambiente: {temperatura_ambiente}°C")
    print(f"   Potencia: {fuente_poder.power}W")
    print(f"   Volumen del fluido: {contenedor.get_standard_fluid_volume()*1e6:.1f}cm³")
    print(f"   Eventos aleatorios: HABILITADOS (nueva implementación)")
    print(f"   Probabilidad: 1/300 por segundo (≈{(1/300)*100:.3f}%/s)")
    print(f"   Media de temperatura total: {temp_total_media}°C")
    print(f"   Media de duración: {duracion_media}s")
    
    # Ejecutar simulación
    print("\nEjecutando simulacion con eventos aleatorios...")
    print("   (Los eventos se mostraran cuando ocurran)")
    resultados = simulacion.simulate(logs=False)
    
    # Crear directorio para resultados si no existe
    os.makedirs("results/images", exist_ok=True)
    
    # Procesar resultados para visualización
    tiempos, temperaturas = zip(*resultados)
    resultados_formateados = {
        'times': tiempos,
        'fluid_temperatures': temperaturas
    }
    
    # Graficar la evolución de la temperatura del fluido
    vis = Visualization(results=resultados_formateados)
    vis.plot_fluid_temperature_evolution(
        title="Prueba de Eventos Aleatorios - Nueva Implementación",
        save_path="results/images/prueba_eventos_aleatorios.png"
    )
    
    # Mostrar estadísticas
    tiempo_final = tiempos[-1]
    temp_final = temperaturas[-1]
    
    # Obtener información de eventos ocurridos
    eventos_ocurridos = simulacion.evento_aleatorio.get_eventos_ocurridos() if simulacion.evento_aleatorio else []
    
    print(f"\nResultados:")
    print(f"   Tiempo total: {tiempo_final:.1f} segundos ({tiempo_final/60:.1f} minutos)")
    print(f"   Temperatura final: {temp_final:.2f}°C")
    print(f"   Objetivo alcanzado: {'Si' if temp_final >= temperatura_objetivo else 'No'}")
    print(f"   Eventos aleatorios ocurridos: {len(eventos_ocurridos)}")
    
    if eventos_ocurridos:
        print(f"\nDetalle de eventos aleatorios:")
        for i, evento in enumerate(eventos_ocurridos, 1):
            print(f"   Evento {i}:")
            print(f"     Tiempo: {evento['tiempo_inicio']:.1f}s")
            print(f"     Temperatura inicial: {evento['temperatura_inicial']:.2f}°C")
            print(f"     Descenso total: {evento['descenso_total']:.1f}°C en {evento['duracion']:.1f}s")
            if 'distribucion_stats' in evento:
                stats = evento['distribucion_stats']
                print(f"     Media aplicación: {stats['media_descensos']:.2f}°C/s")
                print(f"     Rango aplicación: {stats['min_descenso']:.2f} - {stats['max_descenso']:.2f}°C/s")
    
    print(f"   Grafico guardado en: results/images/prueba_eventos_aleatorios.png")
    
    return resultados


def configurar_eventos_aleatorios():
    """
    Configura los parámetros de eventos aleatorios usando la nueva implementación.
    Los eventos aleatorios están SIEMPRE habilitados.
    
    Returns:
        tuple: (include_events, temp_total_media, duracion_media)
    """
    print("\nEventos aleatorios: SIEMPRE HABILITADOS")
    print("Los eventos tienen probabilidad FIJA de 1/300 por segundo (≈0.33%)")
    print("NUEVA IMPLEMENTACIÓN:")
    print("- Temperatura total: Chi-cuadrada (favorece números pequeños)")
    print("- Duración: Normal (mínimo 1 segundo)")
    print("- Aplicación: Distribución normal desordenada por segundo")
    print("Máximo descenso posible: 50°C")
    print("NOTA: Si la temperatura generada es < 0, se ajusta automáticamente a 0.01°C")
    print()
    
    # Obtener parámetros de las distribuciones
    while True:
        try:
            temp_total_media = float(input("Media de temperatura total del evento (°C) [default: 5.0]: ") or "5.0")
            if temp_total_media >= 0.0 and temp_total_media <= 45.0:
                break
            print("La media de temperatura total debe estar entre 0.0 y 45.0 °C")
        except ValueError:
            print("Por favor ingrese un número válido.")
    
    while True:
        try:
            duracion_media = float(input("Media de duración del evento (segundos) [default: 5.0]: ") or "5.0")
            if duracion_media >= 1.0 and duracion_media <= 60.0:
                break
            print("La media de duración debe estar entre 1.0 y 60 segundos")
        except ValueError:
            print("Por favor ingrese un número válido.")
    
    # Mostrar estimaciones
    print(f"\nEstimaciones basadas en las medias:")
    print(f"   Descenso total medio esperado: {temp_total_media:.1f}°C")
    print(f"   Duración media esperada: {duracion_media:.1f}s")
    print(f"   Intensidad promedio: {temp_total_media/duracion_media:.2f}°C/s")
    print(f"   Cada evento tendrá parámetros únicos generados aleatoriamente")
    
    return True, temp_total_media, duracion_media  # Siempre True


def distribucion_uniforme_resistencias_con_eventos():
    """
    TP 5.A con eventos aleatorios: Distribución uniforme de 5 valores próximos de resistencias.
    """
    print("\nTP 5.A CON EVENTOS ALEATORIOS: Distribución uniforme de resistencias")
    print("="*70)
    
    # Configurar eventos aleatorios (siempre habilitados)
    include_events, temp_total_media, duracion_media = configurar_eventos_aleatorios()
    
    # Crear objetos base
    container, power_source, simulation = crear_objetos_base()
    
    # Crear objeto para estadísticas
    stats = Statistic()
    
    # Obtener parámetros del usuario para la distribución
    print("\nParámetros para la distribución uniforme de resistencias (grosor de pared):")
    
    while True:
        try:
            min_thickness = float(input("Grosor mínimo de pared (mm) [default: 1.0]: ") or "1.0")
            if 0.5 <= min_thickness <= 10.0:
                break
            print("El grosor mínimo debe estar entre 0.5 y 10.0 mm")
        except ValueError:
            print("Por favor ingrese un número válido.")
    
    while True:
        try:
            max_thickness = float(input("Grosor máximo de pared (mm) [default: 5.0]: ") or "5.0")
            if max_thickness > min_thickness and max_thickness <= 15.0:
                break
            print(f"El grosor máximo debe ser mayor que {min_thickness} y no mayor que 15.0 mm")
        except ValueError:
            print("Por favor ingrese un número válido.")
    
    num_simulations = 5  # Fijo en 5 según el enunciado del TP
    
    # Convertir de mm a metros
    min_thickness_m = min_thickness / 1000.0
    max_thickness_m = max_thickness / 1000.0
    
    # Generar distribución uniforme de grosores
    thicknesses = stats.generate_uniform_distribution('wall_thickness', min_thickness_m, max_thickness_m, num_simulations)
    print(f"\nGrosores generados: {[f'{t*1000:.1f}mm' for t in thicknesses]}")
    
    results = []
    
    # Ejecutar simulación para cada grosor
    for i, thickness in enumerate(thicknesses):
        print(f"\nSimulación {i+1}/{num_simulations}: Grosor = {thickness*1000:.1f}mm")
        
        # Crear fluido
        water = Fluid(name="water", density=1000, specific_heat=4186)
        
        # Crear contenedor con grosor específico
        modified_container = Container(
            container.forma,
            water,
            container.material,
            thickness,
            container.base_density
        )
        
        # Crear simulación con grosor específico
        current_sim = Simulation(modified_container, power_source,
                                initial_temperature=20.0,
                                fluid_volume=modified_container.get_standard_fluid_volume())
        
        current_sim.configure_simulation(
            target_temp=60,
            ambient_temp=20,
            time_step=1.0,
            include_heat_loss=True,
            correction_factor=0.90
        )
        
        # Configurar eventos aleatorios (siempre habilitados)
        current_sim.configure_evento_aleatorio(
            include_random_events=True,
            descenso_temp_total_media=temp_total_media,
            duracion_segundos_media=duracion_media
        )
        print(f"   Eventos aleatorios: HABILITADOS")
        
        # Ejecutar simulación
        sim_results = current_sim.simulate(logs=False)
        
        # Almacenar resultados
        results.append({
            'wall_thickness_mm': thickness * 1000,  # Para visualización en mm
            'wall_thickness': thickness,
            'times': [time for time, _ in sim_results],
            'fluid_temperatures': [temp for _, temp in sim_results],
            'eventos_ocurridos': len(current_sim.evento_aleatorio.get_eventos_ocurridos()) if current_sim.evento_aleatorio else 0
        })
    
    # Ordenar resultados por grosor (ascendente)
    results_sorted = sorted(results, key=lambda x: x['wall_thickness'])
    
    # Crear directorio para guardar resultados si no existe
    os.makedirs("results/images", exist_ok=True)
    
    # Visualizar resultados
    viz = Visualization({})
    filename = f"tp5a_resistencias_con_eventos.png"
    title = f"TP 5.A: Efecto de la resistencia térmica CON eventos aleatorios"
    
    viz.plot_distribution_results(
        results_sorted,
        'wall_thickness_mm',
        title=title,
        save_path=f'results/images/{filename}',
        legend_title='Grosor de pared (mm)',
        x_label='Tiempo (segundos)',
        y_label='Temperatura (°C)'
    )
    
    print(f"\nResultados guardados en 'results/images/{filename}'")
    
    # Mostrar estadísticas
    print(f"\nEstadísticas de simulaciones:")
    for i, result in enumerate(results_sorted):
        tiempo_final = result['times'][-1]
        temp_final = result['fluid_temperatures'][-1]
        eventos = result['eventos_ocurridos']
        print(f"   Grosor {result['wall_thickness_mm']:.1f}mm: "
              f"{temp_final:.1f}°C en {tiempo_final:.1f}s, {eventos} eventos")
    
    input("\nPresione Enter para volver al menú principal...")


def distribucion_normal_temperaturas_iniciales_con_eventos():
    """
    TP 5.B con eventos aleatorios: Distribución normal de 5 temperaturas iniciales del agua.
    """
    print("\nTP 5.B CON EVENTOS ALEATORIOS: Distribución normal de temperaturas iniciales")
    print("="*70)
    
    # Configurar eventos aleatorios (siempre habilitados)
    include_events, temp_total_media, duracion_media = configurar_eventos_aleatorios()
    
    # Crear objetos base
    container, power_source, simulation = crear_objetos_base()
    
    # Crear objeto para estadísticas
    stats = Statistic()
    
    # Parámetros según el TP5
    mean_temp = 10
    std_dev = 5
    count = 5
    
    print(f"\nParámetros de la distribución normal:")
    print(f"Media: {mean_temp}°C")
    print(f"Desviación estándar: {std_dev}°C")
    print(f"Número de valores: {count}")
    
    # Generar los valores de temperatura
    initial_temps = stats.generate_normal_distribution('initial_temperature', mean_temp, std_dev, count)
    print(f"\nTemperaturas iniciales generadas: {[f'{temp:.1f}°C' for temp in initial_temps]}")
    
    results = []
    
    # Ejecutar simulación para cada temperatura inicial
    for i, temp in enumerate(initial_temps):
        print(f"\nSimulación {i+1}/{count}: Temperatura inicial = {temp:.1f}°C")
        
        # Crear fluido
        water = Fluid(name="water", density=1000, specific_heat=4186)
        
        # Crear contenedor
        modified_container = Container(
            container.forma,
            water,
            container.material,
            container.thickness,
            container.base_density
        )
        
        # Crear simulación con temperatura inicial específica
        current_sim = Simulation(modified_container, power_source,
                                initial_temperature=temp,
                                fluid_volume=modified_container.get_standard_fluid_volume())
        
        current_sim.configure_simulation(
            target_temp=60,
            ambient_temp=20,
            time_step=1.0,
            include_heat_loss=True,
            correction_factor=0.90
        )
        
        # Configurar eventos aleatorios (siempre habilitados)
        current_sim.configure_evento_aleatorio(
            include_random_events=True,
            descenso_temp_total_media=temp_total_media,
            duracion_segundos_media=duracion_media
        )
        print(f"   Eventos aleatorios: HABILITADOS")
        
        # Ejecutar simulación
        sim_results = current_sim.simulate(logs=False)
        
        # Almacenar resultados
        results.append({
            'initial_temperature': temp,
            'times': [time for time, _ in sim_results],
            'fluid_temperatures': [temp for _, temp in sim_results],
            'eventos_ocurridos': len(current_sim.evento_aleatorio.get_eventos_ocurridos()) if current_sim.evento_aleatorio else 0
        })
    
    # Ordenar resultados por temperatura inicial (ascendente)
    results_sorted = sorted(results, key=lambda x: x['initial_temperature'])
    
    # Crear directorio para guardar resultados si no existe
    os.makedirs("results/images", exist_ok=True)
    
    # Visualizar resultados
    viz = Visualization({})
    filename = f"tp5b_temperaturas_iniciales_con_eventos.png"
    title = f"TP 5.B: Efecto de la temperatura inicial CON eventos aleatorios"
    
    viz.plot_distribution_results(
        results_sorted,
        'initial_temperature',
        title=title,
        save_path=f'results/images/{filename}',
        legend_title='Temperatura inicial (°C)',
        x_label='Tiempo (segundos)',
        y_label='Temperatura (°C)'
    )
    
    print(f"\nResultados guardados en 'results/images/{filename}'")
    
    # Mostrar estadísticas
    print(f"\nEstadísticas de simulaciones:")
    for i, result in enumerate(results_sorted):
        tiempo_final = result['times'][-1]
        temp_final = result['fluid_temperatures'][-1]
        eventos = result['eventos_ocurridos']
        print(f"   T.ini {result['initial_temperature']:.1f}°C: "
              f"{temp_final:.1f}°C en {tiempo_final:.1f}s, {eventos} eventos")
    
    input("\nPresione Enter para volver al menú principal...")


def distribucion_uniforme_temperaturas_ambiente_con_eventos():
    """
    TP 5.C con eventos aleatorios: Distribución uniforme de 8 temperaturas ambiente.
    """
    print("\nTP 5.C CON EVENTOS ALEATORIOS: Distribución uniforme de temperaturas ambiente")
    print("="*70)
    
    # Configurar eventos aleatorios
    include_events, temp_total_media, duracion_media = configurar_eventos_aleatorios()
    
    # Crear objetos base
    container, power_source, simulation = crear_objetos_base()
    
    # Crear objeto para estadísticas
    stats = Statistic()
    
    # Parámetros según el TP5
    min_temp = -20
    max_temp = 50
    count = 8
    
    print(f"\nParámetros de la distribución uniforme:")
    print(f"Rango de temperatura ambiente: {min_temp}°C a {max_temp}°C")
    print(f"Número de valores: {count}")
    
    # Generar distribución uniforme de temperaturas ambiente
    ambient_temps = stats.generate_uniform_distribution('ambient_temperature', min_temp, max_temp, count)
    print(f"\nTemperaturas ambiente generadas: {[f'{temp:.1f}°C' for temp in ambient_temps]}")
    
    results = []
    
    # Ejecutar simulación para cada temperatura ambiente
    for i, temp in enumerate(ambient_temps):
        print(f"\nSimulación {i+1}/{count}: Temperatura ambiente = {temp:.1f}°C")
        
        # Crear simulación con temperatura ambiente específica
        current_sim = Simulation(container, power_source,
                                initial_temperature=20.0,
                                fluid_volume=container.get_standard_fluid_volume())
        
        current_sim.configure_simulation(
            target_temp=60,
            ambient_temp=temp,
            time_step=1.0,
            include_heat_loss=True,
            correction_factor=0.90
        )
        
        # Configurar eventos aleatorios (siempre habilitados)
        current_sim.configure_evento_aleatorio(
            include_random_events=True,
            descenso_temp_total_media=temp_total_media,
            duracion_segundos_media=duracion_media
        )
        print(f"   Eventos aleatorios: HABILITADOS")
        
        # Ejecutar simulación
        sim_results = current_sim.simulate(logs=False)
        
        # Almacenar resultados
        results.append({
            'ambient_temperature': temp,
            'times': [time for time, _ in sim_results],
            'fluid_temperatures': [temp for _, temp in sim_results],
            'eventos_ocurridos': len(current_sim.evento_aleatorio.get_eventos_ocurridos()) if current_sim.evento_aleatorio else 0
        })
    
    # Ordenar resultados por temperatura ambiente (ascendente)
    results_sorted = sorted(results, key=lambda x: x['ambient_temperature'])
    
    # Crear directorio para guardar resultados si no existe
    os.makedirs("results/images", exist_ok=True)
      # Visualizar resultados
    viz = Visualization({})
    filename = f"tp5c_temperaturas_ambiente_con_eventos.png"
    title = f"TP 5.C: Efecto de la temperatura ambiente CON eventos aleatorios"
    
    viz.plot_distribution_results(
        results_sorted,
        'ambient_temperature',
        title=title,
        save_path=f'results/images/{filename}',
        legend_title='Temperatura ambiente (°C)',
        x_label='Tiempo (segundos)',
        y_label='Temperatura (°C)'
    )
    
    print(f"\nResultados guardados en 'results/images/{filename}'")
    
    # Mostrar estadísticas    print(f"\nEstadísticas de simulaciones:")
    for i, result in enumerate(results_sorted):
        tiempo_final = result['times'][-1]
        temp_final = result['fluid_temperatures'][-1]
        eventos = result['eventos_ocurridos']
        print(f"   T.amb {result['ambient_temperature']:.1f}°C: "
              f"{temp_final:.1f}°C en {tiempo_final:.1f}s, {eventos} eventos")
    
    input("\nPresione Enter para volver al menú principal...")


def distribucion_normal_tension_alimentacion_con_eventos():
    """
    TP 5.D con eventos aleatorios: Distribución normal de 5 valores de tensión de alimentación.
    """
    print("\nTP 5.D CON EVENTOS ALEATORIOS: Distribución normal de tensión de alimentación")
    print("="*70)
    
    # Configurar eventos aleatorios
    include_events, temp_total_media, duracion_media = configurar_eventos_aleatorios()
    
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
            print("Por favor seleccione 1 o 2.")
    
    # Configurar según la opción
    if choice == "2":
        mean_voltage = 220
        std_dev = 40
        voltage_type = "AC"
    else:
        mean_voltage = 12
        std_dev = 4
        voltage_type = "DC"
    
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
        
        # Crear simulación con potencia específica
        current_sim = Simulation(container, modified_power_source,
                                initial_temperature=20.0,
                                fluid_volume=container.get_standard_fluid_volume())
        
        current_sim.configure_simulation(
            target_temp=60,
            ambient_temp=20,
            time_step=1.0,
            include_heat_loss=True,
            correction_factor=0.90        )
        
        # Configurar eventos aleatorios (siempre habilitados)
        current_sim.configure_evento_aleatorio(
            include_random_events=True,
            descenso_temp_total_media=temp_total_media,
            duracion_segundos_media=duracion_media
        )
        print(f"   Eventos aleatorios: HABILITADOS")
        
        # Ejecutar simulación
        sim_results = current_sim.simulate(logs=False)
        
        # Almacenar resultados
        results.append({
            'voltage': voltage,
            'power': adjusted_power,
            'times': [time for time, _ in sim_results],
            'fluid_temperatures': [temp for _, temp in sim_results],
            'eventos_ocurridos': len(current_sim.evento_aleatorio.get_eventos_ocurridos()) if current_sim.evento_aleatorio else 0
        })
    
    # Ordenar resultados por tensión (ascendente)
    results_sorted = sorted(results, key=lambda x: x['voltage'])
    
    # Crear directorio para guardar resultados si no existe
    os.makedirs("results/images", exist_ok=True)
      # Visualizar resultados
    viz = Visualization({})
    filename = f"tp5d_tension_alimentacion_con_eventos.png"
    title = f"TP 5.D: Efecto de la tensión ({voltage_type}) CON eventos aleatorios"
    
    viz.plot_distribution_results(
        results_sorted,
        'voltage',
        title=title,
        save_path=f'results/images/{filename}',
        legend_title='Tensión (V)',
        x_label='Tiempo (segundos)',
        y_label='Temperatura (°C)'
    )
    
    print(f"\nResultados guardados en 'results/images/{filename}'")
    
    # Mostrar estadísticas    print(f"\nEstadísticas de simulaciones:")
    for i, result in enumerate(results_sorted):
        tiempo_final = result['times'][-1]
        temp_final = result['fluid_temperatures'][-1]
        eventos = result['eventos_ocurridos']
        print(f"   {result['voltage']:.1f}V ({result['power']:.0f}W): "              f"{temp_final:.1f}°C en {tiempo_final:.1f}s, {eventos} eventos")
    
    input("\nPresione Enter para volver al menú principal...")


def simulacion_todas_distribuciones_con_eventos():
    """
    TP 5.E CON EVENTOS ALEATORIOS: Simulación con curva base y variaciones sistemáticas de parámetros.
    """
    print("\nTP 5.E CON EVENTOS ALEATORIOS: Curva base con variaciones de parámetros")
    print("="*70)
    
    # Configurar eventos aleatorios (siempre habilitados)
    include_events, temp_total_media, duracion_media = configurar_eventos_aleatorios()
    
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
            correction_factor=0.90
        )
        
        # Configurar eventos aleatorios (siempre habilitados)
        custom_sim.configure_evento_aleatorio(
            include_random_events=True,
            descenso_temp_total_media=temp_total_media,
            duracion_segundos_media=duracion_media
        )
        print(f"  - Eventos aleatorios: HABILITADOS")
        
        # Ejecutar simulación
        sim_results = custom_sim.simulate(logs=False)
        
        # Almacenar resultados
        results.append({
            'name': config['name'],
            'initial_temperature': config['initial_temp'],
            'ambient_temperature': config['ambient_temp'],
            'wall_thickness_mm': config['thickness'] * 1000,
            'power': config['power'],
            'times': [time for time, _ in sim_results],
            'fluid_temperatures': [temp for _, temp in sim_results],
            'eventos_ocurridos': len(custom_sim.evento_aleatorio.get_eventos_ocurridos()) if custom_sim.evento_aleatorio else 0
        })
    
    # Crear directorio para guardar resultados si no existe
    os.makedirs("results/images", exist_ok=True)
    
    # Visualizar resultados
    viz = Visualization({})
    viz.plot_distribution_results(
        results,
        'name',
        title='TP 5.E: Curva base con variaciones sistemáticas CON eventos aleatorios',
        save_path='results/images/tp5e_curva_base_variaciones_con_eventos.png',
        legend_title='Configuración',
        x_label='Tiempo (segundos)',
        y_label='Temperatura (°C)'
    )
    
    print(f"\nResultados guardados en 'results/images/tp5e_curva_base_variaciones_con_eventos.png'")
    
    # Mostrar estadísticas simplificadas
    print(f"\nEstadísticas de simulaciones:")
    for result in results:
        tiempo_final = result['times'][-1]
        temp_final = result['fluid_temperatures'][-1]
        eventos = result['eventos_ocurridos']
        print(f"   {result['name']}: {temp_final:.1f}°C en {tiempo_final:.1f}s, {eventos} eventos")
    
    input("\nPresione Enter para volver al menú principal...")


def menu_principal():
    """
    Muestra el menú principal de la aplicación con exactamente 7 opciones.
    """
    while True:
        print("\n" + "="*80)
        print("SIMULADOR CON EVENTOS ALEATORIOS - TP5 DISTRIBUCIONES")
        print("="*80)        
        print("Seleccione una opción:")
        print()
        print("1. Probar evento aleatorio con curva base")
        print("2. TP5.A - Distribución uniforme de resistencias")
        print("3. TP5.B - Distribución normal de temperaturas iniciales")
        print("4. TP5.C - Distribución uniforme de temperaturas ambiente")
        print("5. TP5.D - Distribución normal de tensión de alimentación")
        print("6. TP5.E - Curva base con variaciones")
        print("7. Salir")
        print()
        
        opcion = input("Ingrese su opcion (1-7): ").strip()
        
        if opcion == "1":
            probar_evento_con_curva_base()
            input("\nPresione Enter para volver al menu principal...")
            
        elif opcion == "2":
            distribucion_uniforme_resistencias_con_eventos()
            input("\nPresione Enter para volver al menu principal...")
            
        elif opcion == "3":
            distribucion_normal_temperaturas_iniciales_con_eventos()
            input("\nPresione Enter para volver al menu principal...")
            
        elif opcion == "4":
            distribucion_uniforme_temperaturas_ambiente_con_eventos()
            input("\nPresione Enter para volver al menu principal...")
            
        elif opcion == "5":
            distribucion_normal_tension_alimentacion_con_eventos()
            input("\nPresione Enter para volver al menu principal...")
        elif opcion == "6":
            simulacion_todas_distribuciones_con_eventos()
            input("\nPresione Enter para volver al menu principal...")
            
        elif opcion == "7":
            print("\nHasta luego!")
            break
            
        else:
            print("\nOpcion no valida. Por favor ingrese un numero del 1 al 7.")


def mostrar_info_eventos():
    """
    Muestra información detallada sobre el sistema de eventos aleatorios.
    """
    print("\n" + "="*70)
    print("INFORMACION SOBRE EVENTOS ALEATORIOS - NUEVA IMPLEMENTACIÓN")
    print("="*70)
    
    print("Características del sistema:")
    print(f"   • Probabilidad FIJA: 1/300 por segundo (≈0.333% cada segundo)")
    print(f"   • Descenso máximo FIJO: 50°C por evento")
    print(f"   • Solo puede haber UN evento activo a la vez")
    print(f"   • Parámetros ALEATORIOS usando distribuciones Chi-cuadrada y Normal")
    print()
    
    print("NUEVA IMPLEMENTACIÓN - Generación aleatoria de parámetros:")
    print(f"   • Temperatura total: Distribución Chi-cuadrada (favorece números pequeños)")
    print(f"   • Duración del evento: Distribución Normal (mínimo 1 segundo)")
    print(f"   • Aplicación por segundo: Distribución Normal desordenada")
    print(f"   • Área bajo la curva = temperatura total exacta")
    print(f"   • Valores negativos se ajustan automáticamente a 0.01")
    print()
    
    print("Parámetros configurables (medias de las distribuciones):")
    print(f"   • Media de temperatura total: De 0°C a 45°C (default: 5°C)")
    print(f"   • Media de duración: De 1s a 60s (default: 5s)")
    print(f"   • Sistema automático de ajuste para valores < 0")
    print()
    
    print("Ejemplos de configuración:")
    print(f"   • Media temp total: 5°C, Media duración: 5s")
    print(f"     → Intensidad promedio: 1.0°C/s")
    print(f"   • Media temp total: 0°C, Media duración: 10s")
    print(f"     → Eventos muy suaves (chi-cuadrada favorece valores pequeños)")
    print(f"   • Cada evento tiene parámetros únicos generados independientemente")
    print()
    
    print("Probabilidad de ocurrencia:")
    print(f"   • En 60s: {(1-(299/300)**60)*100:.1f}% de probabilidad")
    print(f"   • En 300s: {(1-(299/300)**300)*100:.1f}% de probabilidad")
    print(f"   • En 600s: {(1-(299/300)**600)*100:.1f}% de probabilidad")
    print()
    
    print("PROCESOS SIMULTANEOS:")
    print(f"   El sistema SIEMPRE mantiene el calentamiento normal")
    print(f"   Los eventos aleatorios ocurren AL MISMO TIEMPO que el calentamiento")
    print(f"   Resultado: Calentamiento - Evento = Temperatura neta")
    print()
    
    print("Ejemplo de simultaneidad:")
    print(f"   Momento t = 100s:")
    print(f"   • Calentamiento normal: +0.5°C/s")
    print(f"   • Evento aleatorio activo: -1.2°C/s (generado con nueva implementación)")
    print(f"   • Resultado neto: -0.7°C/s (temperatura BAJA pero sistema sigue calentando)")
    print(f"   • Al terminar el evento: temperatura vuelve a subir a +0.5°C/s")
    print()
    
    print("Ventajas de la nueva implementación:")
    print(f"   • Control exacto de la temperatura total aplicada")
    print(f"   • Variabilidad realista en la aplicación por segundo")
    print(f"   • Flexibilidad para eventos muy suaves (media = 0)")
    print(f"   • Distribución chi-cuadrada favorece eventos pequeños")
    print(f"   • Aplicación desordenada simula condiciones reales")
    print(f"   • El sistema NUNCA deja de calentar durante un evento!")


if __name__ == "__main__":
    print("Iniciando simulador con eventos aleatorios...")
    menu_principal()