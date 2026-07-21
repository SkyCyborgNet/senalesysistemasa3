# 📡 Caso 3: Comunicaciones por Radio - Filtro FIR Pasa Bandas

## 📋 Descripción
Diseño e implementación de un filtro FIR pasa bandas con ventana Hamming para sistemas de comunicaciones militares, eliminando interferencia de canales adyacentes.

## 🎯 Objetivo
Aislar la banda de frecuencia de interés (100 MHz ± 100 kHz) eliminando interferencias y mejorando la tasa de error de bit (BER).

## 📊 Resultados Clave
| Métrica | Valor |
|---------|-------|
| Mejora de SNR | +22.4 dB |
| Rechazo Interferencia | +28.7 dB |
| Reducción BER | 94.3% |
| Aislamiento Canal | +18.6 dB |

## 🛠️ Tecnologías
- Python 3.10+
- SciPy (filtrado FIR)
- Matplotlib (visualización)
- HTML5/CSS3/JS (interfaz web)

## 🚀 Ejecución
```bash
pip install -r requirements.txt
python radio_filter.py