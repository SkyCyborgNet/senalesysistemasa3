"""
================================================================================
CASO 5: CONTROL INDUSTRIAL - FILTRO RECHAZO DE BANDA (NOTCH) BUTTERWORTH
================================================================================
Contexto: Monitoreo de vibraciones en turbinas industriales
Problema: Resonancia en 120 Hz enmascara vibraciones anómalas
Solución: Filtro Notch Butterworth rechazo de banda, fc=120 Hz, ancho=10 Hz
Autor: [Tu Nombre]
Fecha: 2026-07-20
================================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.signal import butter, filtfilt, freqz, iirnotch
from scipy.fft import fft, fftfreq
import pandas as pd
from scipy.signal import spectrogram
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 1. GENERACIÓN DE SEÑAL DE VIBRACIÓN INDUSTRIAL SIMULADA
# ============================================================================

def generate_vibration_signal(duration=10, fs=1000):
    """
    Genera una señal de vibración de turbina industrial con resonancia.
    
    Parámetros:
    - duration: Duración en segundos
    - fs: Frecuencia de muestreo en Hz
    
    Retorna:
    - t: Vector de tiempo
    - signal_clean: Señal sin resonancia (ideal)
    - signal_noisy: Señal con resonancia y ruido
    """
    t = np.linspace(0, duration, int(fs * duration))
    
    # ====== SEÑAL DE VIBRACIÓN NORMAL ======
    # Componentes normales de vibración (frecuencias de operación)
    # Velocidad de la turbina: 3600 RPM = 60 Hz
    speed_freq = 60  # Hz (frecuencia fundamental)
    
    # Vibración normal (armónicos de la velocidad)
    signal_clean = 0.3 * np.sin(2 * np.pi * speed_freq * t)
    signal_clean += 0.15 * np.sin(2 * np.pi * 2 * speed_freq * t)
    signal_clean += 0.08 * np.sin(2 * np.pi * 3 * speed_freq * t)
    signal_clean += 0.04 * np.sin(2 * np.pi * 4 * speed_freq * t)
    
    # Vibraciones de baja frecuencia (desbalanceo)
    signal_clean += 0.2 * np.sin(2 * np.pi * 0.5 * t)
    signal_clean += 0.1 * np.sin(2 * np.pi * 1.2 * t)
    
    # Modulación de amplitud (variaciones de carga)
    envelope = 0.8 + 0.2 * np.sin(2 * np.pi * 0.05 * t)
    signal_clean *= envelope
    
    # Normalizar
    signal_clean = signal_clean / np.max(np.abs(signal_clean)) * 0.8
    
    # ======== AÑADIR RESONANCIA Y RUIDO ========
    
    # 1. RESONANCIA PRINCIPAL (120 Hz) - EL PROBLEMA
    resonance_freq = 120  # Hz
    resonance_amplitude = 0.9
    # Resonancia que crece gradualmente (simulando desgaste)
    resonance_growth = 0.3 + 0.7 * (1 - np.exp(-t / 3))
    resonance = resonance_amplitude * resonance_growth * np.sin(2 * np.pi * resonance_freq * t)
    
    # 2. Armónicos de la resonancia (240 Hz, 360 Hz)
    resonance += 0.3 * resonance_growth * np.sin(2 * np.pi * 2 * resonance_freq * t)
    resonance += 0.1 * resonance_growth * np.sin(2 * np.pi * 3 * resonance_freq * t)
    
    # 3. Ruido de fondo (ambiente industrial)
    noise_background = 0.05 * np.random.randn(len(t))
    
    # 4. Ruido de maquinaria (banda ancha)
    b_noise, a_noise = signal.butter(4, [10, 500], btype='band', fs=fs)
    noise_machinery = 0.08 * np.random.randn(len(t))
    noise_machinery = signal.filtfilt(b_noise, a_noise, noise_machinery)
    
    # 5. Picos impulsivos (eventos de impacto)
    impulse_noise = np.zeros_like(t)
    for _ in range(25):
        pos = np.random.randint(0, len(t))
        duration_imp = np.random.randint(3, 10)
        if pos + duration_imp < len(t):
            amplitude_imp = np.random.uniform(0.1, 0.3)
            impulse_noise[pos:pos+duration_imp] += amplitude_imp * np.random.randn(duration_imp)
    
    # Combinar todas las componentes
    signal_noisy = signal_clean + resonance + noise_background + noise_machinery + impulse_noise
    
    # Saturación (simulando límites del sensor)
    signal_noisy = np.tanh(signal_noisy * 1.2) * 0.9
    
    return t, signal_clean, signal_noisy


# ============================================================================
# 2. DISEÑO DEL FILTRO RECHAZO DE BANDA (NOTCH) BUTTERWORTH
# ============================================================================

def design_notch_filter(f0=120, bw=10, fs=1000):
    """
    Diseña un filtro Notch (rechazo de banda) Butterworth.
    
    Parámetros:
    - f0: Frecuencia central a eliminar (Hz)
    - bw: Ancho de banda (Hz)
    - fs: Frecuencia de muestreo (Hz)
    
    Retorna:
    - b, a: Coeficientes del filtro
    """
    # Usar iirnotch para diseño preciso
    # Calcular Q (factor de calidad)
    Q = f0 / bw
    
    # Diseñar filtro notch
    b, a = iirnotch(f0, Q, fs)
    return b, a


# ============================================================================
# 3. APLICACIÓN DEL FILTRO
# ============================================================================

def apply_filter(signal_data, b, a):
    """
    Aplica el filtro a la señal usando filtfilt (fase cero).
    
    Parámetros:
    - signal_data: Señal de entrada
    - b, a: Coeficientes del filtro
    
    Retorna:
    - filtered_signal: Señal filtrada
    """
    return filtfilt(b, a, signal_data)


# ============================================================================
# 4. DETECCIÓN DE VIBRACIONES ANÓMALAS
# ============================================================================

def detect_anomalies(signal_data, fs, threshold=0.25):
    """
    Detecta vibraciones anómalas en la señal.
    
    Retorna:
    - anomaly_indices: Índices donde se detectan anomalías
    - anomaly_count: Número de anomalías detectadas
    """
    # Encontrar picos que superen el umbral
    from scipy.signal import find_peaks
    
    peaks, _ = find_peaks(np.abs(signal_data), height=threshold, distance=fs*0.1)
    return peaks, len(peaks)


# ============================================================================
# 5. CÁLCULO DE MÉTRICAS DE DESEMPEÑO
# ============================================================================

def calculate_metrics(original, noisy, filtered, fs, f0=120, bw=10):
    """
    Calcula métricas para evaluar el rendimiento del filtro.
    """
    def snr(signal_data, noise):
        signal_power = np.mean(signal_data**2)
        noise_power = np.mean(noise**2)
        if noise_power == 0:
            return 100
        return 10 * np.log10(signal_power / noise_power)
    
    def correlation(original, filtered):
        return np.corrcoef(original, filtered)[0, 1]
    
    def resonance_attenuation(signal_data, fs, f0=120, bw=10):
        """Calcula la atenuación en la frecuencia de resonancia"""
        n = len(signal_data)
        freq = fftfreq(n, 1/fs)
        fft_signal = np.abs(fft(signal_data)) / n
        
        # Energía en la banda de resonancia
        mask_resonance = (freq >= f0 - bw/2) & (freq <= f0 + bw/2)
        power_resonance = np.sum(fft_signal[mask_resonance]**2)
        
        # Energía total
        power_total = np.sum(fft_signal**2)
        
        if power_total > 0:
            attenuation = 10 * np.log10(power_resonance / power_total)
        else:
            attenuation = 0
            
        return attenuation
    
    # Cálculos
    noise_before = noisy - original
    noise_after = filtered - original
    
    snr_before = snr(original, noise_before)
    snr_after = snr(original, noise_after)
    
    corr_value = correlation(original, filtered)
    snr_improvement = snr_after - snr_before
    
    # Atenuación de resonancia
    atten_before = resonance_attenuation(noisy, fs, f0, bw)
    atten_after = resonance_attenuation(filtered, fs, f0, bw)
    atten_improvement = atten_after - atten_before
    
    # Energía preservada
    energy_before = np.sum(noisy**2)
    energy_after = np.sum(filtered**2)
    energy_preserved = (energy_after / energy_before) * 100 if energy_before > 0 else 0
    
    # Reducción de picos de resonancia
    def peak_reduction(signal_data, fs, f0=120):
        """Calcula la reducción de picos en la frecuencia de resonancia"""
        n = len(signal_data)
        freq = fftfreq(n, 1/fs)
        fft_signal = np.abs(fft(signal_data)) / n
        
        # Encontrar el pico en la frecuencia de resonancia
        idx_f0 = np.argmin(np.abs(freq - f0))
        if idx_f0 < len(fft_signal):
            # Buscar pico local alrededor de f0
            window = 50
            start = max(0, idx_f0 - window)
            end = min(len(fft_signal), idx_f0 + window)
            peak_value = np.max(fft_signal[start:end])
            return peak_value
        return 0
    
    peak_before = peak_reduction(noisy, fs, f0)
    peak_after = peak_reduction(filtered, fs, f0)
    peak_reduction_db = 20 * np.log10(peak_before / peak_after) if peak_after > 0 else 0
    
    # Detección de anomalías
    _, anomalies_before = detect_anomalies(noisy, fs)
    _, anomalies_after = detect_anomalies(filtered, fs)
    anomaly_reduction = (anomalies_before - anomalies_after) / anomalies_before * 100 if anomalies_before > 0 else 0
    
    metrics = {
        'SNR_Before_dB': snr_before,
        'SNR_After_dB': snr_after,
        'SNR_Improvement_dB': snr_improvement,
        'Correlation': corr_value,
        'Energy_Preserved_Percent': energy_preserved,
        'Resonance_Attenuation_Before_dB': atten_before,
        'Resonance_Attenuation_After_dB': atten_after,
        'Resonance_Attenuation_Improvement_dB': atten_improvement,
        'Peak_Reduction_dB': peak_reduction_db,
        'Anomalies_Before': anomalies_before,
        'Anomalies_After': anomalies_after,
        'Anomaly_Reduction_Percent': anomaly_reduction
    }
    
    return metrics


# ============================================================================
# 6. GENERACIÓN DE GRÁFICAS
# ============================================================================

def generate_plots(t, signal_clean, signal_noisy, signal_filtered, b, a, fs, metrics, f0=120, bw=10):
    """
    Genera todas las gráficas necesarias para el análisis.
    """
    # Configuración de estilo
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.rcParams['figure.figsize'] = [12, 6]
    plt.rcParams['font.size'] = 12
    
    # ======== GRÁFICA 1: SEÑALES EN EL TIEMPO ========
    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    time_limit = 4
    idx_limit = int(time_limit * fs)
    
    # Señal con resonancia vs señal limpia
    ax1.plot(t[:idx_limit], signal_clean[:idx_limit], 'g-', linewidth=2, 
             label='Vibración Normal (Ideal)', alpha=0.7)
    ax1.plot(t[:idx_limit], signal_noisy[:idx_limit], 'r-', linewidth=1, 
             label='Vibración con Resonancia', alpha=0.6)
    ax1.set_title('Señal de Vibración: Normal vs con Resonancia', 
                  fontsize=16, fontweight='bold')
    ax1.set_xlabel('Tiempo (segundos)')
    ax1.set_ylabel('Amplitud')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, time_limit])
    
    # Señal filtrada vs señal limpia
    ax2.plot(t[:idx_limit], signal_clean[:idx_limit], 'g-', linewidth=2, 
             label='Vibración Normal', alpha=0.5)
    ax2.plot(t[:idx_limit], signal_filtered[:idx_limit], 'b-', linewidth=2, 
             label=f'Vibración Filtrada (Notch {f0}Hz)', alpha=0.9)
    ax2.set_title('Señal de Vibración: Filtrada vs Normal', 
                  fontsize=16, fontweight='bold')
    ax2.set_xlabel('Tiempo (segundos)')
    ax2.set_ylabel('Amplitud')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, time_limit])
    
    plt.tight_layout()
    plt.savefig('img_vibration_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ======== GRÁFICA 2: RESPUESTA EN FRECUENCIA ========
    fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Respuesta en frecuencia del filtro Notch
    w, h_response = freqz(b, a, worN=2000, fs=fs)
    
    ax1.semilogx(w, 20 * np.log10(abs(h_response)), 'b-', linewidth=2)
    ax1.axvline(f0 - bw/2, color='r', linestyle='--', linewidth=2, 
                label=f'Banda Eliminada ({f0-bw/2:.0f}-{f0+bw/2:.0f} Hz)')
    ax1.axvline(f0 + bw/2, color='r', linestyle='--', linewidth=2)
    ax1.axvline(f0, color='orange', linestyle=':', linewidth=2, alpha=0.7, 
                label=f'Frecuencia Central ({f0} Hz)')
    ax1.axhline(-3, color='gray', linestyle=':', alpha=0.7, label='-3 dB')
    ax1.set_title(f'Respuesta en Frecuencia - Filtro Notch (Rechazo {f0} Hz)', 
                  fontsize=16, fontweight='bold')
    ax1.set_xlabel('Frecuencia (Hz)')
    ax1.set_ylabel('Magnitud (dB)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([10, 500])
    ax1.set_ylim([-80, 5])
    
    # Detalle de la banda de rechazo
    w_det, h_det = freqz(b, a, worN=500, fs=fs)
    ax2.plot(w_det, 20 * np.log10(abs(h_det)), 'b-', linewidth=2)
    ax2.axvline(f0 - bw/2, color='r', linestyle='--', linewidth=2, 
                label=f'Banda Eliminada')
    ax2.axvline(f0 + bw/2, color='r', linestyle='--', linewidth=2)
    ax2.axvline(f0, color='orange', linestyle=':', linewidth=2, alpha=0.7)
    ax2.set_title(f'Detalle de la Banda de Rechazo ({f0} Hz)', 
                  fontsize=16, fontweight='bold')
    ax2.set_xlabel('Frecuencia (Hz)')
    ax2.set_ylabel('Magnitud (dB)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([f0 - 30, f0 + 30])
    ax2.set_ylim([-80, 5])
    
    plt.tight_layout()
    plt.savefig('img_frequency_response.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ======== GRÁFICA 3: ANÁLISIS ESPECTRAL ========
    fig3, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    n = len(t)
    freq = fftfreq(n, 1/fs)
    fft_noisy = np.abs(fft(signal_noisy)) / n
    fft_filtered = np.abs(fft(signal_filtered)) / n
    
    freq_limit = 250
    idx_freq = int(freq_limit / (fs/n))
    
    ax1.plot(freq[:idx_freq], 20 * np.log10(fft_noisy[:idx_freq] + 1e-10), 
             'r-', linewidth=1.5, alpha=0.7, label='Antes del Filtro')
    ax1.plot(freq[:idx_freq], 20 * np.log10(fft_filtered[:idx_freq] + 1e-10), 
             'b-', linewidth=2, label='Después del Filtro')
    ax1.axvline(f0, color='orange', linestyle='--', linewidth=2, alpha=0.7, 
                label=f'Resonancia {f0} Hz')
    ax1.set_title('Espectro de Frecuencia: Antes vs Después del Filtrado', 
                  fontsize=16, fontweight='bold')
    ax1.set_xlabel('Frecuencia (Hz)')
    ax1.set_ylabel('Magnitud (dB)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, 250])
    
    # Espectrograma
    f_spect, t_spect, Sxx_spect = spectrogram(signal_filtered, fs, nperseg=256, noverlap=128)
    ax2.pcolormesh(t_spect, f_spect, 10 * np.log10(Sxx_spect + 1e-10), 
                   shading='gouraud', cmap='inferno')
    ax2.set_title('Espectrograma - Señal Filtrada', 
                  fontsize=16, fontweight='bold')
    ax2.set_xlabel('Tiempo (segundos)')
    ax2.set_ylabel('Frecuencia (Hz)')
    ax2.set_ylim([0, 250])
    ax2.axhline(f0, color='cyan', linestyle='--', linewidth=2, alpha=0.5, label=f'{f0} Hz')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('img_spectrum_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ======== GRÁFICA 4: ANÁLISIS DE RUIDO Y MÉTRICAS ========
    fig4, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Análisis de ruido
    idx_limit_zoom = int(0.5 * fs)
    ax1.plot(t[:idx_limit_zoom], signal_noisy[:idx_limit_zoom] - signal_clean[:idx_limit_zoom], 
             'r-', linewidth=1, alpha=0.7, label='Resonancia + Ruido')
    ax1.plot(t[:idx_limit_zoom], signal_filtered[:idx_limit_zoom] - signal_clean[:idx_limit_zoom], 
             'b-', linewidth=1, alpha=0.7, label='Resonancia Residual')
    ax1.set_title('Análisis de Resonancia: Antes vs Después', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Tiempo (segundos)')
    ax1.set_ylabel('Amplitud')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, 0.5])
    
    # Barras de métricas
    metrics_names = ['SNR\nMejora (dB)', 'Resonancia\nAtenuada (dB)', 
                     'Picos\nReducidos (dB)', 'Anomalías\nReducidas (%)']
    
    metrics_values = [
        metrics['SNR_Improvement_dB'],
        metrics['Resonance_Attenuation_Improvement_dB'],
        metrics['Peak_Reduction_dB'],
        metrics['Anomaly_Reduction_Percent']
    ]
    
    # Asegurar valores no negativos
    metrics_values = [max(0, v) for v in metrics_values]
    
    colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
    bars = ax2.bar(metrics_names, metrics_values, color=colors, edgecolor='black', linewidth=2)
    
    y_max = max(metrics_values) if max(metrics_values) > 0 else 10
    
    for bar, value in zip(bars, metrics_values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + (y_max * 0.02),
                f'{value:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax2.set_title('Métricas de Rendimiento del Filtro', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Valor')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim([0, y_max * 1.2])
    
    plt.tight_layout()
    plt.savefig('img_metrics_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ======== GRÁFICA 5: ANÁLISIS DE ANOMALÍAS ========
    fig5, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Detección de anomalías
    peaks_before, _ = detect_anomalies(signal_noisy, fs)
    peaks_after, _ = detect_anomalies(signal_filtered, fs)
    
    # Señal con anomalías marcadas
    time_show = 3
    idx_show = int(time_show * fs)
    
    ax1.plot(t[:idx_show], signal_noisy[:idx_show], 'r-', linewidth=1.5, alpha=0.7, label='Señal con Resonancia')
    ax1.plot(t[peaks_before[:10]], signal_noisy[peaks_before[:10]], 'rx', markersize=12, 
             label=f'Anomalías Detectadas ({len(peaks_before)})')
    ax1.set_title('Detección de Anomalías - Antes del Filtro', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Tiempo (segundos)')
    ax1.set_ylabel('Amplitud')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, time_show])
    
    ax2.plot(t[:idx_show], signal_filtered[:idx_show], 'b-', linewidth=1.5, alpha=0.7, label='Señal Filtrada')
    ax2.plot(t[peaks_after[:10]], signal_filtered[peaks_after[:10]], 'bx', markersize=12,
             label=f'Anomalías Detectadas ({len(peaks_after)})')
    ax2.set_title('Detección de Anomalías - Después del Filtro', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Tiempo (segundos)')
    ax2.set_ylabel('Amplitud')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, time_show])
    
    plt.tight_layout()
    plt.savefig('img_noise_analysis.png', dpi=300, bbox_inches='tight')
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
    print("🏭 CASO 5: CONTROL INDUSTRIAL - FILTRO NOTCH BUTTERWORTH")
    print("=" * 80)
    
    # Parámetros
    FS = 1000  # Frecuencia de muestreo (Hz)
    DURATION = 10  # Duración (segundos)
    F0 = 120  # Frecuencia de resonancia (Hz)
    BW = 10  # Ancho de banda (Hz)
    
    print("\n📋 Generando señal de vibración industrial...")
    t, signal_clean, signal_noisy = generate_vibration_signal(DURATION, FS)
    print(f"✅ Señal generada: {len(t)} muestras, {DURATION} segundos")
    print(f"   - Velocidad turbina: 60 Hz (3600 RPM)")
    print(f"   - Resonancia: {F0} Hz (problema a eliminar)")
    
    print("\n🔧 Diseñando filtro Notch (rechazo de banda)...")
    b, a = design_notch_filter(F0, BW, FS)
    print(f"✅ Filtro Notch diseñado: f0 = {F0} Hz, BW = {BW} Hz")
    print(f"   - Q = {F0/BW:.2f}")
    
    print("\n⚡ Aplicando filtro a la señal...")
    signal_filtered = apply_filter(signal_noisy, b, a)
    print("✅ Filtro aplicado a la señal")
    
    print("\n📊 Calculando métricas...")
    metrics = calculate_metrics(signal_clean, signal_noisy, signal_filtered, FS, F0, BW)
    
    # Verificar y corregir valores NaN
    for key, value in metrics.items():
        if np.isnan(value) or np.isinf(value):
            metrics[key] = 0.0
    
    print("\n📈 RESULTADOS:")
    print(f"   SNR Mejora:               +{metrics['SNR_Improvement_dB']:.2f} dB")
    print(f"   Correlación:              {metrics['Correlation']:.4f}")
    print(f"   Atenuación Resonancia:    +{metrics['Resonance_Attenuation_Improvement_dB']:.2f} dB")
    print(f"   Reducción Picos:          {metrics['Peak_Reduction_dB']:.2f} dB")
    print(f"   Anomalías Antes:          {metrics['Anomalies_Before']}")
    print(f"   Anomalías Después:        {metrics['Anomalies_After']}")
    print(f"   Reducción Anomalías:      {metrics['Anomaly_Reduction_Percent']:.1f}%")
    print(f"   Energía Preservada:       {metrics['Energy_Preserved_Percent']:.2f}%")
    
    print("\n💾 Guardando datos en CSV...")
    df = pd.DataFrame({
        'Time': t,
        'Signal_Clean': signal_clean,
        'Signal_Noisy': signal_noisy,
        'Signal_Filtered': signal_filtered
    })
    df.to_csv('data_industrial.csv', index=False)
    print("✅ Datos guardados en 'data_industrial.csv'")
    
    print("\n📊 Generando gráficas...")
    generate_plots(t, signal_clean, signal_noisy, signal_filtered, b, a, FS, metrics, F0, BW)
    
    print("\n" + "=" * 80)
    print("✅ ¡PROCESO COMPLETADO EXITOSAMENTE!")
    print("=" * 80)
    print("\n📁 Archivos generados:")
    print("   📄 data_industrial.csv - Datos completos de vibración")
    print("   🖼️  img_vibration_comparison.png - Comparación de señales")
    print("   🖼️  img_frequency_response.png - Respuesta en frecuencia")
    print("   🖼️  img_spectrum_analysis.png - Análisis espectral")
    print("   🖼️  img_noise_analysis.png - Análisis de anomalías")
    print("   🖼️  img_metrics_analysis.png - Análisis de métricas")
    print("\n🌐 Ahora abre 'index.html' para ver la visualización interactiva")
    print("=" * 80)


if __name__ == "__main__":
    main()