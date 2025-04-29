import math
from abc import ABC, abstractmethod
from fluid import Fluid
from typing import Dict, Any, Union
from material import Material
from shape import Shape

class Container:
    """
    Clase para representar un contenedor que contiene un fluido
    """
    def __init__(self, forma, fluido, material, wall_thickness, base_thickness, base_density):
        self.forma = forma
        self.fluido = fluido
        self.material = material
        self.wall_thickness = wall_thickness
        self.base_thickness = base_thickness
        self.base_density = base_density
    
    def get_volume(self):
        """
        Obtiene el volumen del contenedor basado en su forma.
        
        Returns:
            float: El volumen del contenedor en m³
        """
        return self.forma.get_volume()
    
    def get_volume_to_surface_ratio(self):
        """
        Calcula el ratio de volumen a superficie de contacto con el fluido.
        
        Returns:
            Ratio entre el volumen del fluido y la superficie de contacto (m)
        """
        # Usar el volumen del fluido almacenado en el contenedor
        volume = self.get_volume()
        
        # Para un contenedor cilíndrico lleno hasta cierta altura
        if self.forma.__class__.__name__ == "CylindricalShape":
            radius = self.forma.radius
            
            # Calcular la altura del fluido dentro del cilindro
            fluid_height = volume / (math.pi * radius**2)
            
            # Calcular área de contacto (base + paredes laterales hasta nivel del fluido)
            contact_area = math.pi * radius**2 + 2 * math.pi * radius * fluid_height
            
            return volume / contact_area
        else:
            # Para otras formas, usar una aproximación
            # Surface area will be ligeramente overestimated here
            surface_area = self.forma.get_surface_area()
            return volume / surface_area
    
    def calculate_heat_loss_coefficient(self, correction_factor):
        """
        Calcula el coeficiente de pérdida de calor basado en la conductividad térmica,
        grosor de las paredes y geometría del contenedor.
        
        Args:
            correction_factor: Factor de corrección empírico
        
        Returns:
            Coeficiente para usar en la ecuación de pérdida de calor
        """
        # Obtener el área de contacto del fluido con el contenedor
        surface_area = self.forma.get_surface_area()
        
        # La conductancia térmica (W/m²K) depende de la conductividad y grosor
        # Más conductividad = más transferencia de calor
        # Más grosor = menos transferencia de calor
        thermal_conductance = self.material.thermal_conductivity / self.wall_thickness
        
        # Reducir el coeficiente por un factor de escala para simular efectos reales
        # El valor típico para contenedores domésticos es alrededor de 0.001-0.1
        scale_factor = 0.0001  # Ajustado para obtener valores realistas
        
        # Fórmula correcta: conductancia * superficie * factor / (masa * calor específico)
        heat_loss_coefficient = (thermal_conductance * surface_area * correction_factor * scale_factor) / \
                               (self.get_volume() * self.fluido.density * self.fluido.specific_heat)
        
        return heat_loss_coefficient

    def calculate_heat_loss(self, current_temp, ambient_temp, correction_factor=1.0):
        """
        Calcula la pérdida de calor actual basada en la diferencia de temperatura.
        
        Args:
            current_temp (float): Temperatura actual del fluido en °C
            ambient_temp (float): Temperatura ambiente en °C
            correction_factor (float): Factor de corrección para ajustar el modelo
            
        Returns:
            float: Pérdida de calor en Watts
        """
        # Obtener el coeficiente de pérdida de calor
        heat_loss_coeff = self.calculate_heat_loss_coefficient(correction_factor)
        
        # Calcular la superficie total del contenedor
        surface_area = self.get_total_surface_area()
        
        # Calcular la pérdida de calor usando la ley de enfriamiento de Newton
        # Q = h * A * (T - T_ambiente)
        temp_diff = current_temp - ambient_temp
        heat_loss = heat_loss_coeff * surface_area * temp_diff
        
        return max(0, heat_loss)  # No permitir pérdida negativa (ganancia) de calor
    
    def get_total_surface_area(self):
        """
        Calcula el área de superficie total del contenedor.
        Incluye las paredes laterales y la base (y la tapa si es un contenedor cerrado).
        
        Returns:
            float: Área de superficie total en metros cuadrados
        """
        # Obtener el área de superficie lateral desde la forma
        # Para un cilindro, esto sería 2*pi*r*h
        lateral_surface_area = self.forma.get_lateral_surface_area()
        
        # Obtener el área de la base desde la forma
        # Para un cilindro, esto sería pi*r²
        base_area = self.forma.get_base_area()
        
        # Sumar las áreas para obtener la superficie total
        # Consideramos que el contenedor tiene base pero no tapa (como una olla)
        total_surface_area = lateral_surface_area + base_area
        
        return total_surface_area
