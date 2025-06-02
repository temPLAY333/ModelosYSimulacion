class Logs:
    """
    Clase para manejar logs de forma universal y dinámica.
    Permite activar y desactivar los logs en tiempo de ejecución.
    """

    def __init__(self):
        """
        Inicializa la clase Logs con los logs desactivados por defecto.
        """
        self.enabled = False

    def enable(self):
        """
        Activa los logs.
        """
        self.enabled = True

    def disable(self):
        """
        Desactiva los logs.
        """
        self.enabled = False

    def log(self, message: str):
        """
        Imprime un mensaje si los logs están activados.

        Args:
            message (str): El mensaje a imprimir.
        """
        if self.enabled:
            print(message)

# Instancia global para usar en todo el proyecto
logger = Logs()
