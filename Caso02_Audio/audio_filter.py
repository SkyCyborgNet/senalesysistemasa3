"""
================================================================================
CASO 2: RESTAURACIÓN DE AUDIO - FILTRO PASA ALTOS CHEBYSHEV
================================================================================
Contexto: Grabación histórica de discurso político (1950) con zumbido de 60Hz
Problema: Zumbido de fondo (60Hz) y ruido de grabación analógica
Solución: Filtro Chebyshev pasa altos Tipo I con fc = 80 Hz, ripple = 0.5 dB
Autor: [Tu Nombre]
Fecha: 2026-07-20
================================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.signal import cheby1, filtfilt, freqz
import pandas as pd
from scipy.fft import fft, fftfreq
from scipy.signal import spectrogram
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 1. GENERACIÓN DE SEÑAL DE AUDIO SIMULADA (DISCURSO + RUIDO)
# ============================================================================

def generate_audio_signal(duration=8, fs=8000):
    """
    Genera una señal de audio simulada (voz humana) con ruido realista.
    
    Parámetros:
    - duration: Duración en segundos
    - fs: Frecuencia de muestreo en Hz
    
    Retorna:
    - t: Vector de tiempo
    - audio_clean: Audio sin ruido
    - audio_noisy: Audio con ruido
    """
    t = np.linspace(0, duration, int(fs * duration))
    
    # ====== SEÑAL DE VOZ SIMULADA ======
    # La voz humana tiene componentes fundamentales en 80-300 Hz
    # y armónicos hasta 3.4 kHz (banda telefónica)
    
    audio_clean = np.zeros_like(t)
    
    # Frecuencias fundamentales de la voz (sílabas y fonemas)
    # Simulando un discurso político con frases
    
    # Componente 1: Voz grave (hombre) - 120 Hz
    voice_fundamental = 120
    voice_amplitude = 0.7
    
    # Generar voz con armónicos (timbre realista)
    for harmonic in range(1, 20):
        freq = voice_fundamental * harmonic
        if freq > 3400:  # Frecuencia máxima de voz
            break
        # Amplitud decrece con la frecuencia (como en voz real)
        amplitude = voice_amplitude / (harmonic * 1.5)
        # Pequeñas variaciones para simular entonación
        audio_clean += amplitude * np.sin(2 * np.pi * freq * t + np.random.randn() * 0.5)
    
    # Añadir modulación de amplitud (simulando énfasis en palabras)
    envelope = 0.5 + 0.5 * np.sin(2 * np.pi * 1.2 * t)  # Ritmo del habla ~1.2 Hz
    audio_clean *= envelope
    
    # Añadir pausas y silencios (simulando respiración y pausas)
    silence_mask = np.ones_like(t)
    for i in range(4, int(duration), 3):
        start_idx = int(i * fs)
        end_idx = int((i + 0.3) * fs)
        if end_idx < len(silence_mask):
            silence_mask[start_idx:end_idx] = 0.1
    
    audio_clean *= silence_mask
    
    # Pequeño ruido de cuantización (grabación antigua)
    audio_clean += 0.001 * np.random.randn(len(t))
    
    # Normalizar
    audio_clean = audio_clean / np.max(np.abs(audio_clean)) * 0.9
    
    # ======== AÑADIR RUIDO REALISTA ========
    
    # 1. Zumbido de 60 Hz (el problema principal)
    noise_60hz = 0.8 * np.sin(2 * np.pi * 60 * t)
    
    # 2. Armónicos del zumbido (120 Hz, 180 Hz, 240 Hz)
    noise_60hz += 0.3 * np.sin(2 * np.pi * 120 * t)
    noise_60hz += 0.15 * np.sin(2 * np.pi * 180 * t)
    noise_60hz += 0.05 * np.sin(2 * np.pi * 240 * t)
    
    # 3. Ruido de grabación analógica (ruido de cinta)
    noise_tape = 0.15 * np.random.randn(len(t))
    # Ruido coloreado (más energía en bajas frecuencias)
    b, a = signal.butter(2, 0.1, btype='low')
    noise_tape = signal.filtfilt(b, a, noise_tape)
    noise_tape *= 0.2
    
    # 4. Ruido de fondo (ambiente)
    noise_ambient = 0.05 * np.random.randn(len(t))
    
    # 5. Ruido de aguja (pops y clicks - grabación de vinilo)
    noise_pops = np.zeros_like(t)
    for _ in range(20):
        pos = np.random.randint(0, len(t))
        duration_pops = np.random.randint(10, 50)
        if pos + duration_pops < len(t):
            amplitude_pop = np.random.uniform(0.1, 0.4)
            noise_pops[pos:pos+duration_pops] += amplitude_pop * np.random.randn(duration_pops) * 0.5
    
    # Combinar todos los ruidos
    audio_noisy = audio_clean + noise_60hz + noise_tape + noise_ambient + noise_pops
    
    # Añadir saturación (grabación antigua)
    audio_noisy = np.tanh(audio_noisy * 1.2) * 0.9
    
    return t, audio_clean, audio_noisy

# ============================================================================
# 2. DISEÑO DEL FILTRO PASA ALTOS CHEBYSHEV
# ============================================================================

def design_highpass_filter(cutoff=80, fs=8000, order=4, ripple=0.5):
    """
    Diseña un filtro Chebyshev Tipo I pasa altos.
    
    Parámetros:
    - cutoff: Frecuencia de corte en Hz
    - fs: Frecuencia de muestreo en Hz
    - order: Orden del filtro
    - ripple: Ripple en banda de paso (dB)
    
    Retorna:
    - b, a: Coeficientes del filtro
    """
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = cheby1(order, ripple, normal_cutoff, btype='high', analog=False)
    return b, a

# ============================================================================
# 3. APLICACIÓN DEL FILTRO
# ============================================================================

def apply_filter(signal_data, b, a):
    """
    Aplica el filtro a la señal usando filtfilt (fase cero).
    """
    return filtfilt(b, a, signal_data)

# ============================================================================
# 4. CÁLCULO DE MÉTRICAS DE DESEMPEÑO
# ============================================================================

def calculate_metrics(original, noisy, filtered, fs):
    """
    Calcula métricas para evaluar el rendimiento del filtro.
    """
    def snr(signal, noise):
        signal_power = np.mean(signal**2)
        noise_power = np.mean(noise**2)
        if noise_power == 0:
            return 100
        return 10 * np.log10(signal_power / noise_power)
    
    def mse(original, filtered):
        return np.mean((original - filtered)**2)
    
    def correlation(original, filtered):
        return np.corrcoef(original, filtered)[0, 1]
    
    def thd(signal, fs, freq_band=[0, 100]):
        """Distorsión armónica total en banda específica"""
        n = len(signal)
        freq = fftfreq(n, 1/fs)
        fft_signal = np.abs(fft(signal)) / n
        
        # Solo considerar frecuencias positivas
        mask = (freq >= freq_band[0]) & (freq <= freq_band[1])
        power_total = np.sum(fft_signal[mask]**2)
        
        # Energía en 60 Hz y armónicos
        freqs_60hz = [60, 120, 180, 240]
        power_harmonics = 0
        for f in freqs_60hz:
            idx = np.argmin(np.abs(freq - f))
            if idx < len(fft_signal):
                # Sumar energía en un rango estrecho
                idx_range = 5
                power_harmonics += np.sum(fft_signal[max(0, idx-idx_range):min(len(fft_signal), idx+idx_range)]**2)
        
        if power_total > 0:
            thd_percent = (power_harmonics / power_total) * 100
        else:
            thd_percent = 0
            
        return thd_percent
    
    # Cálculos
    noise_before = noisy - original
    noise_after = filtered - original
    
    snr_before = snr(original, noise_before)
    snr_after = snr(original, noise_after)
    
    mse_value = mse(original, filtered)
    corr_value = correlation(original, filtered)
    
    # THD antes y después
    thd_before = thd(noisy, fs)
    thd_after = thd(filtered, fs)
    
    # Mejora del SNR
    snr_improvement = snr_after - snr_before
    
    # Energía de la señal
    energy_before = np.sum(noisy**2)
    energy_after = np.sum(filtered**2)
    energy_preserved = (energy_after / energy_before) * 100
    
    # Reducción del zumbido de 60 Hz
    def calculate_60hz_energy(signal, fs):
        n = len(signal)
        freq = fftfreq(n, 1/fs)
        fft_signal = np.abs(fft(signal)) / n
        
        # Energía en 60 Hz (± 2 Hz)
        idx_60hz = np.argmin(np.abs(freq - 60))
        if idx_60hz < len(fft_signal):
            idx_range = 20  # ±2 Hz a 8000 Hz de sampleo
            energy_60hz = np.sum(fft_signal[max(0, idx_60hz-idx_range):min(len(fft_signal), idx_60hz+idx_range)]**2)
        else:
            energy_60hz = 0
            
        return energy_60hz
    
    energy_60hz_before = calculate_60hz_energy(noisy, fs)
    energy_60hz_after = calculate_60hz_energy(filtered, fs)
    
    if energy_60hz_before > 0:
        hum_reduction = 10 * np.log10(energy_60hz_before / (energy_60hz_after + 1e-10))
    else:
        hum_reduction = 0
    
    metrics = {
        'SNR_Before_dB': snr_before,
        'SNR_After_dB': snr_after,
        'SNR_Improvement_dB': snr_improvement,
        'MSE': mse_value,
        'Correlation': corr_value,
        'Energy_Preserved_Percent': energy_preserved,
        'THD_Before_Percent': thd_before,
        'THD_After_Percent': thd_after,
        'Hum_Reduction_dB': hum_reduction
    }
    
    return metrics

# ============================================================================
# 5. GENERACIÓN DE GRÁFICAS
# ============================================================================

def generate_plots(t, audio_clean, audio_noisy, audio_filtered, b, a, fs, metrics):
    """
    Genera todas las gráficas necesarias para el análisis.
    """
    # Configuración de estilo
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.rcParams['figure.figsize'] = [12, 6]
    plt.rcParams['font.size'] = 12
    
    # ======== GRÁFICA 1: SEÑALES EN EL TIEMPO ========
    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Mostrar solo 2 segundos para claridad
    time_limit = 2
    idx_limit = int(time_limit * fs)
    
    # Señal con ruido vs señal limpia
    ax1.plot(t[:idx_limit], audio_clean[:idx_limit], 'g-', linewidth=2, 
             label='Audio Ideal (Discurso)', alpha=0.7)
    ax1.plot(t[:idx_limit], audio_noisy[:idx_limit], 'r-', linewidth=1, 
             label='Audio con Ruido (60Hz + Grabación)', alpha=0.6)
    ax1.set_title('Señal de Audio: Original vs Con Ruido', fontsize=16, fontweight='bold')
    ax1.set_xlabel('Tiempo (segundos)')
    ax1.set_ylabel('Amplitud')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, time_limit])
    
    # Señal filtrada vs señal limpia
    ax2.plot(t[:idx_limit], audio_clean[:idx_limit], 'g-', linewidth=2, 
             label='Audio Ideal', alpha=0.5)
    ax2.plot(t[:idx_limit], audio_filtered[:idx_limit], 'b-', linewidth=2, 
             label=f'Audio Filtrado (Chebyshev, fc=80Hz)', alpha=0.9)
    ax2.set_title('Señal de Audio: Filtrada vs Ideal', fontsize=16, fontweight='bold')
    ax2.set_xlabel('Tiempo (segundos)')
    ax2.set_ylabel('Amplitud')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, time_limit])
    
    plt.tight_layout()
    plt.savefig('img_audio_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ======== GRÁFICA 2: RESPUESTA EN FRECUENCIA ========
    fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Respuesta en frecuencia del filtro
    w, h = freqz(b, a, worN=2000, fs=fs)
    
    ax1.semilogx(w, 20 * np.log10(abs(h)), 'b-', linewidth=2)
    ax1.axvline(80, color='r', linestyle='--', linewidth=2, 
                label='Frecuencia de Corte (80 Hz)')
    ax1.axhline(-3, color='gray', linestyle=':', alpha=0.7, label='-3 dB')
    ax1.axhline(-0.5, color='orange', linestyle=':', alpha=0.7, 
                label=f'Ripple = {0.5} dB')
    ax1.set_title('Respuesta en Frecuencia - Filtro Pasa Altos Chebyshev (Orden 4)', 
                  fontsize=16, fontweight='bold')
    ax1.set_xlabel('Frecuencia (Hz)')
    ax1.set_ylabel('Magnitud (dB)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([1, 5000])
    ax1.set_ylim([-80, 5])
    
    # Espectro de la señal (antes y después)
    n = len(t)
    freq = fftfreq(n, 1/fs)
    fft_noisy = np.abs(fft(audio_noisy)) / n
    fft_filtered = np.abs(fft(audio_filtered)) / n
    
    # Mostrar solo hasta 500 Hz (para ver el zumbido y voz)
    freq_limit = 500
    idx_freq = int(freq_limit / (fs/n))
    
    ax2.plot(freq[:idx_freq], 20 * np.log10(fft_noisy[:idx_freq] + 1e-10), 
             'r-', linewidth=1.5, alpha=0.7, label='Antes del Filtro')
    ax2.plot(freq[:idx_freq], 20 * np.log10(fft_filtered[:idx_freq] + 1e-10), 
             'b-', linewidth=2, label='Después del Filtro')
    ax2.axvline(80, color='g', linestyle='--', linewidth=2, 
                label='Frecuencia de Corte (80 Hz)')
    ax2.axvline(60, color='orange', linestyle=':', linewidth=2, alpha=0.7, 
                label='Zumbido de 60 Hz')
    ax2.set_title('Espectro de Frecuencia: Antes vs Después del Filtrado', 
                  fontsize=16, fontweight='bold')
    ax2.set_xlabel('Frecuencia (Hz)')
    ax2.set_ylabel('Magnitud (dB)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, 500])
    
    plt.tight_layout()
    plt.savefig('img_frequency_response.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ======== GRÁFICA 3: ESPECTROGRAMA ========
    fig3, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Espectrograma antes
    f_spect, t_spect, Sxx_spect = spectrogram(audio_noisy, fs, nperseg=512, noverlap=256)
    ax1.pcolormesh(t_spect, f_spect, 10 * np.log10(Sxx_spect + 1e-10), 
                   shading='gouraud', cmap='inferno')
    ax1.set_title('Espectrograma - Audio con Ruido', fontsize=16, fontweight='bold')
    ax1.set_xlabel('Tiempo (segundos)')
    ax1.set_ylabel('Frecuencia (Hz)')
    ax1.set_ylim([0, 500])
    ax1.axhline(60, color='cyan', linestyle='--', linewidth=2, alpha=0.7, 
                label='Zumbido 60 Hz')
    ax1.legend()
    
    # Espectrograma después
    f_spect, t_spect, Sxx_spect = spectrogram(audio_filtered, fs, nperseg=512, noverlap=256)
    ax2.pcolormesh(t_spect, f_spect, 10 * np.log10(Sxx_spect + 1e-10), 
                   shading='gouraud', cmap='inferno')
    ax2.set_title('Espectrograma - Audio Filtrado', fontsize=16, fontweight='bold')
    ax2.set_xlabel('Tiempo (segundos)')
    ax2.set_ylabel('Frecuencia (Hz)')
    ax2.set_ylim([0, 500])
    ax2.axhline(80, color='lime', linestyle='--', linewidth=2, alpha=0.7, 
                label='Corte 80 Hz')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('img_spectrogram_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ======== GRÁFICA 4: ANÁLISIS DE RUIDO Y MÉTRICAS ========
    fig4, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Análisis de ruido
    idx_limit_zoom = int(0.5 * fs)
    ax1.plot(t[:idx_limit_zoom], audio_noisy[:idx_limit_zoom] - audio_clean[:idx_limit_zoom], 
             'r-', linewidth=1, alpha=0.7, label='Ruido Original')
    ax1.plot(t[:idx_limit_zoom], audio_filtered[:idx_limit_zoom] - audio_clean[:idx_limit_zoom], 
             'b-', linewidth=1, alpha=0.7, label='Ruido Residual')
    ax1.set_title('Análisis de Ruido: Antes vs Después', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Tiempo (segundos)')
    ax1.set_ylabel('Amplitud')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, 0.5])
    
    # Barras de métricas
    metrics_names = ['SNR\nMejora (dB)', 'Correlación\n(0-1)', 'THD\nReducción (%)', 
                     'Energía\nPreservada (%)']
    
    # Calcular reducción de THD
    thd_reduction = metrics['THD_Before_Percent'] - metrics['THD_After_Percent']
    
    metrics_values = [
        metrics['SNR_Improvement_dB'],
        metrics['Correlation'],
        max(0, thd_reduction),
        metrics['Energy_Preserved_Percent']
    ]
    
    colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
    bars = ax2.bar(metrics_names, metrics_values, color=colors, edgecolor='black', linewidth=2)
    
    # Añadir valores en las barras
    for bar, value in zip(bars, metrics_values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{value:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax2.set_title('Métricas de Rendimiento del Filtro', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Valor')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim([0, max(metrics_values) + 5])
    
    plt.tight_layout()
    plt.savefig('img_noise_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ======== GRÁFICA 5: PRESERVACIÓN DE VOZ ========
    fig5, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
    
    # Análisis de la voz (80-3400 Hz)
    def frequency_band_energy(signal, fs, f_low, f_high):
        n = len(signal)
        freq = fftfreq(n, 1/fs)
        fft_signal = np.abs(fft(signal)) / n
        mask = (freq >= f_low) & (freq <= f_high)
        return np.sum(fft_signal[mask]**2)
    
    # Energía en banda de voz vs ruido
    voice_energy_clean = frequency_band_energy(audio_clean, fs, 80, 3400)
    voice_energy_noisy = frequency_band_energy(audio_noisy, fs, 80, 3400)
    voice_energy_filtered = frequency_band_energy(audio_filtered, fs, 80, 3400)
    
    # Energía en banda de ruido (0-80 Hz)
    noise_energy_clean = frequency_band_energy(audio_clean, fs, 0, 80)
    noise_energy_noisy = frequency_band_energy(audio_noisy, fs, 0, 80)
    noise_energy_filtered = frequency_band_energy(audio_filtered, fs, 0, 80)
    
    labels = ['Audio\nIdeal', 'Con\nRuido', 'Filtrado']
    voice_energies = [voice_energy_clean, voice_energy_noisy, voice_energy_filtered]
    noise_energies = [noise_energy_clean, noise_energy_noisy, noise_energy_filtered]
    
    x = np.arange(len(labels))
    width = 0.35
    
    ax1.bar(x - width/2, voice_energies, width, label='Energía de Voz (80-3400 Hz)', 
            color='#2ecc71', edgecolor='black', linewidth=1.5)
    ax1.bar(x + width/2, noise_energies, width, label='Energía de Ruido (0-80 Hz)', 
            color='#e74c3c', edgecolor='black', linewidth=1.5)
    ax1.set_title('Preservación de Voz vs Eliminación de Ruido', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.set_ylabel('Energía')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Índice de inteligibilidad
    intelligibility_clean = voice_energy_clean / (voice_energy_clean + noise_energy_clean + 1e-10)
    intelligibility_noisy = voice_energy_noisy / (voice_energy_noisy + noise_energy_noisy + 1e-10)
    intelligibility_filtered = voice_energy_filtered / (voice_energy_filtered + noise_energy_filtered + 1e-10)
    
    intelligibility_values = [intelligibility_clean, intelligibility_noisy, intelligibility_filtered]
    
    colors_qual = ['#2ecc71', '#e74c3c', '#3498db']
    bars2 = ax2.bar(labels, intelligibility_values, color=colors_qual, edgecolor='black', linewidth=2)
    
    # Añadir valores
    for bar, value in zip(bars2, intelligibility_values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{value:.1%}', ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax2.set_title('Índice de Inteligibilidad del Discurso', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Inteligibilidad (0-1)')
    ax2.set_ylim([0, 1.1])
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.axhline(0.7, color='orange', linestyle='--', linewidth=2, alpha=0.7, 
                label='Umbral de Inteligibilidad')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('img_voice_preservation.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Todas las gráficas generadas exitosamente!")

# ============================================================================
# 6. FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """
    Función principal que ejecuta todo el flujo de trabajo.
    """
    print("=" * 80)
    print("🎵 CASO 2: RESTAURACIÓN DE AUDIO - FILTRO PASA ALTOS CHEBYSHEV")
    print("=" * 80)
    
    # Parámetros
    FS = 8000  # Frecuencia de muestreo (Hz) - calidad de telefonía
    DURATION = 8  # Duración (segundos)
    CUTOFF = 80  # Frecuencia de corte (Hz)
    ORDER = 4  # Orden del filtro
    RIPPLE = 0.5  # Ripple en dB
    
    print("\n📋 Generando señal de audio simulada...")
    t, audio_clean, audio_noisy = generate_audio_signal(DURATION, FS)
    print(f"✅ Audio generado: {len(t)} muestras, {DURATION} segundos")
    print(f"   - Voz: 80-3400 Hz")
    print(f"   - Zumbido principal: 60 Hz + armónicos")
    
    print("\n🔧 Diseñando filtro Chebyshev pasa altos...")
    b, a = design_highpass_filter(CUTOFF, FS, ORDER, RIPPLE)
    print(f"✅ Filtro Chebyshev diseñado: Orden {ORDER}, fc = {CUTOFF} Hz, Ripple = {RIPPLE} dB")
    
    print("\n⚡ Aplicando filtro a la señal...")
    audio_filtered = apply_filter(audio_noisy, b, a)
    print("✅ Filtro aplicado a la señal")
    
    print("\n📊 Calculando métricas...")
    metrics = calculate_metrics(audio_clean, audio_noisy, audio_filtered, FS)
    
    print("\n📈 RESULTADOS:")
    print(f"   SNR Antes:       {metrics['SNR_Before_dB']:.2f} dB")
    print(f"   SNR Después:     {metrics['SNR_After_dB']:.2f} dB")
    print(f"   Mejora SNR:      +{metrics['SNR_Improvement_dB']:.2f} dB")
    print(f"   Correlación:     {metrics['Correlation']:.4f}")
    print(f"   THD Antes:       {metrics['THD_Before_Percent']:.2f}%")
    print(f"   THD Después:     {metrics['THD_After_Percent']:.2f}%")
    print(f"   Reducción THD:   {metrics['THD_Before_Percent'] - metrics['THD_After_Percent']:.2f}%")
    print(f"   Reducción Zumbido: {metrics['Hum_Reduction_dB']:.2f} dB")
    print(f"   Energía Preservada: {metrics['Energy_Preserved_Percent']:.2f}%")
    
    print("\n💾 Guardando datos en CSV...")
    df = pd.DataFrame({
        'Time': t,
        'Audio_Clean': audio_clean,
        'Audio_Noisy': audio_noisy,
        'Audio_Filtered': audio_filtered
    })
    df.to_csv('data_audio.csv', index=False)
    print("✅ Datos guardados en 'data_audio.csv'")
    
    print("\n📊 Generando gráficas...")
    generate_plots(t, audio_clean, audio_noisy, audio_filtered, b, a, FS, metrics)
    
    print("\n" + "=" * 80)
    print("✅ ¡PROCESO COMPLETADO EXITOSAMENTE!")
    print("=" * 80)
    print("\n📁 Archivos generados:")
    print("   📄 data_audio.csv - Datos completos del audio")
    print("   🖼️  img_audio_comparison.png - Comparación de señales")
    print("   🖼️  img_frequency_response.png - Respuesta en frecuencia")
    print("   🖼️  img_spectrogram_comparison.png - Espectrogramas")
    print("   🖼️  img_noise_analysis.png - Análisis de rendimiento")
    print("   🖼️  img_voice_preservation.png - Preservación de voz")
    print("\n🌐 Ahora abre 'index.html' para ver la visualización interactiva")
    print("=" * 80)

if __name__ == "__main__":
    main()