import time
import numpy as np

from core.fluid import Fluid
from core.shape import create_shape
from core.material import Material
from core.container import Container
from core.power_source import PowerSource
from simulation.simulation import Simulation
from utils.visualization import Visualization

def main():
    """
    Función principal para simular el calentamiento de agua en un contenedor
    considerando pérdida de calor
    """    # Crear un fluido - agua
    agua = Fluid(
        name="Agua", 
        specific_heat=4186.0, 
        density=997.0, 
        viscosity=0.001, 
        thermal_conductivity=0.6
    )
    
    # Crear un material - acero inoxidable
    acero = Material(
        name="Aluminio", 
        thermal_conductivity=220.0, 
        specific_heat=502.0, 
        density=7900.0
    )
    
    # Crear una forma para el contenedor - cilindro
    cylinder_shape = create_shape(
        type_name="cylindrical", dimensions={"radius": 0.09, "height": 0.150})  # Volumen: 3800cc
    
    # Crear un contenedor
    contenedor = Container(
        forma=cylinder_shape,
        fluido=agua,
        material=acero,
        thickness=0.0025,
        base_density=8000.0  # Añadido: densidad específica de la base
    )    # Crear una fuente de poder
    fuente_poder = PowerSource(power=1100.0)  # 1100W (220V * 5A)
      # Crear un objeto de simulación con temperatura inicial y volumen estándar
    simulacion = Simulation(contenedor, fuente_poder, 
                           initial_temperature=20.0,  # 20°C initial temp
                           fluid_volume=contenedor.get_standard_fluid_volume())  # 2/3 of container volume
    
    # Definir temperatura objetivo y parámetros de simulación
    temperatura_objetivo = 60.0  # Temperatura objetivo: 60°C
    temperatura_ambiente = 20.0  # Temperatura ambiente: 20°C
    correction_factor = 0.90  # Factor de corrección empírico
    
    # Calcular y mostrar el ratio volumen/superficie
    volumen_superficie_ratio = contenedor.get_volume_to_surface_ratio()
    print(f"Ratio volumen/superficie: {volumen_superficie_ratio:.6f} m")
    
    # Preguntar al usuario qué tipo de simulación desea ejecutar
    print("\nSeleccione el tipo de simulación:")
    print("1. Con pérdida de calor")
    print("2. Sin pérdida de calor")
    
    while True:
        opcion = input("Ingrese su opción (1 o 2): ")
        if opcion in ["1", "2"]:
            break
        print("Opción no válida. Por favor ingrese 1 o 2.")
    
    # Preguntar si desea agregar hielo durante la simulación
    print("\n¿Desea agregar hielo durante la simulación?")
    print("1. Sí")
    print("2. No")
    
    agregar_hielo = False
    tiempo_hielo = 0
    masa_hielo = 0.0
    sim_type = ""
    
    while True:
        opcion_hielo = input("Ingrese su opción (1 o 2): ")
        if opcion_hielo in ["1", "2"]:
            break
        print("Opción no válida. Por favor ingrese 1 o 2.")
    
    if opcion_hielo == "1":
        agregar_hielo = True
        while True:
            try:
                tiempo_hielo = int(input("¿En qué segundo desea agregar el hielo? (ej: 50): "))
                if tiempo_hielo > 0:
                    break
                print("El tiempo debe ser un número positivo.")
            except ValueError:
                print("Por favor ingrese un número válido.")
        
        while True:
            try:
                masa_hielo_g = float(input("¿Cuántos gramos de hielo desea agregar? (ej: 100): "))
                if masa_hielo_g > 0:
                    masa_hielo = masa_hielo_g / 1000.0  # Convertir a kg
                    break
                print("La masa debe ser un número positivo.")
            except ValueError:
                print("Por favor ingrese un número válido.")
    
    # Definir tipo de simulación para el título del gráfico
    if opcion == "1":
        sim_type = "con pérdida de calor"
        if agregar_hielo:
            sim_type += f" y adición de {masa_hielo*1000:.0f}g de hielo"
    else:
        sim_type = "sin pérdida de calor"
        if agregar_hielo:
            sim_type += f" y adición de {masa_hielo*1000:.0f}g de hielo"
    
    # Configurar la simulación con los parámetros elegidos
    simulacion.configure_simulation(
        target_temp=temperatura_objetivo,
        ambient_temp=temperatura_ambiente,
        time_step=1.0,
        include_heat_loss=(opcion == "1"),
        correction_factor=correction_factor
    )
    
    # Configurar adición de hielo (si corresponde)
    simulacion.configure_ice_addition(
        add_ice=agregar_hielo,
        ice_add_time=tiempo_hielo,
        ice_mass=masa_hielo
    )
    
    # Mostrar información de la simulación    print("\nSimulando " + ("CON" if opcion == "1" else "SIN") + " pérdida de calor:")
    if opcion == "1":
        coef_perdida = contenedor.calculate_heat_loss_coefficient(correction_factor=correction_factor)
        print(f"Coeficiente de pérdida calculado: {coef_perdida:.6f}")
    
    print(f"Simulando calentamiento hasta alcanzar {temperatura_objetivo}°C...")
    if agregar_hielo:
        print(f"Se agregará {masa_hielo*1000:.0f}g de hielo en t={tiempo_hielo}s")
    
    # Ejecutar la simulación
    resultados = simulacion.simulate()
    
    # Procesar resultados para visualización
    tiempos, temperaturas = zip(*resultados)
    resultados_formateados = {
        'times': tiempos,
        'fluid_temperatures': temperaturas
    }
    
    # Graficar la evolución de la temperatura del fluido
    vis = Visualization(results=resultados_formateados)
    vis.plot_fluid_temperature_evolution(
        title=f"Evolución de la temperatura del fluido ({sim_type})",
        save_path="evolucion_temperatura_fluido.png"
    )

if __name__ == "__main__":
    main()