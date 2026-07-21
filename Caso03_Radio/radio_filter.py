"""
================================================================================
CASO 3: COMUNICACIONES POR RADIO - FILTRO PASA BANDAS FIR CON VENTANA HAMMING
================================================================================
Contexto: Sistema de comunicaciones militares en 100 MHz con interferencia
Problema: Canales adyacentes y ruido de banda ancha afectan la señal
Solución: Filtro FIR pasa bandas con ventana Hamming, fc1=99.9 MHz, fc2=100.1 MHz
Autor: [Tu Nombre]
Fecha: 2026-07-20
================================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.signal import firwin, filtfilt, freqz, lfilter
from scipy.fft import fft, fftfreq
import pandas as pd
from scipy.signal import spectrogram
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 1. GENERACIÓN DE SEÑAL DE RADIO SIMULADA (MODULADA + INTERFERENCIA)
# ============================================================================

def generate_radio_signal(duration=5, fs=2000):
    """
    Genera una señal de radio FM simulada con interferencia realista.
    
    Parámetros:
    - duration: Duración en segundos
    - fs: Frecuencia de muestreo en Hz (simulada, escala reducida)
    
    Retorna:
    - t: Vector de tiempo
    - signal_clean: Señal ideal
    - signal_noisy: Señal con ruido e interferencia
    """
    t = np.linspace(0, duration, int(fs * duration))
    
    # ====== SEÑAL MODULADA (FM) ======
    # Frecuencia central de la señal (100 MHz escalada a 100 Hz para simulación)
    fc = 100  # Hz (escala reducida para simulación)
    bandwidth = 20  # Hz (ancho de banda de la señal)
    
    # Señal modulante (información a transmitir)
    message_freq = 5  # Hz
    message = 0.5 * np.sin(2 * np.pi * message_freq * t)
    message += 0.3 * np.sin(2 * np.pi * 2 * message_freq * t)
    message += 0.2 * np.sin(2 * np.pi * 3 * message_freq * t)
    message = np.clip(message, -0.8, 0.8)
    
    # Modulación FM
    modulation_index = 2  # Índice de modulación
    phase = 2 * np.pi * fc * t + modulation_index * np.cumsum(message) / fs
    signal_clean = np.sin(phase)
    
    # Envolvente de la señal (simulando variaciones de transmisión)
    envelope = 0.8 + 0.2 * np.sin(2 * np.pi * 0.5 * t)
    signal_clean *= envelope
    
    # Normalizar
    signal_clean = signal_clean / np.max(np.abs(signal_clean)) * 0.9
    
    # ======== AÑADIR RUIDO E INTERFERENCIA ========
    
    # 1. Interferencia de canales adyacentes
    # Canal adyacente inferior (99.5 MHz escalado a 99.5 Hz)
    adjacent_lower = 0.6 * np.sin(2 * np.pi * 99.5 * t)
    adjacent_lower += 0.3 * np.sin(2 * np.pi * 199 * t)  # Armónico
    adjacent_lower = signal.lfilter([1], [1, 0.8], adjacent_lower)  # Filtrar para simular propagación
    
    # Canal adyacente superior (100.5 MHz escalado a 100.5 Hz)
    adjacent_upper = 0.5 * np.sin(2 * np.pi * 100.5 * t)
    adjacent_upper += 0.2 * np.sin(2 * np.pi * 201 * t)
    adjacent_upper = signal.lfilter([1], [1, 0.7], adjacent_upper)
    
    # 2. Ruido de banda ancha (AWGN)
    noise_awgn = 0.15 * np.random.randn(len(t))
    b_awgn, a_awgn = signal.butter(4, [80, 120], btype='band', fs=fs)
    noise_awgn = signal.filtfilt(b_awgn, a_awgn, noise_awgn)
    
    # 3. Ruido de impulso (interferencia espaciada)
    noise_impulse = np.zeros_like(t)
    for _ in range(15):
        pos = np.random.randint(0, len(t))
        duration_imp = np.random.randint(5, 20)
        if pos + duration_imp < len(t):
            amplitude_imp = np.random.uniform(0.2, 0.6)
            noise_impulse[pos:pos+duration_imp] += amplitude_imp * np.random.randn(duration_imp)
    
    # 4. Ruido de fase (jitter)
    phase_noise = 0.05 * np.random.randn(len(t))
    phase_noise = np.cumsum(phase_noise) / fs * 2 * np.pi
    
    # Combinar todas las interferencias
    signal_noisy = signal_clean + adjacent_lower + adjacent_upper + noise_awgn + noise_impulse
    # Añadir ruido de fase
    signal_noisy = np.sin(np.arcsin(signal_noisy) + phase_noise)
    
    # Saturación (simulando amplificador no lineal)
    signal_noisy = np.tanh(signal_noisy * 1.5) * 0.9
    
    return t, signal_clean, signal_noisy

# ============================================================================
# 2. DISEÑO DEL FILTRO PASA BANDAS FIR CON VENTANA HAMMING
# ============================================================================

def design_bandpass_filter(lowcut=95, highcut=105, fs=2000, numtaps=101, window='hamming'):
    """
    Diseña un filtro FIR pasa bandas con ventana Hamming.
    
    Parámetros:
    - lowcut: Frecuencia de corte inferior en Hz
    - highcut: Frecuencia de corte superior en Hz
    - fs: Frecuencia de muestreo en Hz
    - numtaps: Número de coeficientes del filtro (orden+1)
    - window: Tipo de ventana ('hamming', 'hanning', 'blackman', 'kaiser')
    
    Retorna:
    - h: Coeficientes del filtro FIR
    """
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    
    # Diseñar filtro pasa bandas con ventana
    h = firwin(numtaps, [low, high], pass_zero=False, window=window, fs=fs)
    return h

# ============================================================================
# 3. APLICACIÓN DEL FILTRO (FIR)
# ============================================================================

def apply_filter(signal_data, h):
    """
    Aplica el filtro FIR a la señal.
    
    Parámetros:
    - signal_data: Señal de entrada
    - h: Coeficientes del filtro
    
    Retorna:
    - filtered_signal: Señal filtrada
    """
    # Usar filtfilt para fase cero
    return signal.filtfilt(h, 1, signal_data)

# ============================================================================
# 4. ANÁLISIS DE BER (Bit Error Rate) SIMULADO
# ============================================================================

def calculate_ber(original, filtered, fs, fc=100, bandwidth=20):
    """
    Calcula la tasa de error de bits simulada.
    
    Retorna:
    - ber_before: BER antes del filtrado
    - ber_after: BER después del filtrado
    """
    # Simular demodulación y detección de símbolos
    def demodulate_signal(signal, fs, fc, bandwidth):
        # Filtro de banda para extraer la señal
        nyquist = 0.5 * fs
        low = (fc - bandwidth/2) / nyquist
        high = (fc + bandwidth/2) / nyquist
        b, a = signal.butter(4, [low, high], btype='band')
        filtered = signal.filtfilt(b, a, signal)
        
        # Extraer envolvente (detección de amplitud)
        analytical = signal.hilbert(filtered)
        envelope = np.abs(analytical)
        
        # Normalizar y cuantificar a bits
        envelope = envelope / np.mean(envelope)
        bits = (envelope > 1.0).astype(int)
        return bits
    
    # Demodular señales
    bits_clean = demodulate_signal(original, fs, fc, bandwidth)
    bits_noisy = demodulate_signal(original, fs, fc, bandwidth)  # Base para comparación
    bits_filtered = demodulate_signal(filtered, fs, fc, bandwidth)
    
    # Simular errores basados en SNR
    # Cuanto mayor SNR, menos errores
    def calculate_snr(signal, fs, fc, bandwidth):
        # Calcular potencia en banda
        n = len(signal)
        freq = fftfreq(n, 1/fs)
        fft_signal = np.abs(fft(signal)) / n
        
        mask_band = (freq >= fc - bandwidth/2) & (freq <= fc + bandwidth/2)
        power_signal = np.sum(fft_signal[mask_band]**2)
        
        mask_noise = (freq >= fc - 2*bandwidth) & (freq < fc - bandwidth/2)
        mask_noise |= (freq > fc + bandwidth/2) & (freq <= fc + 2*bandwidth)
        power_noise = np.sum(fft_signal[mask_noise]**2)
        
        if power_noise > 0:
            snr = 10 * np.log10(power_signal / power_noise)
        else:
            snr = 100
        return snr
    
    snr_before = calculate_snr(original, fs, fc, bandwidth)
    snr_after = calculate_snr(filtered, fs, fc, bandwidth)
    
    # Modelo simplificado de BER
    ber_before = 0.5 * np.exp(-snr_before / 10)
    ber_after = 0.5 * np.exp(-snr_after / 10)
    
    # Limitar valores
    ber_before = max(0.001, min(0.5, ber_before))
    ber_after = max(0, min(0.1, ber_after))
    
    return ber_before, ber_after

# ============================================================================
# 5. CÁLCULO DE MÉTRICAS DE DESEMPEÑO
# ============================================================================

def calculate_metrics(original, noisy, filtered, h, fs):
    """
    Calcula métricas para evaluar el rendimiento del filtro.
    """
    def snr(signal, noise):
        signal_power = np.mean(signal**2)
        noise_power = np.mean(noise**2)
        if noise_power == 0:
            return 100
        return 10 * np.log10(signal_power / noise_power)
    
    def correlation(original, filtered):
        return np.corrcoef(original, filtered)[0, 1]
    
    def channel_isolation(signal, fs, fc=100, bandwidth=20):
        """Calcula el aislamiento de canal (rechazo de adyacentes)"""
        n = len(signal)
        freq = fftfreq(n, 1/fs)
        fft_signal = np.abs(fft(signal)) / n
        
        # Energía en banda principal
        mask_main = (freq >= fc - bandwidth/2) & (freq <= fc + bandwidth/2)
        power_main = np.sum(fft_signal[mask_main]**2)
        
        # Energía en canales adyacentes
        mask_adjacent = ((freq >= fc - 1.5*bandwidth) & (freq < fc - bandwidth/2))
        mask_adjacent |= ((freq > fc + bandwidth/2) & (freq <= fc + 1.5*bandwidth))
        power_adjacent = np.sum(fft_signal[mask_adjacent]**2)
        
        # Aislamiento en dB
        if power_adjacent > 0:
            isolation = 10 * np.log10(power_main / power_adjacent)
        else:
            isolation = 50
            
        return isolation
    
    # Cálculos
    noise_before = noisy - original
    noise_after = filtered - original
    
    snr_before = snr(original, noise_before)
    snr_after = snr(original, noise_after)
    
    corr_value = correlation(original, filtered)
    snr_improvement = snr_after - snr_before
    
    # Aislamiento de canal
    isolation_before = channel_isolation(noisy, fs)
    isolation_after = channel_isolation(filtered, fs)
    isolation_improvement = isolation_after - isolation_before
    
    # BER
    ber_before, ber_after = calculate_ber(original, filtered, fs)
    ber_improvement = (ber_before - ber_after) / ber_before * 100 if ber_before > 0 else 0
    
    # Energía preservada
    energy_before = np.sum(noisy**2)
    energy_after = np.sum(filtered**2)
    energy_preserved = (energy_after / energy_before) * 100
    
    # Rechazo de interferencia
    def interference_rejection(signal, fs, fc=100):
        """Calcula el rechazo de interferencia en dB"""
        n = len(signal)
        freq = fftfreq(n, 1/fs)
        fft_signal = np.abs(fft(signal)) / n
        
        # Interferencia en frecuencias específicas
        freqs_adj = [99.5, 100.5, 199, 201]
        power_interference = 0
        for f_adj in freqs_adj:
            idx = np.argmin(np.abs(freq - f_adj))
            if idx < len(fft_signal):
                idx_range = 5
                power_interference += np.sum(fft_signal[max(0, idx-idx_range):min(len(fft_signal), idx+idx_range)]**2)
        
        # Energía total
        power_total = np.sum(fft_signal**2)
        
        if power_total > 0:
            rejection = 10 * np.log10(power_interference / power_total)
        else:
            rejection = 0
            
        return -rejection if rejection < 0 else rejection
    
    rejection_before = interference_rejection(noisy, fs)
    rejection_after = interference_rejection(filtered, fs)
    rejection_improvement = rejection_after - rejection_before
    
    metrics = {
        'SNR_Before_dB': snr_before,
        'SNR_After_dB': snr_after,
        'SNR_Improvement_dB': snr_improvement,
        'Correlation': corr_value,
        'Energy_Preserved_Percent': energy_preserved,
        'Isolation_Before_dB': isolation_before,
        'Isolation_After_dB': isolation_after,
        'Isolation_Improvement_dB': isolation_improvement,
        'BER_Before': ber_before,
        'BER_After': ber_after,
        'BER_Improvement_Percent': ber_improvement,
        'Interference_Rejection_Before_dB': rejection_before,
        'Interference_Rejection_After_dB': rejection_after,
        'Interference_Rejection_Improvement_dB': rejection_improvement
    }
    
    return metrics

# ============================================================================
# 6. GENERACIÓN DE GRÁFICAS
# ============================================================================

def generate_plots(t, signal_clean, signal_noisy, signal_filtered, h, fs, metrics):
    """
    Genera todas las gráficas necesarias para el análisis.
    """
    # Configuración de estilo
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.rcParams['figure.figsize'] = [12, 6]
    plt.rcParams['font.size'] = 12
    
    # ======== GRÁFICA 1: SEÑALES EN EL TIEMPO ========
    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    time_limit = 2
    idx_limit = int(time_limit * fs)
    
    # Señal con ruido vs señal limpia
    ax1.plot(t[:idx_limit], signal_clean[:idx_limit], 'g-', linewidth=2, 
             label='Señal Modulada Ideal', alpha=0.7)
    ax1.plot(t[:idx_limit], signal_noisy[:idx_limit], 'r-', linewidth=1, 
             label='Señal con Interferencia', alpha=0.6)
    ax1.set_title('Señal de Radio: Transmisión Ideal vs con Interferencia', 
                  fontsize=16, fontweight='bold')
    ax1.set_xlabel('Tiempo (segundos)')
    ax1.set_ylabel('Amplitud')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, time_limit])
    
    # Señal filtrada vs señal limpia
    ax2.plot(t[:idx_limit], signal_clean[:idx_limit], 'g-', linewidth=2, 
             label='Señal Ideal', alpha=0.5)
    ax2.plot(t[:idx_limit], signal_filtered[:idx_limit], 'b-', linewidth=2, 
             label=f'Señal Filtrada (FIR Hamming, 95-105 Hz)', alpha=0.9)
    ax2.set_title('Señal de Radio: Filtrada vs Ideal', 
                  fontsize=16, fontweight='bold')
    ax2.set_xlabel('Tiempo (segundos)')
    ax2.set_ylabel('Amplitud')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, time_limit])
    
    plt.tight_layout()
    plt.savefig('img_radio_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ======== GRÁFICA 2: RESPUESTA EN FRECUENCIA DEL FILTRO FIR ========
    fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Respuesta en frecuencia del filtro FIR
    w, h_response = freqz(h, 1, worN=2000, fs=fs)
    
    ax1.plot(w, 20 * np.log10(abs(h_response)), 'b-', linewidth=2)
    ax1.axvline(95, color='r', linestyle='--', linewidth=2, 
                label='Frecuencia de Corte Inferior (95 Hz)')
    ax1.axvline(105, color='r', linestyle='--', linewidth=2, 
                label='Frecuencia de Corte Superior (105 Hz)')
    ax1.axvline(100, color='orange', linestyle=':', linewidth=2, alpha=0.7, 
                label='Frecuencia Central (100 Hz)')
    ax1.axhline(-3, color='gray', linestyle=':', alpha=0.7, label='-3 dB')
    ax1.set_title('Respuesta en Frecuencia - Filtro FIR Pasa Bandas (Ventana Hamming)', 
                  fontsize=16, fontweight='bold')
    ax1.set_xlabel('Frecuencia (Hz)')
    ax1.set_ylabel('Magnitud (dB)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([80, 120])
    ax1.set_ylim([-80, 5])
    
    # Coeficientes del filtro FIR
    ax2.stem(range(len(h)), h, basefmt=' ', linefmt='b-', markerfmt='bo')
    ax2.set_title('Coeficientes del Filtro FIR (N = {} taps)'.format(len(h)), 
                  fontsize=16, fontweight='bold')
    ax2.set_xlabel('Índice del Coeficiente')
    ax2.set_ylabel('Amplitud')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('img_filter_design.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ======== GRÁFICA 3: ANÁLISIS ESPECTRAL ========
    fig3, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    n = len(t)
    freq = fftfreq(n, 1/fs)
    fft_noisy = np.abs(fft(signal_noisy)) / n
    fft_filtered = np.abs(fft(signal_filtered)) / n
    
    freq_limit = 150
    idx_freq = int(freq_limit / (fs/n))
    
    ax1.plot(freq[:idx_freq], 20 * np.log10(fft_noisy[:idx_freq] + 1e-10), 
             'r-', linewidth=1.5, alpha=0.7, label='Antes del Filtro')
    ax1.plot(freq[:idx_freq], 20 * np.log10(fft_filtered[:idx_freq] + 1e-10), 
             'b-', linewidth=2, label='Después del Filtro')
    ax1.axvline(95, color='g', linestyle='--', linewidth=2, alpha=0.7, 
                label='Banda de Paso 95-105 Hz')
    ax1.axvline(105, color='g', linestyle='--', linewidth=2, alpha=0.7)
    ax1.axvline(99.5, color='orange', linestyle=':', linewidth=2, alpha=0.7, 
                label='Interferencia Adyacente')
    ax1.axvline(100.5, color='orange', linestyle=':', linewidth=2, alpha=0.7)
    ax1.set_title('Espectro de Frecuencia: Antes vs Después del Filtrado', 
                  fontsize=16, fontweight='bold')
    ax1.set_xlabel('Frecuencia (Hz)')
    ax1.set_ylabel('Magnitud (dB)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([80, 120])
    
    # Espectrograma
    f_spect, t_spect, Sxx_spect = spectrogram(signal_filtered, fs, nperseg=256, noverlap=128)
    ax2.pcolormesh(t_spect, f_spect, 10 * np.log10(Sxx_spect + 1e-10), 
                   shading='gouraud', cmap='viridis')
    ax2.set_title('Espectrograma - Señal Filtrada (Banda 95-105 Hz)', 
                  fontsize=16, fontweight='bold')
    ax2.set_xlabel('Tiempo (segundos)')
    ax2.set_ylabel('Frecuencia (Hz)')
    ax2.set_ylim([80, 120])
    ax2.axhline(95, color='cyan', linestyle='--', linewidth=2, alpha=0.5, label='95 Hz')
    ax2.axhline(105, color='cyan', linestyle='--', linewidth=2, alpha=0.5, label='105 Hz')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('img_spectrum_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ======== GRÁFICA 4: DIAGRAMA DE CONSTELACIÓN (SIMULADO) ========
    fig4, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Simular constelación para QPSK
    def generate_constellation(signal, fs, fc=100, bandwidth=20):
        # Demodular I/Q
        n = len(signal)
        t = np.arange(n) / fs
        
        # Señal en fase (I)
        i_signal = signal * np.cos(2 * np.pi * fc * t)
        # Señal en cuadratura (Q)
        q_signal = signal * np.sin(2 * np.pi * fc * t)
        
        # Filtrar para eliminar componentes de alta frecuencia
        nyquist = 0.5 * fs
        low = (fc - bandwidth/2) / nyquist
        high = (fc + bandwidth/2) / nyquist
        b, a = signal.butter(4, [low, high], btype='band')
        
        i_filtered = signal.filtfilt(b, a, i_signal)
        q_filtered = signal.filtfilt(b, a, q_signal)
        
        # Submuestrear para obtener símbolos
        symbol_rate = 10  # Símbolos por segundo
        symbol_indices = np.arange(0, n, int(fs / symbol_rate))
        symbol_indices = symbol_indices[symbol_indices < n]
        
        if len(symbol_indices) > 0:
            i_symbols = i_filtered[symbol_indices]
            q_symbols = q_filtered[symbol_indices]
        else:
            i_symbols = i_filtered[::int(fs/symbol_rate)]
            q_symbols = q_filtered[::int(fs/symbol_rate)]
        
        return i_symbols, q_symbols
    
    # Generar constelaciones
    i_before, q_before = generate_constellation(signal_noisy, fs)
    i_after, q_after = generate_constellation(signal_filtered, fs)
    
    # Constelación antes
    ax1.scatter(i_before, q_before, alpha=0.5, s=30, c='red', marker='o')
    ax1.axhline(0, color='gray', linestyle='--', alpha=0.5)
    ax1.axvline(0, color='gray', linestyle='--', alpha=0.5)
    ax1.set_title('Constelación - Con Interferencia', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Componente I')
    ax1.set_ylabel('Componente Q')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([-1.5, 1.5])
    ax1.set_ylim([-1.5, 1.5])
    
    # Constelación después
    ax2.scatter(i_after, q_after, alpha=0.5, s=30, c='blue', marker='o')
    ax2.axhline(0, color='gray', linestyle='--', alpha=0.5)
    ax2.axvline(0, color='gray', linestyle='--', alpha=0.5)
    ax2.set_title('Constelación - Después del Filtro', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Componente I')
    ax2.set_ylabel('Componente Q')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([-1.5, 1.5])
    ax2.set_ylim([-1.5, 1.5])
    
    plt.tight_layout()
    plt.savefig('img_constellation.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ======== GRÁFICA 5: ANÁLISIS DE BER Y MÉTRICAS ========
    fig5, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Métricas principales
    metrics_names = ['SNR\nMejora (dB)', 'Aislamiento\nCanal (dB)', 
                     'BER\nReducción (%)', 'Rechazo\nInterf. (dB)']
    
    metrics_values = [
        metrics['SNR_Improvement_dB'],
        metrics['Isolation_Improvement_dB'],
        metrics['BER_Improvement_Percent'],
        metrics['Interference_Rejection_Improvement_dB']
    ]
    
    colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
    bars = ax1.bar(metrics_names, metrics_values, color=colors, edgecolor='black', linewidth=2)
    
    for bar, value in zip(bars, metrics_values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{value:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax1.set_title('Métricas de Rendimiento del Filtro', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Valor')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_ylim([0, max(metrics_values) + 5])
    
    # Comparación BER
    ber_values = [metrics['BER_Before'], metrics['BER_After']]
    ber_labels = ['Antes', 'Después']
    ber_colors = ['#e74c3c', '#2ecc71']
    
    bars2 = ax2.bar(ber_labels, ber_values, color=ber_colors, edgecolor='black', linewidth=2)
    
    for bar, value in zip(bars2, ber_values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.0005,
                f'{value:.4f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax2.set_title('Tasa de Error de Bit (BER)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('BER')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim([0, max(ber_values) * 1.2 + 0.01])
    
    plt.tight_layout()
    plt.savefig('img_ber_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Todas las gráficas generadas exitosamente!")

# ============================================================================
# 7. FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """
    Función principal que ejecuta todo el flujo de trabajo.
    """
    print("=" * 80)
    print("📡 CASO 3: COMUNICACIONES POR RADIO - FILTRO FIR PASA BANDAS")
    print("=" * 80)
    
    # Parámetros
    FS = 2000  # Frecuencia de muestreo (Hz) - simulación escala reducida
    DURATION = 5  # Duración (segundos)
    LOWCUT = 95  # Frecuencia de corte inferior (Hz)
    HIGHCUT = 105  # Frecuencia de corte superior (Hz)
    NUMTAPS = 101  # Número de coeficientes (orden = 100)
    WINDOW = 'hamming'  # Tipo de ventana
    
    print("\n📋 Generando señal de radio simulada...")
    t, signal_clean, signal_noisy = generate_radio_signal(DURATION, FS)
    print(f"✅ Señal generada: {len(t)} muestras, {DURATION} segundos")
    print(f"   - Frecuencia central: 100 Hz (escala reducida)")
    print(f"   - Interferencia: canales adyacentes 99.5 Hz y 100.5 Hz")
    
    print("\n🔧 Diseñando filtro FIR pasa bandas con ventana Hamming...")
    h = design_bandpass_filter(LOWCUT, HIGHCUT, FS, NUMTAPS, WINDOW)
    print(f"✅ Filtro FIR diseñado: {NUMTAPS} taps, banda {LOWCUT}-{HIGHCUT} Hz")
    print(f"   - Ventana: {WINDOW}")
    print(f"   - Orden: {NUMTAPS - 1}")
    
    print("\n⚡ Aplicando filtro a la señal...")
    signal_filtered = apply_filter(signal_noisy, h)
    print("✅ Filtro aplicado a la señal")
    
    print("\n📊 Calculando métricas...")
    metrics = calculate_metrics(signal_clean, signal_noisy, signal_filtered, h, FS)
    
    print("\n📈 RESULTADOS:")
    print(f"   SNR Mejora:               +{metrics['SNR_Improvement_dB']:.2f} dB")
    print(f"   Correlación:              {metrics['Correlation']:.4f}")
    print(f"   Aislamiento de Canal:     +{metrics['Isolation_Improvement_dB']:.2f} dB")
    print(f"   Rechazo de Interferencia: +{metrics['Interference_Rejection_Improvement_dB']:.2f} dB")
    print(f"   BER Antes:                {metrics['BER_Before']:.4f}")
    print(f"   BER Después:              {metrics['BER_After']:.4f}")
    print(f"   Reducción BER:            {metrics['BER_Improvement_Percent']:.1f}%")
    print(f"   Energía Preservada:       {metrics['Energy_Preserved_Percent']:.2f}%")
    
    print("\n💾 Guardando datos en CSV...")
    df = pd.DataFrame({
        'Time': t,
        'Signal_Clean': signal_clean,
        'Signal_Noisy': signal_noisy,
        'Signal_Filtered': signal_filtered
    })
    df.to_csv('data_radio.csv', index=False)
    print("✅ Datos guardados en 'data_radio.csv'")
    
    print("\n📊 Generando gráficas...")
    generate_plots(t, signal_clean, signal_noisy, signal_filtered, h, FS, metrics)
    
    print("\n" + "=" * 80)
    print("✅ ¡PROCESO COMPLETADO EXITOSAMENTE!")
    print("=" * 80)
    print("\n📁 Archivos generados:")
    print("   📄 data_radio.csv - Datos completos de la señal")
    print("   🖼️  img_radio_comparison.png - Comparación de señales")
    print("   🖼️  img_filter_design.png - Diseño del filtro FIR")
    print("   🖼️  img_spectrum_analysis.png - Análisis espectral")
    print("   🖼️  img_constellation.png - Diagrama de constelación")
    print("   🖼️  img_ber_analysis.png - Análisis de BER")
    print("\n🌐 Ahora abre 'index.html' para ver la visualización interactiva")
    print("=" * 80)

if __name__ == "__main__":
    main()