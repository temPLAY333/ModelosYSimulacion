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
        self.debug_enabled = False

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

    def enable_debug(self):
        """
        Activa los logs de debug (requiere que los logs normales estén activados).
        """
        self.debug_enabled = True

    def disable_debug(self):
        """
        Desactiva los logs de debug.
        """
        self.debug_enabled = False

    def log(self, message: str):
        """
        Imprime un mensaje si los logs están activados.

        Args:
            message (str): El mensaje a imprimir.
        """
        if self.enabled:
            print(message)

    def debug(self, message: str):
        """
        Imprime un mensaje de debug si los logs de debug están activados.

        Args:
            message (str): El mensaje de debug a imprimir.
        """
        if self.enabled and self.debug_enabled:
            print(f"[DEBUG] {message}")

# Instancia global para usar en todo el proyecto
logger = Logs()
