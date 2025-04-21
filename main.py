from material import Material
from fluid import Fluid
from container import Container, Shape
from power_source import PowerSource
from simulation import Simulation
from visualization import Visualization
import numpy as np

def main():
    """
    Función principal para simular el calentamiento de agua en un contenedor
    durante 1 segundo
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
        thermal_conductivity=16.2, 
        specific_heat=502.0, 
        density=7900.0
    )
    
    # Crear una forma para el contenedor - cilindro
    cylinder_shape = Shape(
        type="cylindrical",
        dimensions={"radius": 0.079, "height": 0.1}  # Ajustado para 2000cc
    )
    
    # Crear un contenedor
    contenedor = Container(
        volumen=0.002,  # Volumen en m³ (2000cc)
        forma=cylinder_shape,
        fluido=agua,
        material=acero,
        wall_thickness=0.002  # 2mm de espesor
    )
    
    # Crear una fuente de poder
    fuente_poder = PowerSource(tension=220.0, current=5.0)  # 220V, 5A
    
    # Crear un objeto de simulación
    simulacion = Simulation(contenedor, fuente_poder)
    
    # Simular el calentamiento durante 1 segundo
    print("Simulando calentamiento durante 1 segundo...")
    print("Tiempo(s) | Temperatura del fluido(°C)")
    print("-----------------------------------")
    
    # Realizar la simulación para obtener temperaturas del fluido
    tiempos = np.linspace(0, 1, 11)  # 0 a 1 segundo en 11 pasos (cada 0.1 segundos)
    resultados = simulacion.run_simulation(tiempos)
    
    # Mostrar resultados en consola
    for t, temp in zip(tiempos, resultados['fluid_temperatures']):
        print(f"{t:7.1f} | {temp:7.2f}")
    
    # Visualizar los resultados usando la clase Visualization
    visualizacion = Visualization(resultados)
    visualizacion.plot_fluid_temperature_evolution(
        title=f'Evolución de la temperatura del {agua.name} en contenedor de {acero.name} (2000cc)',
        save_path="temperatura_fluido.png"  # Opcional: guardar el gráfico
    )


if __name__ == "__main__":
    main()
