"""
Programa principal para probar simulaciones con eventos aleatorios.

Este script permite al usuario simular el calentamiento de agua con la posibilidad
de que ocurran eventos aleatorios que afecten la temperatura del sistema.
"""
import os
import time
import numpy as np

from core.fluid import Fluid
from core.shape import create_shape
from core.material import Material
from core.container import Container
from core.power_source import PowerSource
from simulation.simulation import Simulation
from utils.visualization import Visualization


def crear_objetos_base():
    """
    Crea y devuelve los objetos base necesarios para las simulaciones.
    
    Returns:
        tuple: (container, power_source, simulation)
    """
    # Crear un fluido - agua
    agua = Fluid(
        name="Agua", 
        specific_heat=4186.0, 
        density=997.0, 
        viscosity=0.001, 
        thermal_conductivity=0.6
    )
    
    # Crear un material - acero inoxidable
    acero = Material(
        name="Acero Inoxidable", 
        thermal_conductivity=15.0, 
        specific_heat=502.0, 
        density=7900.0
    )
    
    # Crear una forma para el contenedor - cilindro
    cylinder_shape = create_shape(
        type_name="cylindrical", dimensions={"radius": 0.09, "height": 0.150})  # Volumen: ~3800cc
    
    # Crear un contenedor
    contenedor = Container(
        forma=cylinder_shape,
        fluido=agua,
        material=acero,
        thickness=0.0025,  # 2.5mm de grosor
        base_density=8000.0
    )
    
    # Crear una fuente de poder
    fuente_poder = PowerSource(power=1100.0)  # 1100W (220V * 5A)
    
    # Crear un objeto de simulación con temperatura inicial y volumen estándar
    simulacion = Simulation(contenedor, fuente_poder, 
                           initial_temperature=20.0,  # 20°C initial temp
                           fluid_volume=contenedor.get_standard_fluid_volume())  # 2/3 of container volume
    
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
    print("Los parámetros se generan aleatoriamente usando distribuciones normales")
    print("Máximo descenso posible: 50°C (probabilidad < 0.1%)")
    print()
      # Obtener parámetros de las distribuciones normales
    while True:
        try:
            velocidad_media = float(input("Media de velocidad de descenso (°C/s) [default: 1.5]: ") or "1.5")
            if 0.5 <= velocidad_media <= 3.0:
                break
            print("La media de velocidad debe estar entre 0.5 y 3.0 °C/s")
        except ValueError:
            print("Por favor ingrese un número válido.")
    
    while True:
        try:
            duracion_media = float(input("Media de duración del evento (segundos) [default: 15]: ") or "15")
            if 5.0 <= duracion_media <= 30.0:
                break
            print("La media de duración debe estar entre 5 y 30 segundos")
        except ValueError:
            print("Por favor ingrese un número válido.")
    
    # Mostrar estimaciones
    descenso_medio_estimado = velocidad_media * duracion_media
    print(f"\nEstimaciones basadas en las medias:")
    print(f"   Descenso medio esperado: {descenso_medio_estimado:.1f}°C")
    print(f"   Rango típico de velocidad: {velocidad_media*0.5:.1f} - {velocidad_media*1.5:.1f} °C/s")
    print(f"   Rango típico de duración: {duracion_media*0.6:.1f} - {duracion_media*1.4:.1f} s")
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
        descenso_temp_por_segundo_media=velocidad_media,
        duracion_segundos_media=duracion_media
    )
    
    print(f"\nParametros de simulacion:")
    print(f"   Temperatura objetivo: {temperatura_objetivo}°C")
    print(f"   Temperatura ambiente: {temperatura_ambiente}°C")
    print(f"   Potencia: {fuente_poder.power}W")
    print(f"   Volumen del fluido: {contenedor.get_standard_fluid_volume()*1e6:.1f}cm³")
    print(f"   Eventos aleatorios: HABILITADOS (distribuciones normales)")
    print(f"   Probabilidad: 1/300 por segundo (≈{(1/300)*100:.3f}%/s)")
    print(f"   Media de velocidad: {velocidad_media}°C/s")
    print(f"   Media de duración: {duracion_media}s")
    print(f"   Descenso medio esperado: {descenso_medio_estimado:.1f}°C")
    
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
            print(f"     Descenso: {evento['descenso_total']:.1f}°C en {evento['duracion']:.1f}s")
            print(f"     Velocidad: {evento['descenso_por_segundo']:.2f}°C/s")
    
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


def menu_principal():
    """
    Muestra el menú principal de la aplicación.
    """
    while True:
        print("\n" + "="*70)
        print("SIMULADOR CON EVENTOS ALEATORIOS")
        print("="*70)
        print("Seleccione una opción:")
        print()
        print("1. Simulacion normal (sin eventos aleatorios)")
        print("2. Simulacion con eventos aleatorios")
        print("3. Comparar ambas simulaciones")
        print("4. Informacion sobre eventos aleatorios")
        print("5. Salir")
        print()
        
        opcion = input("Ingrese su opcion (1-5): ").strip()
        
        if opcion == "1":
            simulacion_normal()
            input("\nPresione Enter para volver al menu principal...")
            
        elif opcion == "2":
            simulacion_con_eventos_aleatorios()
            input("\nPresione Enter para volver al menu principal...")
            
        elif opcion == "3":
            comparar_simulaciones()
            input("\nPresione Enter para volver al menu principal...")
            
        elif opcion == "4":
            mostrar_info_eventos()
            input("\nPresione Enter para volver al menu principal...")
            
        elif opcion == "5":
            print("\nHasta luego!")
            break
            
        else:
            print("\nOpcion no valida. Por favor ingrese un numero del 1 al 5.")


def mostrar_info_eventos():
    """
    Muestra información detallada sobre el sistema de eventos aleatorios.
    """
    print("\n" + "="*70)
    print("INFORMACION SOBRE EVENTOS ALEATORIOS")
    print("="*70)
    
    print("Caracteristicas del sistema:")
    print(f"   • Probabilidad FIJA: 1/300 por segundo (≈0.333% cada segundo)")
    print(f"   • Descenso maximo FIJO: 50°C por evento")
    print(f"   • Solo puede haber UN evento activo a la vez")
    print(f"   • Parámetros ALEATORIOS usando distribuciones normales")
    print()
    
    print("Generación aleatoria de parámetros:")
    print(f"   • Velocidad de descenso: Distribución Normal(media, std)")
    print(f"   • Duración del evento: Distribución Normal(media, std)")
    print(f"   • Cada evento tiene parámetros únicos generados independientemente")
    print(f"   • Sistema de rechazo para garantizar descenso total ≤ 48°C")
    print()
    
    print("Parámetros configurables (medias de las distribuciones):")
    print(f"   • Media de velocidad: Cuántos °C/s baja en promedio")
    print(f"   • Media de duración: Cuántos segundos dura en promedio")
    print()
    
    print("Ejemplos de configuración:")
    print(f"   • Media velocidad: 1.5°C/s, Media duración: 15s")
    print(f"     → Descenso medio esperado: 22.5°C")
    print(f"     → Rango típico velocidad: 0.75 - 2.25°C/s")
    print(f"     → Rango típico duración: 9 - 21s")
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
    print(f"   • Evento aleatorio activo: -1.8°C/s (generado aleatoriamente)")
    print(f"   • Resultado neto: -1.3°C/s (temperatura BAJA pero sistema sigue calentando)")
    print(f"   • Al terminar el evento: temperatura vuelve a subir a +0.5°C/s")
    print()
    
    print("Impacto en la simulacion:")
    print(f"   • Los eventos RETRASAN el calentamiento")
    print(f"   • Pueden hacer que NO se alcance la temperatura objetivo")
    print(f"   • Simulan condiciones reales impredecibles con variabilidad natural")
    print(f"   • El sistema NUNCA deja de calentar durante un evento!")
    print(f"   • Cada evento es único e impredecible en intensidad y duración")


if __name__ == "__main__":
    print("Iniciando simulador con eventos aleatorios...")
    menu_principal()