import numpy as np
from core.container import Container
from core.power_source import PowerSource
from core.evento_aleatorio import EventoAleatorio
from utils.logs import logger
from typing import Optional

class Simulation:
    """
    Clase para simular el calentamiento de un fluido en un contenedor
    usando una fuente de poder específica.
    """
    def __init__(self, container: Container, power_source: PowerSource, 
                 initial_temperature: float = 20.0, fluid_volume: float = 0.001):
        """
        Inicializa la simulación con un contenedor, fuente de poder y estado contextual
        
        Args:
            container: Contenedor con fluido
            power_source: Fuente de poder
            initial_temperature: Temperatura inicial del fluido en °C
            fluid_volume: Volumen del fluido en m³
        """
        self.container = container
        self.power_source = power_source
        
        # Estado contextual del fluido
        self.current_temperature = initial_temperature
        self.current_volume = fluid_volume
        
        # Configuración de simulación
        self.time_step = 1.0
        self.target_temp = 60.0
        self.ambient_temp = 25.0
        self.include_heat_loss = True
        self.correction_factor = 1.0
        
        # Constantes físicas - hielo y agua
        self.ICE_SPECIFIC_HEAT = 2108      # J/(kg·K) - Calor específico del hielo
        self.ICE_DENSITY = 917             # kg/m³ - Densidad del hielo a 0°C
        self.ICE_LATENT_HEAT = 334000      # J/kg - Calor latente de fusión del hielo
        self.ICE_MELTING_POINT = 0.0       # °C - Punto de fusión del hielo
        self.WATER_SPECIFIC_HEAT = 4186    # J/(kg·K) - Calor específico del agua
        
        # Configuración para hielo
        self.add_ice = False
        self.ice_add_time = 50
        self.ice_mass = 0.0                # kg
        self.ice_added = False             # Bandera que indica si el hielo ya se añadió
        self.ice_temp = -5.0               # °C - Temperatura inicial del hielo
        self.ice_remaining = 0.0           # kg - Masa de hielo restante
        self.ice_phase = None              # Fase actual del proceso (None, 'warming', 'melting')
          # Variables para seguimiento
        self.initial_fluid_volume = 0.0    # m³
        self.added_water_volume = 0.0      # m³ - Volumen de agua añadido por hielo derretido
        
        # Para eventos de simulación
        self.simulation_events = {}
        
        # Configuración para eventos aleatorios
        self.evento_aleatorio = None  # Se configurará con configure_evento_aleatorio()
        self.include_random_events = False
    
    def configure_simulation(self, target_temp, ambient_temp=25.0, time_step=1.0, 
                           include_heat_loss=True, correction_factor=1.0):
        """
        Configura los parámetros básicos de simulación
        """
        self.target_temp = target_temp
        self.ambient_temp = ambient_temp
        self.time_step = time_step
        self.include_heat_loss = include_heat_loss
        self.correction_factor = correction_factor
        return self
     
    def configure_ice_addition(self, add_ice=False, ice_add_time=50, ice_mass=0.1, ice_temp=-5.0):
        """
        Configura los parámetros para la adición de hielo
        """
        self.add_ice = add_ice
        self.ice_add_time = ice_add_time
        self.ice_mass = ice_mass  # kg
        self.ice_temp = ice_temp  # °C
        self.ice_added = False
        self.ice_phase = None
        self.ice_remaining = 0.0
        self.added_water_volume = 0.0
        return self
      
    def configure_evento_aleatorio(self, include_random_events=False, 
                                 descenso_temp_total_media=15.0, 
                                 duracion_segundos_media=20.0):
        """
        Configura los parámetros para eventos aleatorios durante la simulación.
        
        NUEVA IMPLEMENTACIÓN:
        - Temperatura total: Chi-cuadrada (favorece números pequeños)
        - Duración: Normal (mínimo 10 segundos)
        - Aplicación: Distribución normal desordenada por segundo
        
        Args:
            include_random_events: Si incluir eventos aleatorios en la simulación
            descenso_temp_total_media: Media del descenso total de temperatura (default: 15°C)
            duracion_segundos_media: Media de la duración del evento (default: 20s)
        """
        self.include_random_events = include_random_events
        if include_random_events:
            self.evento_aleatorio = EventoAleatorio(
                descenso_temp_total_media=descenso_temp_total_media,
                duracion_segundos_media=duracion_segundos_media
            )
        else:
            self.evento_aleatorio = None
        return self
    
    def calculate_heating(self, current_temp):
        """
        Calcula el aumento de temperatura debido al calentamiento básico
        """
        heat_added = self.power_source.power * self.time_step
        
        # Calcular masa actual del fluido usando el estado contextual
        fluid_mass = self.container.fluido.density * self.current_volume
        
        # Calcular incremento de temperatura
        delta_temp = heat_added / (fluid_mass * self.container.fluido.specific_heat)
        
        return heat_added, delta_temp
      
    def calculate_cooling(self, current_temp):
        """
        Calcula la disminución de temperatura debido a la pérdida de calor
        """        # Calcular el coeficiente de transferencia de calor global U (W/K)
        U_global = self.container.calculate_heat_loss_coefficient(self.correction_factor, self.current_volume)
        logger.debug(f"Coeficiente de transferencia de calor global U: {U_global:.6f} W/K")

        # Calcular la pérdida de calor usando la ley de enfriamiento de Newton
        # Q_loss = U * (T_fluid - T_ambient) * time_step
        heat_loss = U_global * (current_temp - self.ambient_temp) * self.time_step
        logger.debug(f"Pérdida de calor calculada: {heat_loss:.6f} J")

        # Calcular masa actual del fluido usando el estado contextual
        fluid_mass = self.container.fluido.density * self.current_volume
        logger.debug(f"Masa del fluido: {fluid_mass:.6f} kg")        # Calcular disminución de temperatura
        temp_drop = heat_loss / (fluid_mass * self.container.fluido.specific_heat)
        logger.debug(f"Disminución de temperatura calculada: {temp_drop:.6f} °C")

        return heat_loss, temp_drop
    
    def handle_ice(self, time_elapsed, current_temp):
        """
        Maneja la adición de hielo en el momento especificado y su proceso de fusión
        siguiendo principios físicos de transferencia de calor y conservación de energía.
        """
        # Si no hay hielo para añadir o aún no es tiempo
        if not self.add_ice or time_elapsed < self.ice_add_time:
            return current_temp, False, []
        
        # Inicializar proceso si es la primera vez
        if not self.ice_added:
            return self._initialize_ice_addition(time_elapsed, current_temp)
        
        # Si hay hielo en el sistema, procesar según la fase actual
        if self.ice_remaining > 0:
            # Fase 1: Calentar el hielo desde su temperatura inicial hasta 0°C
            if self.ice_temp < self.ICE_MELTING_POINT:
                self.ice_phase = 'warming'
                return self._process_ice_warming(time_elapsed, current_temp)
            
            # Fase 2: Derretir el hielo a temperatura constante de 0°C
            self.ice_phase = 'melting'
            return self._process_ice_melting(time_elapsed, current_temp)
        
        return current_temp, False, []
    
    def _initialize_ice_addition(self, time_elapsed, current_temp):
        """
        Inicializa el proceso de adición de hielo al sistema
        """        # Guardar volumen inicial para referencia
        self.initial_fluid_volume = self.current_volume
        
        # Configurar estado inicial del hielo
        self.ice_added = True
        self.ice_remaining = self.ice_mass
        self.ice_phase = 'warming' if self.ice_temp < self.ICE_MELTING_POINT else 'melting'
        
        # Registrar evento y notificar
        message = f"Agregando {self.ice_mass*1000:.0f}g de hielo a {self.ice_temp:.1f}°C al fluido a {current_temp:.2f}°C"
        print(f"\n[t={time_elapsed:.1f}s] {message}")
        self.simulation_events[time_elapsed] = f"Adición de hielo: {self.ice_mass*1000:.0f}g a {self.ice_temp:.1f}°C"
        
        # Calcular volumen del hielo (para información)
        ice_volume_m3 = self.ice_mass / self.ICE_DENSITY
        water_equivalent_volume = self.ice_mass / 1000  # Volumen equivalente en agua (kg/1000 = m³)
        
        # Mostrar información adicional
        print(f"Volumen de hielo: {ice_volume_m3*1e6:.1f}cm³")
        print(f"Cuando se derrita completamente añadirá: {water_equivalent_volume*1e6:.1f}cm³ de agua")
        print(f"Energía necesaria para calentar el hielo a 0°C: {self.ice_mass * self.ICE_SPECIFIC_HEAT * abs(self.ice_temp):.1f}J")
        print(f"Energía necesaria para derretir el hielo: {self.ice_mass * self.ICE_LATENT_HEAT:.1f}J")
        
        # La temperatura no cambia inmediatamente al añadir hielo
        return current_temp, True, []
    
    def _process_ice_warming(self, time_elapsed, current_temp):
        """
        Procesa la fase de calentamiento del hielo desde su temperatura 
        inicial hasta el punto de fusión (0°C)
        """
        # Guardar temperatura inicial para puntos intermedios
        start_temp = current_temp
          # Calcular masa actual del fluido usando el estado contextual
        fluid_mass = self.container.fluido.density * self.current_volume
        
        # 1. Calcular la energía necesaria para calentar todo el hielo hasta 0°C
        energy_needed_total = self.ice_remaining * self.ICE_SPECIFIC_HEAT * abs(self.ice_temp)
        
        # 2. Determinar la energía disponible del fluido
        # Reducimos SIGNIFICATIVAMENTE el factor de transferencia para un proceso más gradual
        # Basado en una transferencia de calor más realista
        heat_transfer_factor = 0.005  # 0.5% por segundo (reducido de 5%)
        
        # La energía disponible depende de la temperatura del agua por encima de 0°C
        available_energy = fluid_mass * self.WATER_SPECIFIC_HEAT * max(0, current_temp) * heat_transfer_factor
        
        # Limitar la transferencia para evitar cambios demasiado bruscos
        # Esto permite un aumento de temperatura del hielo de máximo 0.5°C por paso
        max_energy_per_step = self.ice_remaining * self.ICE_SPECIFIC_HEAT * 0.5
        available_energy = min(available_energy, max_energy_per_step)
        
        # 3. Determinar la energía realmente transferida en este paso
        energy_transferred = min(available_energy, energy_needed_total)
        
        # 4. Calcular el cambio en la temperatura del hielo
        if energy_transferred > 0:
            delta_ice_temp = energy_transferred / (self.ice_remaining * self.ICE_SPECIFIC_HEAT)
            self.ice_temp = min(0, self.ice_temp + delta_ice_temp)
        
        # 5. Calcular la disminución de temperatura en el fluido
        temp_decrease = energy_transferred / (fluid_mass * self.WATER_SPECIFIC_HEAT)
        new_temp = max(0, current_temp - temp_decrease)
        
        # Generar puntos intermedios para suavizar la visualización
        intermediate_points = []
        if abs(new_temp - current_temp) > 0.01:  # Solo si hay un cambio significativo
            intermediate_points = self._generate_intermediate_points(time_elapsed, start_temp, new_temp)
            
        # Reportar estado
        if abs(self.ICE_MELTING_POINT - self.ice_temp) < 0.01:
            print(f"[t={time_elapsed:.1f}s] El hielo alcanzó 0°C, comenzando a derretirse. Temp. fluido: {new_temp:.2f}°C")
            self.simulation_events[time_elapsed] = "El hielo alcanzó su punto de fusión (0°C)"
        else:
            # Mostrar el cambio de temperatura del hielo y la temperatura actual del fluido
            temp_change_rate = delta_ice_temp / self.time_step if 'delta_ice_temp' in locals() else 0
            print(f"[t={time_elapsed:.1f}s] El hielo se calentó a {self.ice_temp:.1f}°C (+{temp_change_rate:.2f}°C/s), temp. fluido: {new_temp:.2f}°C")
        
        return new_temp, True, intermediate_points
    
    def _process_ice_melting(self, time_elapsed, current_temp):
        """
        Procesa la fase de fusión del hielo a temperatura constante de 0°C.
        Aplica las leyes de conservación de energía y equilibrio térmico.
        """        # Guardar temperatura y volumen inicial para cálculos y reportes
        start_temp = current_temp
        original_fluid_volume = self.current_volume
        fluid_mass = self.container.fluido.density * original_fluid_volume
        
        # 1. CONSERVACIÓN DE ENERGÍA: determinar la energía disponible para derretir hielo
        
        # Reducimos SIGNIFICATIVAMENTE el factor de transferencia para un proceso más realista
        # Basado en un modelo de transferencia de calor más gradual
        heat_transfer_factor = 0.003  # 0.3% por segundo (reducido de 8%)
        
        # La energía disponible depende de cuánto está el agua por encima de 0°C
        available_energy = fluid_mass * self.WATER_SPECIFIC_HEAT * max(0, current_temp) * heat_transfer_factor
        
        # 2. FUSIÓN DEL HIELO: calcular cuánto hielo se derrite con la energía disponible
        
        # Energía necesaria para derretir todo el hielo restante
        energy_for_complete_melting = self.ice_remaining * self.ICE_LATENT_HEAT
        
        # Energía realmente transferida (limitada por lo disponible)
        energy_transferred = min(available_energy, energy_for_complete_melting)
        
        # Calcular masa de hielo derretida
        ice_melted = energy_transferred / self.ICE_LATENT_HEAT  # kg
        
        # Limitar la cantidad de hielo derretido por paso para un proceso gradual
        # No más del 2% del hielo total por segundo
        max_melt_rate = self.ice_mass * 0.02 * self.time_step
        ice_melted = min(ice_melted, max_melt_rate, self.ice_remaining)
        
        self.ice_remaining -= ice_melted
        
        # Tasa de derretimiento para reportes (g/s)
        melt_rate_g_per_s = (ice_melted / self.time_step) * 1000
        
        # 3. CONSERVACIÓN DE MASA: actualizar la masa de agua en el sistema
          # El hielo derretido se convierte en agua y aumenta el volumen del fluido
        water_added = ice_melted  # kg (misma masa, distinta densidad)
        water_volume_added = water_added / 1000  # m³ (asumiendo densidad del agua = 1000 kg/m³)
        self.current_volume += water_volume_added
        self.added_water_volume += water_volume_added
        
        # 4. EQUILIBRIO TÉRMICO: calcular la nueva temperatura del fluido
        
        # Primero: disminución por transferencia de energía al hielo
        temp_decrease_transfer = energy_transferred / (fluid_mass * self.WATER_SPECIFIC_HEAT)
        
        # Temperatura después de la transferencia de energía
        intermediate_temp = max(0, current_temp - temp_decrease_transfer)
        
        # Luego: efecto de mezcla con agua a 0°C del hielo derretido
        if ice_melted > 0:
            # Usar la ecuación de mezcla: T_final = (m1*T1 + m2*T2)/(m1 + m2)
            # donde m2 = agua del hielo a T2 = 0°C
            new_temp = (intermediate_temp * fluid_mass) / (fluid_mass + water_added)
        else:
            new_temp = intermediate_temp
        
        # Generar puntos intermedios para suavizar la visualización
        intermediate_points = []
        if abs(new_temp - current_temp) > 0.01:  # Solo si hay cambio significativo
            intermediate_points = self._generate_intermediate_points(time_elapsed, start_temp, new_temp)
        
        # 5. REPORTES: mostrar el progreso del proceso
        
        # Calcular porcentaje de hielo derretido
        percent_melted = 100 * (1 - (self.ice_remaining / self.ice_mass)) if self.ice_mass > 0 else 100
        
        # Estimar tiempo restante basado en la tasa de derretimiento actual
        time_remaining = "∞" if melt_rate_g_per_s <= 0 else f"{self.ice_remaining / (melt_rate_g_per_s/1000):.1f}s"
        
        if self.ice_remaining > 0.001:  # Aún queda hielo significativo
            print(f"[t={time_elapsed:.1f}s] Hielo derritiéndose: {self.ice_remaining*1000:.1f}g restantes ({percent_melted:.1f}%)")
        else:
            # Todo el hielo se ha derretido
            self.ice_remaining = 0
            self.ice_phase = None
            
            # Reportar el fin del proceso
            message = f"Todo el hielo se ha derretido. Temperatura final: {new_temp:.2f}°C"
            print(f"\n[t={time_elapsed:.1f}s] {message}")
              # Reportar cambio total de volumen
            initial_volume_ml = self.initial_fluid_volume * 1e6
            final_volume_ml = self.current_volume * 1e6
            print(f"Volumen inicial: {initial_volume_ml:.1f}cm³")
            print(f"Volumen final: {final_volume_ml:.1f}cm³")
            print(f"Incremento total: {self.added_water_volume*1e6:.1f}cm³ (+{(self.added_water_volume/self.initial_fluid_volume)*100:.1f}%)")
            
            # Registrar evento
            self.simulation_events[time_elapsed] = "Todo el hielo se ha derretido"
        
        return new_temp, True, intermediate_points
    
    def _generate_intermediate_points(self, time_elapsed, start_temp, end_temp, num_points=5):
        """
        Genera puntos intermedios para una visualización más suave de cambios de temperatura
        """
        points = []
        for i in range(1, num_points+1):
            fraction = i / (num_points+1)
            interp_time = time_elapsed - self.time_step * (1-fraction)
            interp_temp = start_temp - (start_temp - end_temp) * fraction
            points.append((interp_time, interp_temp))
        return points
      
    def get_simulation_events(self):
        """
        Devuelve los eventos importantes registrados durante la simulación
        """
        return self.simulation_events
    
    def handle_evento_aleatorio(self, time_elapsed, temperatura_actual=None):
        """
        Maneja los eventos aleatorios durante la simulación.
        
        Args:
            time_elapsed: Tiempo transcurrido en la simulación
            temperatura_actual: Temperatura actual del fluido en este momento
            
        Returns:
            float: Descenso de temperatura causado por el evento aleatorio
        """
        if not self.include_random_events or self.evento_aleatorio is None:
            return 0.0
        
        descenso_temp = 0.0
          # Verificar si debe iniciarse un nuevo evento
        if self.evento_aleatorio.verificar_evento(time_elapsed):
            # Usar la temperatura actual pasada como parámetro, o la del estado contextual como fallback
            temp_para_registro = temperatura_actual if temperatura_actual is not None else self.current_temperature
            descenso_total, duracion = self.evento_aleatorio.iniciar_evento(time_elapsed, temp_para_registro)
            
            # Registrar el evento en el historial de simulación
            event_message = f"Evento aleatorio iniciado: -{descenso_total:.1f}°C durante {duracion:.1f}s"
            self.simulation_events[time_elapsed] = event_message              # Mostrar cuadro con datos del evento detectado
            print(f"\n" + "="*60)
            print(f"EVENTO ALEATORIO DETECTADO en t={time_elapsed:.1f}s")
            print(f"="*60)
            print(f"Temperatura al inicio del evento: {temp_para_registro:.2f}°C")
            print(f"Descenso de temperatura: {descenso_total:.1f}°C")
            print(f"Duracion estimada: {duracion:.1f}s")
            print(f"Velocidad de descenso: {descenso_total/duracion:.2f}°C/s")
            print(f"IMPORTANTE: El calentamiento CONTINÚA durante el evento")
            print(f"Resultado neto = Calentamiento - Evento")
            print(f"="*60)# Procesar evento activo (si existe)
        if self.evento_aleatorio.evento_activo:
            descenso_temp = self.evento_aleatorio.procesar_evento(time_elapsed, self.time_step)
            
            # Verificar si el evento terminó
            if not self.evento_aleatorio.evento_activo and descenso_temp == 0.0:
                event_message = "Evento aleatorio finalizado"
                self.simulation_events[time_elapsed] = event_message
                print(f"\n[t={time_elapsed:.1f}s] EVENTO ALEATORIO FINALIZADO")
                print(f"Temperatura actual: {self.current_temperature:.2f}°C")
                print(f"Calentamiento normal continúa...")
                print("-"*60)
        
        return descenso_temp
    
    def simulate(self, logs=True):        
        """
        Ejecuta la simulación hasta alcanzar la temperatura objetivo
        """
        results = []
        time_elapsed = 0.0
        current_temp = self.current_temperature

        if logs:
            logger.enable()
        else:
            logger.disable()

        logger.log(f"Temperatura inicial: {current_temp:.2f}°C")
        logger.log(f"Objetivo: {self.target_temp:.2f}°C")
        logger.log("Tiempo(s) | Temperatura(°C)")
        logger.log("-------------------------")        # Registrar punto inicial
        results.append((time_elapsed, current_temp))

        # Variables para detección de equilibrio térmico y límites de tiempo
        max_simulation_time = 300000  # 5 horas máximo
        equilibrium_check_interval = 1000  # Verificar equilibrio cada 1000 segundos
        last_equilibrium_check = 0
        temp_history = []  # Historial de temperaturas para detección de equilibrio
        equilibrium_tolerance = 0.001  # Tolerancia para considerar equilibrio térmico
        
        while current_temp < self.target_temp and time_elapsed < max_simulation_time:
            # Avanzar el tiempo para este paso
            time_elapsed += self.time_step            # Calcular calentamiento (siempre, independientemente del hielo)
            heat_added, temp_increase = self.calculate_heating(current_temp)

            # Calcular enfriamiento (si corresponde, siempre independiente del hielo)
            heat_loss = 0
            temp_decrease = 0
            if self.include_heat_loss:
                heat_loss, temp_decrease = self.calculate_cooling(current_temp)            # =====================================
            # APLICAR PROCESOS FÍSICOS SIMULTÁNEOS
            # =====================================
            
            # 1. PROCESOS BASE: Aplicar calentamiento y enfriamiento natural
            temp_before_events = current_temp + temp_increase - temp_decrease            # 2. EVENTOS ALEATORIOS: Ocurren SIMULTÁNEAMENTE con el calentamiento
            #    El sistema SIGUE calentando mientras el evento causa descenso adicional
            #    Esto simula condiciones reales como pérdidas imprevistas, cortes parciales, etc.
            evento_temp_decrease = 0.0
            if self.include_random_events:
                evento_temp_decrease = self.handle_evento_aleatorio(time_elapsed, temp_before_events)
                
                # Si hay evento activo, mostrar la evolución detallada cada segundo
                if self.evento_aleatorio and self.evento_aleatorio.evento_activo and int(time_elapsed) % 1 == 0:
                    estado = self.evento_aleatorio.get_estado_evento()
                    if estado:
                        print(f"t={time_elapsed:.0f}s: Temp={temp_before_events:.2f}°C → "
                              f"{temp_before_events - evento_temp_decrease:.2f}°C "
                              f"(calentamiento: +{temp_increase:.2f}°C, evento: -{evento_temp_decrease:.2f}°C, "
                              f"restante: {estado['tiempo_restante']:.0f}s)")
            
            # Aplicar el descenso del evento
            current_temp = temp_before_events - evento_temp_decrease

            # Comprobar si es momento de añadir hielo o continuar el proceso de fusión
            ice_effect_applied = False
            if self.add_ice and (time_elapsed >= self.ice_add_time or self.ice_remaining > 0):
                new_temp, ice_processed, intermediate_points = self.handle_ice(time_elapsed, current_temp)

                # Añadir puntos intermedios si existen
                if ice_processed and intermediate_points:
                    results.extend(intermediate_points)

                # Actualizar temperatura con efectos del hielo
                current_temp = new_temp
                ice_effect_applied = ice_processed

                # Mostrar más actualizaciones cuando hay hielo
                if self.ice_remaining > 0 and int(time_elapsed) % 5 == 0:
                    logger.log(f"{time_elapsed:.1f} | {current_temp:.2f}")

            # Registrar el resultado de este paso de tiempo
            # Solo si no hemos añadido puntos intermedios que ya incluyen este tiempo
            if not (ice_effect_applied and intermediate_points and 
                   any(abs(t - time_elapsed) < 0.01 for t, _ in intermediate_points)):
                results.append((time_elapsed, current_temp))            # Mostrar actualizaciones cada 10 segundos (si no está mostrando ya por el hielo)
            if int(time_elapsed) % 10 == 0 and not (self.ice_remaining > 0 and int(time_elapsed) % 5 == 0):
                logger.log(f"{time_elapsed:.1f} | {current_temp:.2f}")

            # Verificar equilibrio térmico cada cierto intervalo
            if time_elapsed - last_equilibrium_check >= equilibrium_check_interval:
                temp_history.append(current_temp)
                
                # Mantener solo las últimas 5 mediciones para análisis de equilibrio
                if len(temp_history) > 5:
                    temp_history.pop(0)
                
                # Si tenemos suficientes mediciones, verificar equilibrio
                if len(temp_history) >= 5:
                    temp_variation = max(temp_history) - min(temp_history)
                    if temp_variation < equilibrium_tolerance:
                        logger.log(f"\nEquilibrio térmico alcanzado en {current_temp:.2f}°C después de {time_elapsed:.0f}s")
                        logger.log(f"No es posible alcanzar la temperatura objetivo de {self.target_temp:.2f}°C")
                        logger.log("La pérdida de calor es igual o mayor al calor añadido")
                        break
                
                last_equilibrium_check = time_elapsed

        # Verificar si se alcanzó el límite de tiempo
        if time_elapsed >= max_simulation_time:
            logger.log(f"\nLímite de tiempo alcanzado ({max_simulation_time/3600:.1f} horas)")
            logger.log(f"Temperatura final: {current_temp:.2f}°C")

        return results