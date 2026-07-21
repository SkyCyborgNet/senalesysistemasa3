"""
================================================================================
CASO 4: PROCESAMIENTO DE IMÁGENES MÉDICAS - FILTRO PASA BAJOS FIR CON VENTANA KAISER
================================================================================
Contexto: Escáner CT para detección de tumores
Problema: Ruido de Poisson y cuantización dificultan diagnóstico
Solución: Filtro FIR pasa bajos con ventana Kaiser, preservando bordes
Autor: [Tu Nombre]
Fecha: 2026-07-20
================================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.signal import firwin, filtfilt, freqz
from scipy.fft import fft2, fftshift, ifft2
from scipy.ndimage import convolve
from skimage import data, exposure, util
from skimage.metrics import peak_signal_noise_ratio, structural_similarity
import pandas as pd
from scipy.signal import spectrogram
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 1. GENERACIÓN DE IMAGEN MÉDICA SIMULADA
# ============================================================================

def generate_medical_image(size=256):
    """
    Genera una imagen médica simulada (similar a escáner CT) con características realistas.
    
    Parámetros:
    - size: Tamaño de la imagen (size x size)
    
    Retorna:
    - image_clean: Imagen sin ruido
    - image_noisy: Imagen con ruido
    """
    # Crear imagen base con estructuras anatómicas simuladas
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    X, Y = np.meshgrid(x, y)
    
    # ====== ESTRUCTURAS ANATÓMICAS ======
    image_clean = np.zeros((size, size))
    
    # 1. Fondo (tejido blando)
    background = 0.3 * np.ones((size, size))
    background += 0.1 * np.sin(2 * np.pi * 0.05 * X) * np.cos(2 * np.pi * 0.07 * Y)
    image_clean += background
    
    # 2. Órgano principal (ej: tumor en forma de elipse)
    organ_center_x = 0.2
    organ_center_y = 0.1
    organ_radius_x = 0.3
    organ_radius_y = 0.25
    organ = np.exp(-((X - organ_center_x)**2 / (2 * organ_radius_x**2) + 
                     (Y - organ_center_y)**2 / (2 * organ_radius_y**2)))
    organ = organ * 0.6
    image_clean += organ
    
    # 3. Tumor (pequeña masa con bordes irregulares)
    tumor_center_x = -0.1
    tumor_center_y = 0.2
    tumor_radius = 0.08
    tumor = np.exp(-((X - tumor_center_x)**2 + (Y - tumor_center_y)**2) / (2 * tumor_radius**2))
    tumor = tumor * 0.8 + 0.2 * np.random.randn(size, size) * 0.05
    tumor = np.clip(tumor, 0, 1)
    image_clean += tumor
    
    # 4. Vasos sanguíneos (estructuras lineales)
    for i in range(8):
        angle = np.random.uniform(0, 2 * np.pi)
        x0 = np.random.uniform(-0.8, 0.8)
        y0 = np.random.uniform(-0.8, 0.8)
        length = np.random.uniform(0.2, 0.5)
        width = np.random.uniform(0.02, 0.05)
        
        # Crear línea
        t = np.linspace(-length/2, length/2, 50)
        x_line = x0 + t * np.cos(angle)
        y_line = y0 + t * np.sin(angle)
        
        for j in range(len(t)):
            for k in range(len(t)):
                if j < len(x_line) and k < len(y_line):
                    idx_x = np.argmin(np.abs(x - x_line[j]))
                    idx_y = np.argmin(np.abs(y - y_line[k]))
                    if idx_x < size and idx_y < size:
                        image_clean[idx_y, idx_x] += 0.15 * np.exp(-((j - len(t)/2)**2 + (k - len(t)/2)**2) / (2 * (width * size)**2))
    
    # 5. Hueso (estructura densa)
    bone_x = 0.6
    bone_y = -0.5
    bone_radius = 0.15
    bone = np.exp(-((X - bone_x)**2 + (Y - bone_y)**2) / (2 * bone_radius**2))
    bone = bone * 0.9
    image_clean += bone
    
    # 6. Bordes de tejidos (simulando contornos)
    for i in range(5):
        cx = np.random.uniform(-0.8, 0.8)
        cy = np.random.uniform(-0.8, 0.8)
        r = np.random.uniform(0.1, 0.4)
        circle = np.exp(-((X - cx)**2 + (Y - cy)**2) / (2 * r**2))
        circle = circle * 0.3
        image_clean += circle
    
    # Normalizar imagen
    image_clean = np.clip(image_clean, 0, 1)
    image_clean = (image_clean - np.min(image_clean)) / (np.max(image_clean) - np.min(image_clean))
    
    # ======== AÑADIR RUIDO REALISTA ========
    
    # 1. Ruido de Poisson (característico en imágenes médicas)
    # Escalar para simular diferentes niveles de radiación
    scale_factor = 50
    image_scaled = image_clean * scale_factor
    noise_poisson = np.random.poisson(image_scaled) / scale_factor
    image_noisy = noise_poisson
    
    # 2. Ruido de cuantización (simulando ADC)
    quant_levels = 256
    image_noisy = np.round(image_noisy * (quant_levels - 1)) / (quant_levels - 1)
    
    # 3. Ruido gaussiano (ruido electrónico del detector)
    noise_gaussian = 0.03 * np.random.randn(size, size)
    image_noisy += noise_gaussian
    
    # 4. Ruido de sal y pimienta (artefactos)
    pepper_mask = np.random.rand(size, size) < 0.005
    salt_mask = np.random.rand(size, size) < 0.005
    image_noisy[pepper_mask] = 0
    image_noisy[salt_mask] = 1
    
    # Recortar valores
    image_noisy = np.clip(image_noisy, 0, 1)
    
    return image_clean, image_noisy


# ============================================================================
# 2. DISEÑO DEL FILTRO PASA BAJOS FIR CON VENTANA KAISER (1D para imagen 2D)
# ============================================================================

def design_2d_lowpass_filter(cutoff=0.3, size=15, beta=5.0):
    """
    Diseña un filtro FIR pasa bajos 2D con ventana Kaiser.
    
    Parámetros:
    - cutoff: Frecuencia de corte normalizada (0-1)
    - size: Tamaño del kernel (debe ser impar)
    - beta: Parámetro beta de la ventana Kaiser
    
    Retorna:
    - h: Kernel del filtro 2D
    """
    # Diseñar filtro 1D
    h1d = firwin(size, cutoff, window=('kaiser', beta), fs=2)
    
    # Crear filtro 2D a partir del 1D (filtro separable)
    h2d = np.outer(h1d, h1d)
    h2d = h2d / np.sum(h2d)  # Normalizar
    
    return h2d


# ============================================================================
# 3. APLICACIÓN DEL FILTRO A IMAGEN 2D
# ============================================================================

def apply_filter_2d(image, kernel):
    """
    Aplica el filtro 2D a la imagen usando convolución.
    
    Parámetros:
    - image: Imagen de entrada
    - kernel: Kernel del filtro
    
    Retorna:
    - filtered_image: Imagen filtrada
    """
    return convolve(image, kernel, mode='reflect')


# ============================================================================
# 4. CÁLCULO DE MÉTRICAS DE DESEMPEÑO
# ============================================================================

def calculate_metrics(original, noisy, filtered):
    """
    Calcula métricas para evaluar el rendimiento del filtro.
    """
    # PSNR (Peak Signal-to-Noise Ratio)
    psnr_before = peak_signal_noise_ratio(original, noisy)
    psnr_after = peak_signal_noise_ratio(original, filtered)
    psnr_improvement = psnr_after - psnr_before
    
    # SSIM (Structural Similarity Index)
    ssim_before = structural_similarity(original, noisy, data_range=1.0)
    ssim_after = structural_similarity(original, filtered, data_range=1.0)
    ssim_improvement = ssim_after - ssim_before
    
    # MSE (Mean Squared Error)
    mse_before = np.mean((original - noisy)**2)
    mse_after = np.mean((original - filtered)**2)
    mse_reduction = (mse_before - mse_after) / mse_before * 100 if mse_before > 0 else 0
    
    # Energía preservada
    energy_before = np.sum(noisy**2)
    energy_after = np.sum(filtered**2)
    energy_preserved = (energy_after / energy_before) * 100 if energy_before > 0 else 0
    
    # Detección de bordes (sobel)
    from scipy.ndimage import sobel
    edges_original = np.sqrt(sobel(original, axis=0)**2 + sobel(original, axis=1)**2)
    edges_filtered = np.sqrt(sobel(filtered, axis=0)**2 + sobel(filtered, axis=1)**2)
    
    edge_preservation = np.sum(edges_filtered) / np.sum(edges_original) * 100 if np.sum(edges_original) > 0 else 0
    
    # Correlación
    correlation = np.corrcoef(original.flatten(), filtered.flatten())[0, 1]
    
    metrics = {
        'PSNR_Before_dB': psnr_before,
        'PSNR_After_dB': psnr_after,
        'PSNR_Improvement_dB': psnr_improvement,
        'SSIM_Before': ssim_before,
        'SSIM_After': ssim_after,
        'SSIM_Improvement': ssim_improvement,
        'MSE_Before': mse_before,
        'MSE_After': mse_after,
        'MSE_Reduction_Percent': mse_reduction,
        'Energy_Preserved_Percent': energy_preserved,
        'Edge_Preservation_Percent': edge_preservation,
        'Correlation': correlation
    }
    
    return metrics


# ============================================================================
# 5. GENERACIÓN DE GRÁFICAS
# ============================================================================

def generate_plots(image_clean, image_noisy, image_filtered, kernel, fs, metrics):
    """
    Genera todas las gráficas necesarias para el análisis.
    """
    # Configuración de estilo
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.rcParams['figure.figsize'] = [12, 6]
    plt.rcParams['font.size'] = 12
    
    # ======== GRÁFICA 1: IMÁGENES COMPARATIVAS ========
    fig1, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # Imagen original
    axes[0, 0].imshow(image_clean, cmap='gray', vmin=0, vmax=1)
    axes[0, 0].set_title('Imagen Original (Ideal)', fontsize=14, fontweight='bold')
    axes[0, 0].axis('off')
    
    # Imagen con ruido
    axes[0, 1].imshow(image_noisy, cmap='gray', vmin=0, vmax=1)
    axes[0, 1].set_title('Imagen con Ruido', fontsize=14, fontweight='bold')
    axes[0, 1].axis('off')
    
    # Imagen filtrada
    axes[0, 2].imshow(image_filtered, cmap='gray', vmin=0, vmax=1)
    axes[0, 2].set_title('Imagen Filtrada (Kaiser)', fontsize=14, fontweight='bold')
    axes[0, 2].axis('off')
    
    # Histograma de la imagen original
    axes[1, 0].hist(image_clean.flatten(), bins=50, alpha=0.7, color='green', edgecolor='black')
    axes[1, 0].set_title('Histograma - Original', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Intensidad')
    axes[1, 0].set_ylabel('Frecuencia')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Histograma de la imagen con ruido
    axes[1, 1].hist(image_noisy.flatten(), bins=50, alpha=0.7, color='red', edgecolor='black')
    axes[1, 1].set_title('Histograma - Con Ruido', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('Intensidad')
    axes[1, 1].set_ylabel('Frecuencia')
    axes[1, 1].grid(True, alpha=0.3)
    
    # Histograma de la imagen filtrada
    axes[1, 2].hist(image_filtered.flatten(), bins=50, alpha=0.7, color='blue', edgecolor='black')
    axes[1, 2].set_title('Histograma - Filtrada', fontsize=12, fontweight='bold')
    axes[1, 2].set_xlabel('Intensidad')
    axes[1, 2].set_ylabel('Frecuencia')
    axes[1, 2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('img_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ======== GRÁFICA 2: RESPUESTA EN FRECUENCIA DEL FILTRO ========
    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Respuesta en frecuencia del kernel 2D
    # Para visualización, usar el kernel 1D
    kernel_1d = kernel[:, kernel.shape[1]//2]
    w, h_response = freqz(kernel_1d, 1, worN=2000, fs=2)
    
    ax1.plot(w, 20 * np.log10(abs(h_response) + 1e-10), 'b-', linewidth=2)
    ax1.axvline(0.3, color='r', linestyle='--', linewidth=2, 
                label='Frecuencia de Corte (0.3)')
    ax1.axhline(-3, color='gray', linestyle=':', alpha=0.7, label='-3 dB')
    ax1.axhline(-6, color='orange', linestyle=':', alpha=0.7, label='-6 dB')
    ax1.set_title('Respuesta en Frecuencia - Filtro FIR Kaiser (1D equivalente)', 
                  fontsize=16, fontweight='bold')
    ax1.set_xlabel('Frecuencia Normalizada')
    ax1.set_ylabel('Magnitud (dB)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0, 1])
    ax1.set_ylim([-80, 5])
    
    # Kernel 2D
    im = ax2.imshow(kernel, cmap='RdBu_r', interpolation='nearest')
    ax2.set_title(f'Kernel 2D del Filtro ({kernel.shape[0]}x{kernel.shape[1]})', 
                  fontsize=16, fontweight='bold')
    ax2.set_xlabel('Columnas')
    ax2.set_ylabel('Filas')
    plt.colorbar(im, ax=ax2, label='Amplitud')
    
    plt.tight_layout()
    plt.savefig('img_frequency_response.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ======== GRÁFICA 3: ANÁLISIS DE RUIDO Y MÉTRICAS ========
    fig3, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Ruido residual
    noise_before = image_noisy - image_clean
    noise_after = image_filtered - image_clean
    
    # Mostrar ruido como imágenes
    ax1.imshow(noise_before, cmap='RdBu_r', vmin=-0.3, vmax=0.3)
    ax1.set_title('Ruido - Antes del Filtro', fontsize=14, fontweight='bold')
    ax1.axis('off')
    ax1.text(0.5, -0.05, f'RMSE: {np.sqrt(np.mean(noise_before**2)):.4f}', 
             transform=ax1.transAxes, ha='center', fontsize=12)
    
    ax2.imshow(noise_after, cmap='RdBu_r', vmin=-0.3, vmax=0.3)
    ax2.set_title('Ruido - Después del Filtro', fontsize=14, fontweight='bold')
    ax2.axis('off')
    ax2.text(0.5, -0.05, f'RMSE: {np.sqrt(np.mean(noise_after**2)):.4f}', 
             transform=ax2.transAxes, ha='center', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('img_noise_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ======== GRÁFICA 4: PRESERVACIÓN DE BORDES ========
    fig4, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    
    from scipy.ndimage import sobel
    
    # Detectar bordes
    edges_original = np.sqrt(sobel(image_clean, axis=0)**2 + sobel(image_clean, axis=1)**2)
    edges_noisy = np.sqrt(sobel(image_noisy, axis=0)**2 + sobel(image_noisy, axis=1)**2)
    edges_filtered = np.sqrt(sobel(image_filtered, axis=0)**2 + sobel(image_filtered, axis=1)**2)
    
    # Normalizar para visualización
    def normalize_edges(edges):
        if np.max(edges) > 0:
            return edges / np.max(edges)
        return edges
    
    ax1.imshow(normalize_edges(edges_original), cmap='hot', vmin=0, vmax=1)
    ax1.set_title('Bordes - Original', fontsize=14, fontweight='bold')
    ax1.axis('off')
    
    ax2.imshow(normalize_edges(edges_noisy), cmap='hot', vmin=0, vmax=1)
    ax2.set_title('Bordes - Con Ruido', fontsize=14, fontweight='bold')
    ax2.axis('off')
    
    ax3.imshow(normalize_edges(edges_filtered), cmap='hot', vmin=0, vmax=1)
    ax3.set_title('Bordes - Filtrado', fontsize=14, fontweight='bold')
    ax3.axis('off')
    
    plt.tight_layout()
    plt.savefig('img_edge_preservation.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # ======== GRÁFICA 5: MÉTRICAS DE RENDIMIENTO ========
    fig5, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Métricas principales
    metrics_names = ['PSNR\nMejora (dB)', 'SSIM\nMejora', 'MSE\nReducción (%)', 
                     'Bordes\nPreservados (%)']
    
    metrics_values = [
        metrics['PSNR_Improvement_dB'],
        metrics['SSIM_Improvement'] * 10,  # Escalar para visualización
        metrics['MSE_Reduction_Percent'],
        metrics['Edge_Preservation_Percent']
    ]
    
    # Asegurar valores no negativos
    metrics_values = [max(0, v) for v in metrics_values]
    
    colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
    bars = ax1.bar(metrics_names, metrics_values, color=colors, edgecolor='black', linewidth=2)
    
    y_max = max(metrics_values) if max(metrics_values) > 0 else 10
    
    for bar, value in zip(bars, metrics_values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + (y_max * 0.02),
                f'{value:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax1.set_title('Métricas de Rendimiento del Filtro', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Valor')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_ylim([0, y_max * 1.2])
    
    # Comparación PSNR y SSIM
    psnr_values = [metrics['PSNR_Before_dB'], metrics['PSNR_After_dB']]
    ssim_values = [metrics['SSIM_Before'], metrics['SSIM_After']]
    
    x = np.arange(2)
    width = 0.35
    
    bars1 = ax2.bar(x - width/2, psnr_values, width, label='PSNR (dB)', 
                    color='#3498db', edgecolor='black', linewidth=1.5)
    bars2 = ax2.bar(x + width/2, ssim_values, width, label='SSIM', 
                    color='#2ecc71', edgecolor='black', linewidth=1.5)
    
    ax2.set_title('Comparación de Calidad de Imagen', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(['Antes', 'Después'])
    ax2.set_ylabel('Valor')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Añadir valores en las barras
    for bar, value in zip(bars1, psnr_values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{value:.1f}', ha='center', va='bottom', fontsize=10)
    
    for bar, value in zip(bars2, ssim_values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{value:.3f}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('img_metrics_analysis.png', dpi=300, bbox_inches='tight')
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
    print("🏥 CASO 4: PROCESAMIENTO DE IMÁGENES MÉDICAS - FILTRO FIR KAISER")
    print("=" * 80)
    
    # Parámetros
    IMAGE_SIZE = 256  # Tamaño de la imagen
    CUTOFF = 0.3  # Frecuencia de corte normalizada
    KERNEL_SIZE = 15  # Tamaño del kernel (debe ser impar)
    BETA = 5.0  # Parámetro beta de la ventana Kaiser
    
    print("\n📋 Generando imagen médica simulada...")
    image_clean, image_noisy = generate_medical_image(IMAGE_SIZE)
    print(f"✅ Imagen generada: {IMAGE_SIZE}x{IMAGE_SIZE} píxeles")
    print(f"   - Estructuras: tejido, órgano, tumor, vasos, hueso")
    print(f"   - Ruido: Poisson + Gaussiano + Sal y Pimienta")
    
    print("\n🔧 Diseñando filtro FIR pasa bajos con ventana Kaiser...")
    kernel = design_2d_lowpass_filter(CUTOFF, KERNEL_SIZE, BETA)
    print(f"✅ Filtro FIR diseñado: {KERNEL_SIZE}x{KERNEL_SIZE} kernel")
    print(f"   - Frecuencia de corte: {CUTOFF}")
    print(f"   - Beta Kaiser: {BETA}")
    
    print("\n⚡ Aplicando filtro a la imagen...")
    image_filtered = apply_filter_2d(image_noisy, kernel)
    print("✅ Filtro aplicado a la imagen")
    
    print("\n📊 Calculando métricas...")
    metrics = calculate_metrics(image_clean, image_noisy, image_filtered)
    
    # Verificar y corregir valores NaN
    for key, value in metrics.items():
        if np.isnan(value) or np.isinf(value):
            metrics[key] = 0.0
    
    print("\n📈 RESULTADOS:")
    print(f"   PSNR Antes:              {metrics['PSNR_Before_dB']:.2f} dB")
    print(f"   PSNR Después:            {metrics['PSNR_After_dB']:.2f} dB")
    print(f"   Mejora PSNR:             +{metrics['PSNR_Improvement_dB']:.2f} dB")
    print(f"   SSIM Antes:              {metrics['SSIM_Before']:.4f}")
    print(f"   SSIM Después:            {metrics['SSIM_After']:.4f}")
    print(f"   Mejora SSIM:             +{metrics['SSIM_Improvement']:.4f}")
    print(f"   Reducción MSE:           {metrics['MSE_Reduction_Percent']:.1f}%")
    print(f"   Bordes Preservados:      {metrics['Edge_Preservation_Percent']:.1f}%")
    print(f"   Correlación:             {metrics['Correlation']:.4f}")
    print(f"   Energía Preservada:      {metrics['Energy_Preserved_Percent']:.2f}%")
    
    print("\n💾 Guardando imágenes...")
    # Guardar imágenes individuales
    plt.imsave('img_original_image.png', image_clean, cmap='gray', vmin=0, vmax=1)
    plt.imsave('img_noisy_image.png', image_noisy, cmap='gray', vmin=0, vmax=1)
    plt.imsave('img_filtered_image.png', image_filtered, cmap='gray', vmin=0, vmax=1)
    print("✅ Imágenes guardadas:")
    print("   - img_original_image.png")
    print("   - img_noisy_image.png")
    print("   - img_filtered_image.png")
    
    print("\n📊 Generando gráficas...")
    generate_plots(image_clean, image_noisy, image_filtered, kernel, 2, metrics)
    
    print("\n" + "=" * 80)
    print("✅ ¡PROCESO COMPLETADO EXITOSAMENTE!")
    print("=" * 80)
    print("\n📁 Archivos generados:")
    print("   🖼️  img_original_image.png - Imagen original")
    print("   🖼️  img_noisy_image.png - Imagen con ruido")
    print("   🖼️  img_filtered_image.png - Imagen filtrada")
    print("   🖼️  img_comparison.png - Comparación de imágenes")
    print("   🖼️  img_frequency_response.png - Respuesta en frecuencia")
    print("   🖼️  img_metrics_analysis.png - Análisis de métricas")
    print("   🖼️  img_edge_preservation.png - Preservación de bordes")
    print("   🖼️  img_noise_analysis.png - Análisis de ruido")
    print("\n🌐 Ahora abre 'index.html' para ver la visualización interactiva")
    print("=" * 80)


if __name__ == "__main__":
    main()