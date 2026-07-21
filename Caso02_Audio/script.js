/**
 * SCRIPT.JS - Caso 2: Restauración de Audio
 * Interactividad, animaciones y controles para audio
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // ============================================================
    // 1. NAVEGACIÓN RESPONSIVE
    // ============================================================
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
    
    // Cerrar menú al hacer click en un enlace
    document.querySelectorAll('.nav-menu a').forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('active');
        });
    });
    
    // ============================================================
    // 2. SCROLL SUAVE Y DESTACADO DE SECCIONES
    // ============================================================
    const sections = document.querySelectorAll('.section, .hero');
    const navLinks = document.querySelectorAll('.nav-menu a');
    
    window.addEventListener('scroll', function() {
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (window.pageYOffset >= sectionTop - 150) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });
    
    // ============================================================
    // 3. ANIMACIONES DE SECCIONES AL SCROLL
    // ============================================================
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.section').forEach(section => {
        observer.observe(section);
    });
    
    // ============================================================
    // 4. CONTROLES DEL FILTRO DE AUDIO (Simulación interactiva)
    // ============================================================
    const cutoffSlider = document.getElementById('cutoffSlider');
    const orderSlider = document.getElementById('orderSlider');
    const rippleSlider = document.getElementById('rippleSlider');
    const cutoffDisplay = document.getElementById('cutoffDisplay');
    const orderDisplay = document.getElementById('orderDisplay');
    const rippleDisplay = document.getElementById('rippleDisplay');
    const applyBtn = document.getElementById('applyFilterBtn');
    
    // Actualizar displays de los sliders
    if (cutoffSlider && cutoffDisplay) {
        cutoffSlider.addEventListener('input', function() {
            cutoffDisplay.textContent = this.value;
        });
    }
    
    if (orderSlider && orderDisplay) {
        orderSlider.addEventListener('input', function() {
            orderDisplay.textContent = this.value;
        });
    }
    
    if (rippleSlider && rippleDisplay) {
        rippleSlider.addEventListener('input', function() {
            rippleDisplay.textContent = parseFloat(this.value).toFixed(1);
        });
    }
    
    // Aplicar filtro (simulación)
    if (applyBtn) {
        applyBtn.addEventListener('click', function() {
            const cutoff = cutoffSlider ? parseInt(cutoffSlider.value) : 80;
            const order = orderSlider ? parseInt(orderSlider.value) : 4;
            const ripple = rippleSlider ? parseFloat(rippleSlider.value) : 0.5;
            
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando audio...';
            this.disabled = true;
            
            // Simular procesamiento de audio
            setTimeout(() => {
                // Calcular métricas basadas en parámetros
                // Mejor SNR con mayor orden y menor ripple
                const baseSNR = 15 + (order * 2) + (ripple * 3) + (cutoff / 20);
                const snrImprovement = Math.min(baseSNR, 45);
                
                // Mejor correlación con mayor orden
                const baseCorr = 0.85 + (order / 30) - (ripple / 10);
                const correlation = Math.min(Math.max(baseCorr, 0.70), 0.98);
                
                // Mejor reducción THD con mayor orden
                const baseTHD = 40 + (order * 6) + (ripple * 5);
                const thdReduction = Math.min(baseTHD, 85);
                
                // Preservación de energía (disminuye con mayor orden)
                const baseEnergy = 90 - (order * 2) - (ripple * 3);
                const energyPreserved = Math.max(Math.min(baseEnergy, 95), 60);
                
                // Calcular métricas derivadas
                const snrBefore = -8.2;
                const snrAfter = snrBefore + snrImprovement;
                const thdBefore = 72.5;
                const thdAfter = Math.max(thdBefore - thdReduction, 2);
                const intelligibilityBefore = 23;
                const intelligibilityAfter = Math.min(intelligibilityBefore + (snrImprovement * 2.5), 95);
                
                // Actualizar métricas principales
                document.getElementById('metricSnr').textContent = snrImprovement.toFixed(1);
                document.getElementById('metricCorr').textContent = correlation.toFixed(2);
                document.getElementById('metricEnergy').textContent = energyPreserved.toFixed(1);
                document.getElementById('metricTHD').textContent = thdReduction.toFixed(1);
                
                // Actualizar tarjetas de simulación
                const snrBeforeEl = document.getElementById('snrBefore');
                const snrAfterEl = document.getElementById('snrAfter');
                const thdBeforeEl = document.getElementById('thdBefore');
                const thdAfterEl = document.getElementById('thdAfter');
                const intelligibilityBeforeEl = document.getElementById('intelligibilityBefore');
                const intelligibilityAfterEl = document.getElementById('intelligibilityAfter');
                
                if (snrBeforeEl) snrBeforeEl.textContent = `${snrBefore.toFixed(1)} dB`;
                if (snrAfterEl) snrAfterEl.textContent = `${snrAfter.toFixed(1)} dB`;
                if (thdBeforeEl) thdBeforeEl.textContent = `${thdBefore.toFixed(1)}%`;
                if (thdAfterEl) thdAfterEl.textContent = `${thdAfter.toFixed(1)}%`;
                if (intelligibilityBeforeEl) intelligibilityBeforeEl.textContent = `${intelligibilityBefore}%`;
                if (intelligibilityAfterEl) intelligibilityAfterEl.textContent = `${intelligibilityAfter.toFixed(1)}%`;
                
                // Actualizar badges de tendencia
                const trendBadges = document.querySelectorAll('.metric-trend');
                if (trendBadges.length >= 4) {
                    // SNR
                    trendBadges[0].innerHTML = `<i class="fas fa-arrow-up"></i> +${Math.round((snrImprovement / 8) * 100)}%`;
                    // Correlación
                    trendBadges[1].innerHTML = `<i class="fas fa-arrow-up"></i> ${correlation > 0.90 ? 'Excelente' : 'Buena'}`;
                    // Energía
                    trendBadges[2].innerHTML = `<i class="fas fa-arrow-${energyPreserved > 80 ? 'up' : 'down'}"></i> ${energyPreserved > 80 ? 'Alta' : 'Media'}`;
                    // THD
                    trendBadges[3].innerHTML = `<i class="fas fa-arrow-up"></i> +${Math.round((thdReduction / 72) * 100)}%`;
                }
                
                this.innerHTML = '<i class="fas fa-check"></i> Audio Restaurado';
                this.disabled = false;
                
                setTimeout(() => {
                    this.innerHTML = '<i class="fas fa-sync"></i> Aplicar Filtro';
                }, 2000);
            }, 2000);
        });
    }
    
    // ============================================================
    // 5. EFECTO DE ZOOM EN IMÁGENES
    // ============================================================
    document.querySelectorAll('.sim-image').forEach(container => {
        container.addEventListener('click', function() {
            const img = this.querySelector('img');
            if (img) {
                // Crear modal para imagen ampliada
                const modal = document.createElement('div');
                modal.style.cssText = `
                    position: fixed;
                    inset: 0;
                    background: rgba(0,0,0,0.9);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 9999;
                    cursor: pointer;
                    padding: 40px;
                `;
                
                const modalImg = document.createElement('img');
                modalImg.src = img.src;
                modalImg.style.cssText = `
                    max-width: 90%;
                    max-height: 90%;
                    border-radius: 8px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
                `;
                
                modal.appendChild(modalImg);
                document.body.appendChild(modal);
                
                modal.addEventListener('click', function() {
                    this.remove();
                });
                
                // Cerrar con tecla ESC
                document.addEventListener('keydown', function handler(e) {
                    if (e.key === 'Escape') {
                        modal.remove();
                        document.removeEventListener('keydown', handler);
                    }
                });
            }
        });
    });
    
    // ============================================================
    // 6. CONTADOR ANIMADO (Efecto visual)
    // ============================================================
    function animateCounter(element, target, duration = 2000, prefix = '', suffix = '') {
        if (!element) return;
        const start = 0;
        const startTime = performance.now();
        
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = start + (target - start) * eased;
            
            if (target % 1 === 0) {
                element.textContent = prefix + Math.round(current) + suffix;
            } else {
                element.textContent = prefix + current.toFixed(target.toString().split('.')[1]?.length || 0) + suffix;
            }
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        
        requestAnimationFrame(update);
    }
    
    // Animar métricas al hacer scroll
    const metricObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                const text = element.textContent;
                const value = parseFloat(text);
                const suffix = text.includes('%') ? '%' : '';
                const prefix = text.includes('+') ? '+' : '';
                
                if (!isNaN(value)) {
                    element.textContent = prefix + '0' + suffix;
                    animateCounter(element, value, 1500, prefix, suffix);
                }
                metricObserver.unobserve(element);
            }
        });
    }, { threshold: 0.5 });
    
    document.querySelectorAll('.metric-value').forEach(el => {
        metricObserver.observe(el);
    });
    
    // ============================================================
    // 7. SCROLL TO TOP (Botón flotante)
    // ============================================================
    const scrollBtn = document.createElement('button');
    scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollBtn.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: var(--secondary, #f39c12);
        color: white;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(243, 156, 18, 0.3);
        transition: all 0.3s ease;
        opacity: 0;
        transform: translateY(20px);
        z-index: 999;
    `;
    
    document.body.appendChild(scrollBtn);
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 500) {
            scrollBtn.style.opacity = '1';
            scrollBtn.style.transform = 'translateY(0)';
        } else {
            scrollBtn.style.opacity = '0';
            scrollBtn.style.transform = 'translateY(20px)';
        }
    });
    
    scrollBtn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    
    // ============================================================
    // 8. TOOLTIP PARA BADGES (Información adicional)
    // ============================================================
    document.querySelectorAll('.footer-badge, .analysis-tag, .sim-badge, .chart-badge').forEach(el => {
        el.addEventListener('mouseenter', function(e) {
            const tooltip = document.createElement('div');
            tooltip.style.cssText = `
                position: fixed;
                background: var(--dark, #1a1a2e);
                color: white;
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 0.8rem;
                z-index: 9999;
                box-shadow: 0 4px 20px rgba(0,0,0,0.2);
                pointer-events: none;
                max-width: 300px;
                border: 1px solid rgba(243, 156, 18, 0.2);
            `;
            
            let text = '';
            const badgeText = el.textContent.trim();
            
            if (el.classList.contains('footer-badge')) {
                text = 'Información adicional sobre el proyecto de restauración';
            } else if (el.classList.contains('analysis-tag')) {
                const tags = {
                    'Alto Impacto': 'Mejora significativa en la calidad del audio',
                    'Alta Fidelidad': 'Preserva la esencia y calidad de la voz original',
                    'Preservación Cultural': 'Protege el patrimonio histórico y cultural',
                    'Calidad Profesional': 'Cumple con estándares de la industria'
                };
                text = tags[badgeText] || 'Categoría de impacto del análisis';
            } else if (el.classList.contains('sim-badge')) {
                text = badgeText === 'CON RUIDO' ? 
                    'Audio original con zumbido de 60 Hz y ruido de grabación' : 
                    'Audio procesado con el filtro Chebyshev pasa altos';
            } else if (el.classList.contains('chart-badge')) {
                text = 'Visualización en el dominio tiempo-frecuencia';
            }
            
            tooltip.textContent = text || 'Más información';
            document.body.appendChild(tooltip);
            
            const rect = el.getBoundingClientRect();
            tooltip.style.top = (rect.bottom + 10) + 'px';
            tooltip.style.left = Math.min(
                rect.left + rect.width/2 - tooltip.offsetWidth/2,
                window.innerWidth - tooltip.offsetWidth - 20
            ) + 'px';
            
            el.addEventListener('mouseleave', function() {
                tooltip.remove();
            }, { once: true });
        });
    });
    
    // ============================================================
    // 9. EFECTO DE ONDA DE AUDIO EN TARJETAS
    // ============================================================
    document.querySelectorAll('.sim-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            const wave = this.querySelector('.audio-wave polyline');
            if (wave) {
                wave.style.animationDuration = '1.2s';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            const wave = this.querySelector('.audio-wave polyline');
            if (wave) {
                wave.style.animationDuration = '3s';
            }
        });
    });
    
    // ============================================================
    // 10. EFECTO DE VIBRACIÓN EN EL DISCO DE VINILO
    // ============================================================
    const vinyl = document.querySelector('.vinyl-record');
    if (vinyl) {
        vinyl.addEventListener('mouseenter', function() {
            const spin = this.querySelector('.vinyl-spin');
            if (spin) {
                spin.style.animationDuration = '2s';
            }
        });
        
        vinyl.addEventListener('mouseleave', function() {
            const spin = this.querySelector('.vinyl-spin');
            if (spin) {
                spin.style.animationDuration = '4s';
            }
        });
    }
    
    // ============================================================
    // 11. SIMULADOR DE REPRODUCCIÓN DE AUDIO (Visual)
    // ============================================================
    let isPlaying = false;
    let audioInterval = null;
    
    // Crear botón de reproducción en la sección de simulación
    const simControls = document.querySelector('.sim-controls');
    if (simControls) {
        const playBtn = document.createElement('button');
        playBtn.className = 'btn btn-secondary';
        playBtn.style.marginTop = '16px';
        playBtn.innerHTML = '<i class="fas fa-play"></i> Reproducir Audio (Simulación)';
        playBtn.id = 'playAudioBtn';
        
        const controlsContainer = simControls.querySelector('.control-group');
        if (controlsContainer) {
            controlsContainer.after(playBtn);
        }
        
        playBtn.addEventListener('click', function() {
            isPlaying = !isPlaying;
            
            if (isPlaying) {
                this.innerHTML = '<i class="fas fa-stop"></i> Detener Reproducción';
                this.style.borderColor = '#e74c3c';
                
                // Simular ondas de audio
                const waves = document.querySelectorAll('.audio-wave polyline');
                waves.forEach(wave => {
                    wave.style.animationDuration = '0.8s';
                    wave.style.stroke = '#2ecc71';
                });
                
                // Animar el disco
                const spin = document.querySelector('.vinyl-spin');
                if (spin) {
                    spin.style.animationDuration = '2s';
                    spin.style.borderColor = '#2ecc71';
                }
                
                // Simular "reproducción" con cambio de color
                let count = 0;
                audioInterval = setInterval(() => {
                    const audioWaves = document.querySelectorAll('.audio-wave polyline');
                    audioWaves.forEach(wave => {
                        const colors = ['#f39c12', '#e67e22', '#d4a843', '#2ecc71', '#3498db'];
                        wave.style.stroke = colors[count % colors.length];
                    });
                    count++;
                    
                    if (count > 20) clearInterval(audioInterval);
                }, 300);
                
            } else {
                this.innerHTML = '<i class="fas fa-play"></i> Reproducir Audio (Simulación)';
                this.style.borderColor = '';
                
                if (audioInterval) {
                    clearInterval(audioInterval);
                    audioInterval = null;
                }
                
                // Restaurar estado
                const waves = document.querySelectorAll('.audio-wave polyline');
                waves.forEach(wave => {
                    wave.style.animationDuration = '3s';
                    wave.style.stroke = '#f39c12';
                });
                
                const spin = document.querySelector('.vinyl-spin');
                if (spin) {
                    spin.style.animationDuration = '4s';
                    spin.style.borderColor = '#d4a843';
                }
            }
        });
    }
    
    // ============================================================
    // 12. INICIALIZAR MÉTRICAS CON VALORES DE EJEMPLO
    // ============================================================
    // Esto asegura que los valores mostrados coincidan con los del script Python
    setTimeout(() => {
        // Valores de ejemplo (coinciden con la ejecución típica)
        const metrics = {
            snr: 25.8,
            corr: 0.94,
            energy: 82.3,
            thd: 67.4
        };
        
        // Solo actualizar si no han sido modificados por los controles
        const snrEl = document.getElementById('metricSnr');
        if (snrEl && snrEl.textContent === '0') {
            snrEl.textContent = metrics.snr.toFixed(1);
        }
        
        const corrEl = document.getElementById('metricCorr');
        if (corrEl && corrEl.textContent === '0') {
            corrEl.textContent = metrics.corr.toFixed(2);
        }
        
        const energyEl = document.getElementById('metricEnergy');
        if (energyEl && energyEl.textContent === '0') {
            energyEl.textContent = metrics.energy.toFixed(1);
        }
        
        const thdEl = document.getElementById('metricTHD');
        if (thdEl && thdEl.textContent === '0') {
            thdEl.textContent = metrics.thd.toFixed(1);
        }
    }, 500);
    
    console.log('🎵 Caso 2: Restauración de Audio - Interactividad cargada');
    console.log('📊 Controles disponibles: Frecuencia de Corte, Orden, Ripple');
    console.log('🎛️ Presiona "Aplicar Filtro" para simular la restauración');
});