import math

class Shape:
    """
    Clase base para representar diferentes formas geométricas de contenedores
    """
    def __init__(self, type_name):
        self.type_name = type_name
    
    def get_surface_area(self):
        """
        Calcula y devuelve el área superficial de la forma
        """
        raise NotImplementedError("Este método debe ser implementado por las clases derivadas")
    
    def get_volume(self):
        """
        Calcula y devuelve el volumen de la forma
        """
        raise NotImplementedError("Este método debe ser implementado por las clases derivadas")


class CylindricalShape(Shape):
    """
    Clase para representar un contenedor de forma cilíndrica
    """
    def __init__(self, radius, height):
        super().__init__("cylindrical")
        self.radius = radius
        self.height = height
    
    def get_surface_area(self):
        """
        Calcula y devuelve el área superficial del cilindro
        Área = 2πr² + 2πrh  (bases circulares + pared lateral)
        """
        return 2 * math.pi * self.radius**2 + 2 * math.pi * self.radius * self.height
    
    def get_volume(self):
        """
        Calcula y devuelve el volumen del cilindro
        Volumen = πr²h
        """
        return math.pi * self.radius**2 * self.height
    
    def get_lateral_surface_area(self):
        """
        Calcula el área de superficie lateral del cilindro.
        
        Returns:
            float: Área lateral en metros cuadrados
        """

        return 2 * math.pi * self.radius* self.height
    
    def get_base_area(self):
        """
        Calcula el área de la base del cilindro.
        
        Returns:
            float: Área de la base en metros cuadrados
        """
        import math
        return math.pi * (self.radius**2)


def create_shape(type_name, dimensions):
    """
    Crea una instancia de forma geométrica según el tipo especificado
    
    Args:
        type_name (str): Nombre del tipo de forma ('cylindrical', etc.)
        dimensions (dict): Dimensiones necesarias para crear la forma
        
    Returns:
        Shape: Instancia de una clase derivada de Shape
    """
    if type_name.lower() == "cylindrical":
        return CylindricalShape(dimensions["radius"], dimensions["height"])
    else:
        raise ValueError(f"Tipo de forma no soportado: {type_name}")
