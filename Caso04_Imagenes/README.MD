# 🏥 Caso 4: Procesamiento de Imágenes Médicas

## 📋 Descripción
Diseño e implementación de un filtro FIR pasa bajos con ventana Kaiser para procesamiento de imágenes médicas (escáner CT), reduciendo ruido mientras se preservan bordes.

## 🎯 Objetivo
Mejorar la calidad de imágenes médicas para facilitar la detección temprana de tumores y reducir diagnósticos erróneos.

## 📊 Resultados Clave
| Métrica | Valor |
|---------|-------|
| Mejora PSNR | +12.8 dB |
| Mejora SSIM | +0.15 |
| Reducción MSE | 68.4% |
| Bordes Preservados | 72.3% |

## 🛠️ Tecnologías
- Python 3.10+
- SciPy (filtrado)
- scikit-image (métricas)
- Matplotlib (visualización)
- HTML5/CSS3/JS (interfaz web)

## 🚀 Ejecución
```bash
pip install -r requirements.txt
python image_filter.py