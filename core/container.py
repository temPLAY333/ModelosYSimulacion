import math

class Container:
    """
    Clase para representar un contenedor que contiene un fluido
    """
    def __init__(self, forma, fluido, material, thickness, base_density):
        self.forma = forma
        self.fluido = fluido
        self.material = material
        self.thickness = thickness
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
        """        # Usar el volumen estándar del fluido (2/3 del contenedor)
        volume = self.get_standard_fluid_volume()
        
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
        
    def calculate_heat_loss_coefficient(self, correction_factor, fluid_volume=None):
        """
        Calcula el coeficiente de pérdida de calor basado en la conductividad térmica,
        grosor de las paredes y geometría del contenedor.
        
        Args:
            correction_factor: Factor de corrección empírico
            fluid_volume: Volumen actual del fluido en m³. Si es None, usa 2/3 del volumen del contenedor
        
        Returns:
            Coeficiente de transferencia de calor global U (W/K)
        """
        # Si no se proporciona volumen del fluido, usar 2/3 del volumen del contenedor como estándar
        if fluid_volume is None:
            fluid_volume = self.get_standard_fluid_volume()        # Obtener el área de superficie total del contenedor
        surface_area = self.forma.get_surface_area()

        # Validar entradas para evitar valores extremos
        thickness = max(0.0001, min(self.thickness, 0.1))  # Limitar grosor entre 0.1mm y 10cm
        surface_area = max(0.001, surface_area)  # Área mínima de 0.001 m²
        
        # Coeficiente de transferencia de calor por convección del aire (W/m²K)
        h_air = 15.0  # W/m²K (convección natural moderada-alta)
        
        # Coeficiente de transferencia de calor por convección del fluido (W/m²K)
        h_fluid = 800.0  # W/m²K
        
        # Resistencia térmica total usando un modelo simplificado más estable
        # R_total = R_convection + R_conduction_wall + R_convection_air
        
        # Resistencia de convección interna (fluido -> pared)
        R_convection_fluid = 1.0 / (h_fluid * surface_area)
        
        # Resistencia de conducción a través de la pared
        # Usar conductividad térmica limitada para evitar valores extremos
        k_material = max(1.0, min(self.material.thermal_conductivity, 500.0))
        R_conduction_wall = thickness / (k_material * surface_area)
          # Resistencia de convección externa (pared -> aire)
        # Factor de grosor más suave y limitado
        thickness_effect = 1.0 + (0.002 / thickness) * 0.5  # Efecto más suave del grosor
        thickness_effect = max(1.0, min(thickness_effect, 3.0))  # Limitar entre 1x y 3x
        R_convection_air = 1.0 / (h_air * surface_area * thickness_effect)
        
        R_total = R_convection_fluid + R_conduction_wall + R_convection_air
        
        # Validar que R_total no sea cero o extremadamente pequeño
        R_total = max(R_total, 1e-6)  # Resistencia mínima para evitar divisiones por cero
        
        # Coeficiente de transferencia de calor global U = 1/R_total (W/K)
        U = 1.0 / R_total
        
        # Factor de amplificación controlado basado en el grosor
        # Grosores menores tienen mayor pérdida de calor, pero de forma controlada
        thickness_mm = thickness * 1000  # Convertir a mm para cálculos
        if thickness_mm < 1.0:
            amplification_factor = 4.0  # Grosor muy fino
        elif thickness_mm < 2.0:
            amplification_factor = 3.0  # Grosor fino
        elif thickness_mm < 5.0:
            amplification_factor = 2.0  # Grosor medio
        else:
            amplification_factor = 1.5  # Grosor grueso
        
        # Aplicar factores de corrección
        heat_loss_coefficient = U * correction_factor * amplification_factor
        
        # Validar resultado final
        heat_loss_coefficient = max(0.001, min(heat_loss_coefficient, 100.0))  # Limitar resultado
        
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
      
    def get_standard_fluid_volume(self):
        """
        Calcula el volumen estándar del fluido como 2/3 del volumen del contenedor.
        
        Returns:
            float: Volumen estándar del fluido en m³
        """
        return (2/3) * self.get_volume()
    
    def set_thickness(self, new_thickness):
        """
        Modifica el grosor  del contenedor.

        Args:
            new_thickness (float): Nuevo grosor del contenedor en metros
        """
        self.thickness = new_thickness
