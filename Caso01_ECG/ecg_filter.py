"""
================================================================================
CASO 1: MONITOREO DE ECG - FILTRO PASA BAJOS BUTTERWORTH
================================================================================
Contexto: Paciente en UCI con monitoreo cardíaco
Problema: Ruido muscular (50-100 Hz) y ruido de línea (60 Hz) contaminan la señal
Solución: Filtro Butterworth pasa bajos de orden 4 con fc = 40 Hz
Autor: [Tu Nombre]
Fecha: 2026-07-20
================================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.signal import butter, filtfilt, freqz
import pandas as pd
from scipy.fft import fft, fftfreq
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 1. GENERACIÓN DE SEÑAL ECG SIMULADA CON RUIDO
# ============================================================================

def generate_ecg_signal(duration=10, fs=1000):
    """
    Genera una señal ECG simulada con componentes realistas.
    
    Parámetros:
    - duration: Duración en segundos
    - fs: Frecuencia de muestreo en Hz
    
    Retorna:
    - t: Vector de tiempo
    - ecg_clean: Señal ECG sin ruido
    - ecg_noisy: Señal ECG con ruido
    """
    t = np.linspace(0, duration, int(fs * duration))
    ecg_clean = np.zeros_like(t)
    
    # Parámetros del ECG (basado en registros reales)
    heart_rate = 72  # Latidos por minuto
    beats_per_second = heart_rate / 60
    beat_interval = 1 / beats_per_second
    
    # Generar latidos individuales (complejo QRS)
    for i in range(int(duration * beats_per_second)):
        beat_center = i * beat_interval
        
        # Onda P (contracción auricular)
        p_wave = 0.15 * np.exp(-((t - beat_center - 0.05) / 0.02)**2)
        
        # Complejo QRS (contracción ventricular)
        qrs_complex = -0.2 * np.exp(-((t - beat_center + 0.02) / 0.01)**2)
        qrs_complex += 1.0 * np.exp(-((t - beat_center) / 0.015)**2)
        qrs_complex += -0.1 * np.exp(-((t - beat_center - 0.02) / 0.01)**2)
        
        # Onda T (repolarización ventricular)
        t_wave = 0.25 * np.exp(-((t - beat_center - 0.12) / 0.04)**2)
        
        # Onda U (repolarización tardía)
        u_wave = 0.05 * np.exp(-((t - beat_center - 0.22) / 0.06)**2)
        
        ecg_clean += p_wave + qrs_complex + t_wave + u_wave
    
    # Normalizar
    ecg_clean = ecg_clean / np.max(np.abs(ecg_clean)) * 0.8
    
    # ======== AÑADIR RUIDO REALISTA ========
    
    # 1. Ruido muscular (50-100 Hz) - EMG
    noise_emg = 0.3 * np.random.randn(len(t))
    b, a = butter(4, [50, 100], btype='band', fs=fs)
    noise_emg = filtfilt(b, a, noise_emg)
    
    # 2. Ruido de línea (60 Hz + armónicos)
    noise_line = 0.15 * np.sin(2 * np.pi * 60 * t)
    noise_line += 0.05 * np.sin(2 * np.pi * 120 * t)
    noise_line += 0.02 * np.sin(2 * np.pi * 180 * t)
    
    # 3. Ruido de movimiento (baja frecuencia)
    noise_motion = 0.1 * np.sin(2 * np.pi * 0.5 * t) + 0.05 * np.sin(2 * np.pi * 1.2 * t)
    
    # 4. Ruido blanco gaussiano
    noise_white = 0.05 * np.random.randn(len(t))
    
    # Combinar todos los ruidos
    ecg_noisy = ecg_clean + noise_emg + noise_line + noise_motion + noise_white
    
    return t, ecg_clean, ecg_noisy

# ============================================================================
# 2. DISEÑO DEL FILTRO PASA BAJOS BUTTERWORTH
# ============================================================================

def design_lowpass_filter(cutoff=40, fs=1000, order=4):
    """
    Diseña un filtro Butterworth pasa bajos.
    
    Parámetros:
    - cutoff: Frecuencia de corte en Hz
    - fs: Frecuencia de muestreo en Hz
    - order: Orden del filtro
    
    Retorna:
    - b, a: Coeficientes del filtro
    """
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
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
# 4. CÁLCULO DE MÉTRICAS DE DESEMPEÑO
# ============================================================================

def calculate_metrics(original, noisy, filtered, fs):
    """
    Calcula métricas para evaluar el rendimiento del filtro.
    
    Retorna:
    - metrics: Diccionario con todas las métricas
    """
    # Relación Señal-Ruido (SNR)
    def snr(signal, noise):
        signal_power = np.mean(signal**2)
        noise_power = np.mean(noise**2)
        return 10 * np.log10(signal_power / noise_power)
    
    # Error Cuadrático Medio (MSE)
    def mse(original, filtered):
        return np.mean((original - filtered)**2)
    
    # Correlación cruzada
    def correlation(original, filtered):
        return np.corrcoef(original, filtered)[0, 1]
    
    # Cálculos
    noise_before = noisy - original
    noise_after = filtered - original
    
    snr_before = snr(original, noise_before)
    snr_after = snr(original, noise_after)
    
    mse_value = mse(original, filtered)
    corr_value = correlation(original, filtered)
    
    # Mejora del SNR
    snr_improvement = snr_after - snr_before
    
    # Energía de la señal
    energy_before = np.sum(noisy**2)
    energy_after = np.sum(filtered**2)
    energy_preserved = (energy_after / energy_before) * 100
    
    metrics = {
        'SNR_Before_dB': snr_before,
        'SNR_After_dB': snr_after,
        'SNR_Improvement_dB': snr_improvement,
        'MSE': mse_value,
        'Correlation': corr_value,
        'Energy_Preserved_Percent': energy_preserved
    }
    
    return metrics

# ============================================================================
# 5. DETECCIÓN DE LATIDOS (QRS)
# ============================================================================

def detect_heartbeats(signal_data, fs, threshold=0.5):
    """
    Detecta los latidos cardíacos (complejos QRS) en la señal.
    
    Retorna:
    - peaks: Índices de los picos R
    - heart_rate: Frecuencia cardíaca en BPM
    """
    # Encontrar picos R (picos positivos)
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(signal_data, height=threshold, distance=fs*0.3)
    
    if len(peaks) > 1:
        # Calcular frecuencia cardíaca
        rr_intervals = np.diff(peaks) / fs
        heart_rate = 60 / np.mean(rr_intervals)
    else:
        heart_rate = 0
    
    return peaks, heart_rate

# ============================================================================
# 6. GENERACIÓN DE GRÁFICAS Y GUARDADO DE DATOS
# ============================================================================

def generate_plots(t, ecg_clean, ecg_noisy, ecg_filtered, b, a, fs, metrics):
    """
    Genera todas las gráficas necesarias para el análisis.
    """
    # Configuración de estilo
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.rcParams['figure.figsize'] = [12, 6]
    plt.rcParams['font.size'] = 12
    
    # ======== GRÁFICA 1: SEÑALES EN EL TIEMPO ========
    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Señal cruda vs señal limpia
    ax1.plot(t, ecg_clean, 'g-', linewidth=2, label='ECG Ideal (Sin ruido)', alpha=0.7)
    ax1.plot(t, ecg_noisy, 'r-', linewidth=1, label='ECG con Ruido', alpha=0.6)
    ax1.set_title('Señal ECG: Original vs Con Ruido', fontsize=16, fontweight='bold')
    ax1.set_xlabel('Tiempo (segundos)')
    ax1.set_ylabel('Amplitud (mV)')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, 5])  # Mostrar solo 5 segundos para claridad
    
    # Señal filtrada vs señal limpia
    ax2.plot(t, ecg_clean, 'g-', linewidth=2, label='ECG Ideal', alpha=0.5)
    ax2.plot(t, ecg_filtered, 'b-', linewidth=2, label='ECG Filtrado (Butterworth, fc=40Hz)', alpha=0.9)
    ax2.set_title('Señal ECG: Filtrada vs Ideal', fontsize=16, fontweight='bold')
    ax2.set_xlabel('Tiempo (segundos)')
    ax2.set_ylabel('Amplitud (mV)')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, 5])
    
    plt.tight_layout()
    plt.savefig('img_ecg_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ======== GRÁFICA 2: RESPONSABLE EN FRECUENCIA ========
    fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Respuesta en frecuencia del filtro
    w, h = freqz(b, a, worN=2000, fs=fs)
    
    ax1.semilogx(w, 20 * np.log10(abs(h)), 'b-', linewidth=2)
    ax1.axvline(40, color='r', linestyle='--', linewidth=2, label='Frecuencia de Corte (40 Hz)')
    ax1.axhline(-3, color='gray', linestyle=':', alpha=0.7, label='-3 dB')
    ax1.set_title('Respuesta en Frecuencia del Filtro Pasa Bajos (Orden 4)', fontsize=16, fontweight='bold')
    ax1.set_xlabel('Frecuencia (Hz)')
    ax1.set_ylabel('Magnitud (dB)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([1, 500])
    ax1.set_ylim([-80, 5])
    
    # Espectro de la señal (antes y después)
    # Calcular FFT
    n = len(t)
    freq = fftfreq(n, 1/fs)
    fft_noisy = np.abs(fft(ecg_noisy)) / n
    fft_filtered = np.abs(fft(ecg_filtered)) / n
    
    ax2.plot(freq[:n//2], 20 * np.log10(fft_noisy[:n//2] + 1e-10), 
             'r-', linewidth=1.5, alpha=0.7, label='Antes del Filtro')
    ax2.plot(freq[:n//2], 20 * np.log10(fft_filtered[:n//2] + 1e-10), 
             'b-', linewidth=2, label='Después del Filtro')
    ax2.axvline(40, color='g', linestyle='--', linewidth=2, label='Frecuencia de Corte (40 Hz)')
    ax2.set_title('Espectro de Frecuencia: Antes vs Después del Filtrado', fontsize=16, fontweight='bold')
    ax2.set_xlabel('Frecuencia (Hz)')
    ax2.set_ylabel('Magnitud (dB)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, 200])
    
    plt.tight_layout()
    plt.savefig('img_frequency_response.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ======== GRÁFICA 3: DETECCIÓN DE LATIDOS ========
    peaks, heart_rate = detect_heartbeats(ecg_filtered, fs)
    
    fig3, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Señal filtrada con picos detectados
    ax1.plot(t, ecg_filtered, 'b-', linewidth=1.5, label='ECG Filtrado')
    ax1.plot(t[peaks], ecg_filtered[peaks], 'r*', markersize=15, 
             label=f'Latidos Detectados (HR: {heart_rate:.1f} BPM)')
    ax1.set_title('Detección de Latidos Cardíacos (Complejos QRS)', fontsize=16, fontweight='bold')
    ax1.set_xlabel('Tiempo (segundos)')
    ax1.set_ylabel('Amplitud (mV)')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, 5])
    
    # Histograma de intervalos RR
    if len(peaks) > 1:
        rr_intervals = np.diff(peaks) / fs * 1000  # en milisegundos
        ax2.hist(rr_intervals, bins=20, color='blue', alpha=0.7, edgecolor='black')
        ax2.axvline(np.mean(rr_intervals), color='red', linestyle='--', 
                   linewidth=2, label=f'Media: {np.mean(rr_intervals):.0f} ms')
        ax2.set_title('Histograma de Intervalos RR', fontsize=16, fontweight='bold')
        ax2.set_xlabel('Intervalo RR (ms)')
        ax2.set_ylabel('Frecuencia')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('img_heart_detection.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ======== GRÁFICA 4: ANÁLISIS DE RUIDO ========
    fig4, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Ruido antes y después del filtrado
    noise_before = ecg_noisy - ecg_clean
    noise_after = ecg_filtered - ecg_clean
    
    ax1.plot(t, noise_before, 'r-', linewidth=1, alpha=0.7, label='Ruido Original')
    ax1.plot(t, noise_after, 'b-', linewidth=1, alpha=0.7, label='Ruido Residual')
    ax1.set_title('Análisis de Ruido: Antes vs Después', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Tiempo (segundos)')
    ax1.set_ylabel('Amplitud (mV)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, 3])
    
    # Barras de métricas
    metrics_names = ['SNR\nMejora (dB)', 'Correlación\n(0-1)', 'Energía\nPreservada (%)']
    metrics_values = [metrics['SNR_Improvement_dB'], 
                      metrics['Correlation'], 
                      metrics['Energy_Preserved_Percent']]
    
    colors = ['#2ecc71', '#3498db', '#e74c3c']
    bars = ax2.bar(metrics_names, metrics_values, color=colors, edgecolor='black', linewidth=2)
    
    # Añadir valores en las barras
    for bar, value in zip(bars, metrics_values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{value:.1f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax2.set_title('Métricas de Rendimiento del Filtro', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Valor')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim([0, max(metrics_values) + 5])
    
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
    print("🚀 CASO 1: MONITOREO DE ECG - FILTRO PASA BAJOS BUTTERWORTH")
    print("=" * 80)
    print("\n📋 Generando señal ECG simulada...")
    
    # Parámetros
    FS = 1000  # Frecuencia de muestreo (Hz)
    DURATION = 10  # Duración (segundos)
    CUTOFF = 40  # Frecuencia de corte (Hz)
    ORDER = 4  # Orden del filtro
    
    # 1. Generar señal
    t, ecg_clean, ecg_noisy = generate_ecg_signal(DURATION, FS)
    print(f"✅ Señal ECG generada: {len(t)} muestras, {DURATION} segundos")
    
    # 2. Diseñar filtro
    b, a = design_lowpass_filter(CUTOFF, FS, ORDER)
    print(f"✅ Filtro Butterworth diseñado: Orden {ORDER}, fc = {CUTOFF} Hz")
    
    # 3. Aplicar filtro
    ecg_filtered = apply_filter(ecg_noisy, b, a)
    print("✅ Filtro aplicado a la señal")
    
    # 4. Calcular métricas
    metrics = calculate_metrics(ecg_clean, ecg_noisy, ecg_filtered, FS)
    print("\n📊 MÉTRICAS DE RENDIMIENTO:")
    print(f"   SNR Antes: {metrics['SNR_Before_dB']:.2f} dB")
    print(f"   SNR Después: {metrics['SNR_After_dB']:.2f} dB")
    print(f"   Mejora SNR: {metrics['SNR_Improvement_dB']:.2f} dB")
    print(f"   MSE: {metrics['MSE']:.6f}")
    print(f"   Correlación: {metrics['Correlation']:.4f}")
    print(f"   Energía Preservada: {metrics['Energy_Preserved_Percent']:.2f}%")
    
    # 5. Detectar latidos
    peaks, heart_rate = detect_heartbeats(ecg_filtered, FS)
    print(f"\n❤️  FRECUENCIA CARDÍACA DETECTADA: {heart_rate:.1f} BPM")
    print(f"   Latidos detectados: {len(peaks)} en {DURATION} segundos")
    
    # 6. Guardar datos en CSV
    df = pd.DataFrame({
        'Time': t,
        'ECG_Clean': ecg_clean,
        'ECG_Noisy': ecg_noisy,
        'ECG_Filtered': ecg_filtered
    })
    df.to_csv('data_ecg.csv', index=False)
    print("✅ Datos guardados en 'data_ecg.csv'")
    
    # 7. Generar gráficas
    print("\n📊 Generando gráficas...")
    generate_plots(t, ecg_clean, ecg_noisy, ecg_filtered, b, a, FS, metrics)
    
    print("\n" + "=" * 80)
    print("✅ ¡PROCESO COMPLETADO EXITOSAMENTE!")
    print("=" * 80)
    print("\n📁 Archivos generados:")
    print("   - data_ecg.csv (Datos completos)")
    print("   - img_ecg_comparison.png (Comparación de señales)")
    print("   - img_frequency_response.png (Respuesta en frecuencia)")
    print("   - img_heart_detection.png (Detección de latidos)")
    print("   - img_noise_analysis.png (Análisis de rendimiento)")
    print("\n🌐 Ahora abre 'index.html' para ver la visualización interactiva")
    print("=" * 80)

if __name__ == "__main__":
    main()