"""
Módulo para eventos aleatorios en las simulaciones.
Permite simular eventos impredecibles que afectan la temperatura del sistema.
"""
import random
import numpy as np
from typing import Optional, Tuple


class EventoAleatorio:
    """
    Clase que representa un evento aleatorio que puede ocurrir durante la simulación.
    
    El evento tiene una probabilidad FIJA de ocurrencia de 1/300 cada segundo y causa
    una disminución de temperatura durante un período determinado.
    """
    
    # Constantes fijas para TODOS los eventos aleatorios
    PROBABILIDAD_POR_SEGUNDO = 1/300  # Probabilidad fija de ocurrencia
    DESCENSO_MAX_TEMP = 50.0          # Máximo descenso de temperatura posible
    def __init__(self, descenso_temp_por_segundo_media: float = 1.5, 
                 duracion_segundos_media: float = 15.0):
        """
        Inicializa el evento aleatorio con distribuciones normales.
        
        Los parámetros de entrada definen las medias de las distribuciones normales.
        Las desviaciones estándar están diseñadas para que sea altamente improbable
        que el descenso total exceda 50°C.
        
        Args:
            descenso_temp_por_segundo_media: Media de la velocidad de descenso (default: 1.5°C/s)
            duracion_segundos_media: Media de la duración del evento (default: 15s)
        """
        # Parámetros de las distribuciones normales
        # Diseñados para que P(velocidad × duración > 50) ≈ 0.001 (0.1%)
        
        # Para velocidad de descenso: Normal(media, std)
        # Rango típico: 0.5 - 2.5 °C/s, con valores extremos hasta ~3.5°C/s
        self.velocidad_media = descenso_temp_por_segundo_media
        self.velocidad_std = descenso_temp_por_segundo_media * 0.25  # 25% de la media como desviación
        self.velocidad_min = 0.1  # Mínimo técnico
        self.velocidad_max = 4.0  # Máximo técnico
        
        # Para duración: Normal(media, std) 
        # Rango típico: 5 - 25 segundos, con valores extremos hasta ~35s
        self.duracion_media = duracion_segundos_media
        self.duracion_std = duracion_segundos_media * 0.2  # 20% de la media como desviación
        self.duracion_min = 3.0   # Mínimo técnico
        self.duracion_max = 40.0  # Máximo técnico
        
        # Estado del evento actual
        self.evento_activo = False
        self.tiempo_inicio_evento = 0.0
        self.duracion_evento = 0.0
        self.descenso_temp_por_segundo = 0.0
        self.descenso_temp_total = 0.0
        self.tiempo_restante_evento = 0.0
        
        # Historial de eventos
        self.eventos_ocurridos = []
        
    def verificar_evento(self, tiempo_actual: float) -> bool:
        """
        Verifica si debe ocurrir un evento aleatorio en el tiempo actual.
        
        Args:
            tiempo_actual: Tiempo actual de la simulación en segundos
            
        Returns:
            bool: True si debe ocurrir un evento, False en caso contrario
        """
        # Solo verificar si no hay un evento activo
        if self.evento_activo:
            return False        # Generar número aleatorio y verificar contra la probabilidad FIJA
        return random.random() < self.PROBABILIDAD_POR_SEGUNDO
    
    def _generar_parametros_aleatorios(self) -> Tuple[float, float]:
        """
        Genera parámetros aleatorios para el evento usando distribuciones normales.
        Implementa un mecanismo de rechazo para asegurar que el descenso total
        casi nunca exceda 50°C.
        
        Returns:
            Tuple[float, float]: (velocidad_descenso, duracion) generados aleatoriamente
        """
        max_intentos = 100  # Prevenir bucle infinito
        
        for intento in range(max_intentos):
            # Generar velocidad con distribución normal, truncada en los límites
            velocidad = np.random.normal(self.velocidad_media, self.velocidad_std)
            velocidad = np.clip(velocidad, self.velocidad_min, self.velocidad_max)
            
            # Generar duración con distribución normal, truncada en los límites  
            duracion = np.random.normal(self.duracion_media, self.duracion_std)
            duracion = np.clip(duracion, self.duracion_min, self.duracion_max)
            
            # Calcular descenso total estimado
            descenso_total = velocidad * duracion
            
            # Verificar si está dentro del límite aceptable
            # Permitir hasta 48°C para dar un margen pequeño
            if descenso_total <= 48.0:
                return velocidad, duracion
            
            # Si es el último intento, ajustar para cumplir el límite
            if intento == max_intentos - 1:
                # Reducir proporcionalmente ambos parámetros
                factor_reduccion = 48.0 / descenso_total
                velocidad *= factor_reduccion
                duracion *= factor_reduccion
                return velocidad, duracion
        
        # Fallback (no debería llegar aquí)
        return self.velocidad_media * 0.8, self.duracion_media * 0.8
    
    def iniciar_evento(self, tiempo_actual: float, temperatura_actual: float = None) -> Tuple[float, float]:
        """
        Inicia un nuevo evento aleatorio generando parámetros aleatorios.
        
        Args:
            tiempo_actual: Tiempo actual de la simulación en segundos
            temperatura_actual: Temperatura actual del fluido (para registro)
            
        Returns:
            Tuple[float, float]: (descenso_temperatura_total, duracion_segundos)
        """
        # Generar parámetros aleatorios para este evento específico
        self.descenso_temp_por_segundo, self.duracion_evento = self._generar_parametros_aleatorios()
        
        # Calcular descenso total basado en los parámetros generados
        self.descenso_temp_total = self.descenso_temp_por_segundo * self.duracion_evento
        
        # Aplicar límite máximo de seguridad (por si acaso)
        if self.descenso_temp_total > self.DESCENSO_MAX_TEMP:
            self.descenso_temp_total = self.DESCENSO_MAX_TEMP
            # Recalcular velocidad para no exceder el máximo
            self.descenso_temp_por_segundo = self.descenso_temp_total / self.duracion_evento
        
        # Configurar estado del evento
        self.evento_activo = True
        self.tiempo_inicio_evento = tiempo_actual
        self.tiempo_restante_evento = self.duracion_evento
        
        # Registrar el evento con la temperatura actual
        evento_info = {
            'tiempo_inicio': tiempo_actual,
            'temperatura_inicial': temperatura_actual if temperatura_actual is not None else 0.0,
            'descenso_total': self.descenso_temp_total,
            'duracion': self.duracion_evento,
            'descenso_por_segundo': self.descenso_temp_por_segundo,
            'generado_aleatoriamente': True  # Indicador de que fue generado aleatoriamente
        }
        self.eventos_ocurridos.append(evento_info)
        
        return self.descenso_temp_total, self.duracion_evento
    
    def procesar_evento(self, tiempo_actual: float, time_step: float = 1.0) -> float:
        """
        Procesa un evento activo y calcula el descenso de temperatura.
        
        Args:
            tiempo_actual: Tiempo actual de la simulación en segundos
            time_step: Paso de tiempo de la simulación en segundos
            
        Returns:
            float: Descenso de temperatura en este paso de tiempo
        """
        if not self.evento_activo:
            return 0.0
        
        # Calcular cuánto tiempo ha pasado desde el inicio del evento
        tiempo_transcurrido = tiempo_actual - self.tiempo_inicio_evento
        
        # Verificar si el evento ya terminó
        if tiempo_transcurrido >= self.duracion_evento:
            self.finalizar_evento()
            return 0.0
        
        # Calcular descenso para este paso de tiempo
        descenso_este_paso = self.descenso_temp_por_segundo * time_step
        
        # Actualizar tiempo restante
        self.tiempo_restante_evento = self.duracion_evento - tiempo_transcurrido
        
        return descenso_este_paso
    
    def finalizar_evento(self) -> None:
        """
        Finaliza el evento actual.
        """
        self.evento_activo = False
        self.tiempo_restante_evento = 0.0
        self.descenso_temp_por_segundo = 0.0
    
    def get_estado_evento(self) -> Optional[dict]:
        """
        Obtiene el estado actual del evento.
        
        Returns:
            dict: Información del evento activo, None si no hay evento activo
        """
        if not self.evento_activo:
            return None
            
        return {
            'activo': True,
            'tiempo_inicio': self.tiempo_inicio_evento,
            'duracion_total': self.duracion_evento,
            'tiempo_restante': self.tiempo_restante_evento,
            'descenso_total': self.descenso_temp_total,
            'descenso_por_segundo': self.descenso_temp_por_segundo
        }
    
    def get_eventos_ocurridos(self) -> list:
        """
        Obtiene la lista de todos los eventos que han ocurrido.
        
        Returns:
            list: Lista de diccionarios con información de eventos
        """
        return self.eventos_ocurridos.copy()
    
    def get_parametros_distribucion(self) -> dict:
        """
        Obtiene información sobre los parámetros de las distribuciones normales.
        
        Returns:
            dict: Información sobre las distribuciones de velocidad y duración
        """
        return {
            'velocidad': {
                'media': self.velocidad_media,
                'desviacion_std': self.velocidad_std,
                'rango_min': self.velocidad_min,
                'rango_max': self.velocidad_max,
                'rango_tipico': f"{self.velocidad_media - 2*self.velocidad_std:.1f} - {self.velocidad_media + 2*self.velocidad_std:.1f}"
            },
            'duracion': {
                'media': self.duracion_media,
                'desviacion_std': self.duracion_std,
                'rango_min': self.duracion_min,
                'rango_max': self.duracion_max,
                'rango_tipico': f"{self.duracion_media - 2*self.duracion_std:.1f} - {self.duracion_media + 2*self.duracion_std:.1f}"
            },
            'descenso_total_esperado': {
                'media': self.velocidad_media * self.duracion_media,
                'maximo_teorico': self.DESCENSO_MAX_TEMP,
                'probabilidad_exceder_50': "< 0.1%"
            }
        }
    
    def reset(self) -> None:
        """
        Reinicia el estado del evento aleatorio.
        """
        self.evento_activo = False
        self.tiempo_inicio_evento = 0.0
        self.duracion_evento = 0.0
        self.descenso_temp_por_segundo = 0.0
        self.descenso_temp_total = 0.0
        self.tiempo_restante_evento = 0.0
        self.eventos_ocurridos.clear()
