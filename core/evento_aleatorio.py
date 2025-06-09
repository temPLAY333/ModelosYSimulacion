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
    una disminución de temperatura durante un período determinado.    """
    
    # Constantes fijas para TODOS los eventos aleatorios
    PROBABILIDAD_POR_SEGUNDO = 1/300  # Probabilidad fija de ocurrencia
    DESCENSO_MAX_TEMP = 50.0          # Máximo descenso de temperatura posible
    
    def __init__(self, descenso_temp_total_media: float = 15.0, 
                 duracion_segundos_media: float = 20.0):
        """
        Inicializa el evento aleatorio con distribuciones para aplicación variable.
        
        NUEVA IMPLEMENTACIÓN:
        - Temperatura total: Chi-cuadrada (favorece números pequeños)
        - Duración: Normal (mínimo 10 segundos)
        - Aplicación: Distribución normal por segundo durante el evento
        
        Args:
            descenso_temp_total_media: Media del descenso total de temperatura (default: 15°C)
            duracion_segundos_media: Media de la duración del evento (default: 20s)
        """
        # Parámetros para temperatura total (Chi-cuadrada escalada)
        # Chi-cuadrada favorece valores pequeños, escalamos para obtener media deseada
        self.temp_total_media = descenso_temp_total_media
        self.temp_total_chi_df = 3  # Grados de libertad para chi-cuadrada (más bajo = más sesgado a números pequeños)
        self.temp_total_max = 50.0  # Máximo absoluto
        
        # Parámetros para duración (Normal con mínimo de 10s)
        self.duracion_media = duracion_segundos_media
        self.duracion_std = duracion_segundos_media * 0.25  # 25% de la media como desviación
        self.duracion_min = 10.0   # Mínimo de 10 segundos
        self.duracion_max = 60.0   # Máximo de 60 segundos
        
        # Parámetros para aplicación de temperatura (Normal por segundo)
        self.aplicacion_variabilidad = 0.3  # 30% de variabilidad en cada aplicación
          # Estado del evento actual
        self.evento_activo = False
        self.tiempo_inicio_evento = 0.0
        self.duracion_evento = 0.0
        self.descenso_temp_total = 0.0
        self.tiempo_restante_evento = 0.0
        
        # Nuevo: Lista de descensos por segundo generados aleatoriamente
        self.descensos_por_segundo = []  # Lista de descensos para cada segundo del evento
        self.indice_segundo_actual = 0   # Índice del segundo actual en el evento
        
        # Historial de eventos
        self.eventos_ocurridos = []
        
    def verificar_evento(self, tiempo_actual: float) -> bool:
        """
        Verifica si debe ocurrir un evento aleatorio en el tiempo actual.
        
        Args:
            tiempo_actual: Tiempo actual de la simulación en segundos
            
        Returns:
            bool: True si debe ocurrir un evento, False en caso contrario
        """        # Solo verificar si no hay un evento activo
        if self.evento_activo:
            return False
        # Generar número aleatorio y verificar contra la probabilidad FIJA
        return random.random() < self.PROBABILIDAD_POR_SEGUNDO
    
    def _generar_parametros_aleatorios(self) -> Tuple[float, float, list]:
        """
        Genera parámetros aleatorios para el evento usando nuevas distribuciones.
        
        NUEVA IMPLEMENTACIÓN:
        - Temperatura total: Chi-cuadrada escalada (favorece números pequeños)
        - Duración: Normal (mínimo 10 segundos)
        - Descensos por segundo: Distribución normal desordenada
        
        Returns:
            Tuple[float, float, list]: (temperatura_total, duracion, lista_descensos_por_segundo)
        """
        # 1. Generar temperatura total usando Chi-cuadrada escalada
        # Chi-cuadrada favorece valores pequeños, escalamos para media deseada
        temp_total = self._generar_temperatura_chi_cuadrada()
        
        # 2. Generar duración con distribución normal (mínimo 10s)
        duracion = self._generar_duracion_normal()
          # 3. Generar lista de descensos por segundo usando distribución normal
        descensos_por_segundo = self._generar_descensos_distribuidos(temp_total, int(duracion))
        
        return temp_total, duracion, descensos_por_segundo
    
    def _generar_temperatura_chi_cuadrada(self) -> float:
        """
        Genera temperatura total usando distribución Chi-cuadrada escalada.
        Favorece números pequeños pero permite algunos valores más grandes.
        Maneja el caso especial donde la media puede ser 0 o muy pequeña.
        """
        max_intentos = 50
        
        # Caso especial: si la media es 0, siempre devolver 0.01
        if self.temp_total_media <= 0:
            return 0.01
        
        for _ in range(max_intentos):
            # Generar valor chi-cuadrada
            chi_val = np.random.chisquare(self.temp_total_chi_df)
            
            # Escalar para obtener la media deseada
            # E[χ²(df)] = df, así que escalamos: media_deseada / df
            factor_escala = self.temp_total_media / self.temp_total_chi_df
            temp_total = chi_val * factor_escala
            
            # Si el valor es negativo o muy pequeño, ajustar a 0.01
            if temp_total <= 0:
                temp_total = 0.01
            
            # Verificar límites (ahora desde 0.01)
            if 0.01 <= temp_total <= self.temp_total_max:
                return temp_total
          # Fallback: usar un valor seguro si no se encuentra en el rango
        return min(self.temp_total_media, self.temp_total_max - 5.0)
    
    def _generar_duracion_normal(self) -> float:
        """
        Genera duración usando distribución normal con mínimo de 1 segundo.
        Maneja el caso donde la media puede ser muy pequeña.
        """
        max_intentos = 50
        
        # Si la media es muy pequeña, usar un mínimo de 1 segundo
        duracion_min_efectiva = max(1.0, self.duracion_min)
        
        for _ in range(max_intentos):
            duracion = np.random.normal(self.duracion_media, self.duracion_std)
            
            # Si el valor es negativo o muy pequeño, ajustar al mínimo
            if duracion <= 0:
                duracion = duracion_min_efectiva
            
            # Aplicar límites
            if duracion_min_efectiva <= duracion <= self.duracion_max:
                return duracion
        
        # Fallback: usar un valor dentro del rango válido
        return np.clip(max(self.duracion_media, duracion_min_efectiva), duracion_min_efectiva, self.duracion_max)
    
    def _generar_descensos_distribuidos(self, temp_total: float, duracion_segundos: int) -> list:
        """
        Genera una lista de descensos por segundo usando distribución normal.
        
        NUEVA IMPLEMENTACIÓN:
        - Crea una distribución normal cuya ÁREA BAJO LA CURVA = temp_total
        - Divide esa área en duracion_segundos pedazos
        - Los valores siguen distribución normal pero se desordenan
        
        Args:
            temp_total: Temperatura total a distribuir (área bajo la curva)
            duracion_segundos: Duración del evento en segundos (número de pedazos)
            
        Returns:
            list: Lista de descensos por segundo (desordenados, distribución normal)
        """
        if duracion_segundos <= 0:
            return []
        
        # Parámetros para la distribución normal
        # Media: debe ser positiva para evitar valores negativos
        media_distribucion = temp_total / duracion_segundos  # Promedio por segundo
        
        # Desviación estándar: controla la forma de la curva
        # Usamos 30% de la media para variabilidad
        std_distribucion = media_distribucion * self.aplicacion_variabilidad
        
        # Asegurar que la media sea suficientemente grande para evitar valores negativos
        # Con 3*std como margen, prácticamente no habrá valores negativos
        media_minima = 3 * std_distribucion
        if media_distribucion < media_minima:
            media_distribucion = media_minima
            # Ajustar std proporcionalmente
            std_distribucion = media_distribucion * self.aplicacion_variabilidad
        
        # Generar muestras de la distribución normal
        descensos = []
        for _ in range(duracion_segundos):
            descenso = np.random.normal(media_distribucion, std_distribucion)
            # Garantizar que sea positivo (no puede haber calentamiento durante evento)
            descenso = max(0.01, descenso)  # Mínimo técnico de 0.01°C
            descensos.append(descenso)
        
        # CRUCIAL: Ajustar para que el área total sea exactamente temp_total
        suma_actual = sum(descensos)
        factor_escala = temp_total / suma_actual
        descensos_escalados = [d * factor_escala for d in descensos]
        
        # Los valores están en cierto orden por la generación secuencial
        # DESORDENAR la lista para aplicación aleatoria
        np.random.shuffle(descensos_escalados)
        
        return descensos_escalados
    
    def get_info_distribucion_actual(self) -> dict:
        """
        Obtiene información sobre la distribución normal actual del evento activo.
        
        Returns:
            dict: Información detallada sobre la distribución generada
        """
        if not self.evento_activo or not self.descensos_por_segundo:
            return {"error": "No hay evento activo con distribución"}
        
        descensos = self.descensos_por_segundo
        
        return {
            'estadisticas_distribucion': {
                'total_valores': len(descensos),
                'suma_total': sum(descensos),
                'media_real': np.mean(descensos),
                'std_real': np.std(descensos),
                'min_valor': min(descensos),
                'max_valor': max(descensos),
                'mediana': np.median(descensos)
            },
            'verificacion_area': {
                'area_objetivo': self.descenso_temp_total,
                'area_real': sum(descensos),
                'diferencia': abs(self.descenso_temp_total - sum(descensos)),
                'porcentaje_precision': ((1 - abs(self.descenso_temp_total - sum(descensos)) / self.descenso_temp_total) * 100) if self.descenso_temp_total > 0 else 0
            },
            'distribucion_info': {
                'tipo': 'Normal desordenada',
                'duracion_segundos': len(descensos),
                'aplicacion_desordenada': True
            }
        }
    
    def iniciar_evento(self, tiempo_actual: float, temperatura_actual: float = None) -> Tuple[float, float]:
        """
        Inicia un nuevo evento aleatorio generando parámetros aleatorios.
        
        NUEVA IMPLEMENTACIÓN: Genera temperatura total, duración y secuencia de aplicación.
        
        Args:
            tiempo_actual: Tiempo actual de la simulación en segundos
            temperatura_actual: Temperatura actual del fluido (para registro)
            
        Returns:
            Tuple[float, float]: (descenso_temperatura_total, duracion_segundos)
        """
        # Generar parámetros aleatorios para este evento específico
        self.descenso_temp_total, self.duracion_evento, self.descensos_por_segundo = self._generar_parametros_aleatorios()
        
        # Configurar estado del evento
        self.evento_activo = True
        self.tiempo_inicio_evento = tiempo_actual
        self.tiempo_restante_evento = self.duracion_evento
        self.indice_segundo_actual = 0
          # Registrar el evento con la temperatura actual
        evento_info = {
            'tiempo_inicio': tiempo_actual,
            'temperatura_inicial': temperatura_actual if temperatura_actual is not None else 0.0,
            'descenso_total': self.descenso_temp_total,
            'duracion': self.duracion_evento,
            'descensos_por_segundo': self.descensos_por_segundo.copy(),  # Copia para preservar la secuencia
            'aplicacion_tipo': 'distribucion_normal_area_bajo_curva',
            'distribucion_stats': {
                'media_descensos': np.mean(self.descensos_por_segundo),
                'std_descensos': np.std(self.descensos_por_segundo),
                'min_descenso': min(self.descensos_por_segundo),
                'max_descenso': max(self.descensos_por_segundo),
                'suma_verificacion': sum(self.descensos_por_segundo)
            },
            'generado_aleatoriamente': True
        }
        self.eventos_ocurridos.append(evento_info)
        
        return self.descenso_temp_total, self.duracion_evento
    
    def procesar_evento(self, tiempo_actual: float, time_step: float = 1.0) -> float:
        """
        Procesa un evento activo y calcula el descenso de temperatura.
        
        NUEVA IMPLEMENTACIÓN: Aplica descensos según distribución normal por segundo.
        
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
        
        # Obtener el descenso para este segundo específico
        # Usar el índice del segundo actual en la lista pre-generada
        segundo_evento = int(tiempo_transcurrido)
        
        # Verificar que tengamos datos para este segundo
        if segundo_evento < len(self.descensos_por_segundo):
            descenso_este_paso = self.descensos_por_segundo[segundo_evento] * time_step
            self.indice_segundo_actual = segundo_evento + 1
        else:
            # Fallback: si nos pasamos, usar el último valor disponible
            if len(self.descensos_por_segundo) > 0:
                descenso_este_paso = self.descensos_por_segundo[-1] * time_step
            else:
                descenso_este_paso = 0.0
          # Actualizar tiempo restante
        self.tiempo_restante_evento = self.duracion_evento - tiempo_transcurrido
        
        return descenso_este_paso
    
    def finalizar_evento(self) -> None:
        """
        Finaliza el evento actual.
        """       
        self.evento_activo = False
        self.tiempo_restante_evento = 0.0
        self.descensos_por_segundo = []
        self.indice_segundo_actual = 0
    
    def get_estado_evento(self) -> Optional[dict]:
        """
        Obtiene el estado actual del evento.
        
        Returns:
            dict: Información del evento activo, None si no hay evento activo
        """
        if not self.evento_activo:
            return None
            
        # Calcular descenso promedio para información
        descenso_promedio = (self.descenso_temp_total / self.duracion_evento) if self.duracion_evento > 0 else 0.0
        
        return {
            'activo': True,
            'tiempo_inicio': self.tiempo_inicio_evento,
            'duracion_total': self.duracion_evento,
            'tiempo_restante': self.tiempo_restante_evento,
            'descenso_total': self.descenso_temp_total,
            'descenso_promedio_por_segundo': descenso_promedio,
            'segundo_actual': self.indice_segundo_actual,
            'total_segundos': len(self.descensos_por_segundo),
            'aplicacion_tipo': 'distribucion_normal_desordenada'
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
        Obtiene información sobre los parámetros de las distribuciones.
        
        Returns:
            dict: Información sobre las distribuciones de temperatura y duración
        """
        return {
            'temperatura_total': {
                'media': self.temp_total_media,
                'distribucion': 'Chi-cuadrada escalada',
                'chi_df': self.temp_total_chi_df,
                'caracteristica': 'Favorece números pequeños',
                'rango_max': self.temp_total_max,
                'rango_tipico': f"2 - {self.temp_total_media * 2:.1f}°C"
            },
            'duracion': {
                'media': self.duracion_media,
                'desviacion_std': self.duracion_std,
                'distribucion': 'Normal truncada',
                'rango_min': self.duracion_min,
                'rango_max': self.duracion_max,
                'rango_tipico': f"{self.duracion_media - 2*self.duracion_std:.1f} - {self.duracion_media + 2*self.duracion_std:.1f}s"
            },            'aplicacion': {
                'tipo': 'Distribución normal por área',
                'descripcion': 'Área bajo curva normal = temperatura total',
                'variabilidad': f"{self.aplicacion_variabilidad * 100:.0f}%",
                'caracteristica': 'Valores generados en orden, luego desordenados',
                'control_area': 'Área total = temperatura objetivo exacta',
                'garantia_positiva': 'Media ≥ 3×std para evitar valores negativos'
            },
            'probabilidad_evento': {
                'por_segundo': f"{self.PROBABILIDAD_POR_SEGUNDO:.6f}",
                'porcentaje': f"{self.PROBABILIDAD_POR_SEGUNDO * 100:.3f}%"
            }
        }
    
    def reset(self) -> None:
        """
        Reinicia el estado del evento aleatorio.
        """
        self.evento_activo = False
        self.tiempo_inicio_evento = 0.0
        self.duracion_evento = 0.0
        self.descenso_temp_total = 0.0
        self.tiempo_restante_evento = 0.0
        self.descensos_por_segundo = []
        self.indice_segundo_actual = 0
        self.eventos_ocurridos.clear()
