/**
 * SCRIPT.JS - Caso 5: Control Industrial
 * Interactividad y controles para filtro Notch
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
    // 4. CONTROLES DEL FILTRO NOTCH (Simulación interactiva)
    // ============================================================
    const freqSlider = document.getElementById('freqSlider');
    const bwSlider = document.getElementById('bwSlider');
    const qSlider = document.getElementById('qSlider');
    const freqDisplay = document.getElementById('freqDisplay');
    const bwDisplay = document.getElementById('bwDisplay');
    const qDisplay = document.getElementById('qDisplay');
    const applyBtn = document.getElementById('applyFilterBtn');
    
    if (freqSlider && freqDisplay) {
        freqSlider.addEventListener('input', function() {
            freqDisplay.textContent = this.value;
            // Actualizar Q automáticamente
            if (bwSlider && qDisplay) {
                const freq = parseInt(this.value);
                const bw = parseInt(bwSlider.value);
                const q = freq / bw;
                qDisplay.textContent = q.toFixed(1);
                if (qSlider) qSlider.value = q;
            }
        });
    }
    
    if (bwSlider && bwDisplay) {
        bwSlider.addEventListener('input', function() {
            bwDisplay.textContent = this.value;
            // Actualizar Q automáticamente
            if (freqSlider && qDisplay) {
                const freq = parseInt(freqSlider.value);
                const bw = parseInt(this.value);
                const q = freq / bw;
                qDisplay.textContent = q.toFixed(1);
                if (qSlider) qSlider.value = q;
            }
        });
    }
    
    if (qSlider && qDisplay) {
        qSlider.addEventListener('input', function() {
            const q = parseFloat(this.value);
            qDisplay.textContent = q.toFixed(1);
            // Actualizar BW automáticamente
            if (freqSlider && bwDisplay) {
                const freq = parseInt(freqSlider.value);
                const bw = freq / q;
                bwDisplay.textContent = Math.round(bw);
                if (bwSlider) bwSlider.value = Math.round(bw);
            }
        });
    }
    
    if (applyBtn) {
        applyBtn.addEventListener('click', function() {
            const freq = freqSlider ? parseInt(freqSlider.value) : 120;
            const bw = bwSlider ? parseInt(bwSlider.value) : 10;
            const q = qSlider ? parseFloat(qSlider.value) : 12.0;
            
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando vibración...';
            this.disabled = true;
            
            setTimeout(() => {
                // Calcular métricas basadas en parámetros
                // Mayor Q = mejor atenuación pero más estrecho
                const baseAtten = 15 + (q / 2);
                const attenImprovement = Math.min(baseAtten, 35);
                
                // Reducción de anomalías mejora con mayor Q
                const baseAnomaly = 60 + (q * 2);
                const anomalyReduction = Math.min(baseAnomaly, 92);
                
                // SNR mejora con mayor Q
                const baseSnr = 10 + (q / 1.5);
                const snrImprovement = Math.min(baseSnr, 25);
                
                // Correlación (balance entre atenuación y preservación)
                const correlation = 0.88 + (q / 50);
                const correlationFinal = Math.min(correlation, 0.98);
                
                // Calcular valores absolutos
                const snrBefore = 3.8;
                const snrAfter = snrBefore + snrImprovement;
                const resonanceBefore = -12.4;
                const resonanceAfter = resonanceBefore - attenImprovement;
                const anomaliesBefore = 18;
                const anomaliesAfter = Math.max(2, Math.round(anomaliesBefore * (1 - anomalyReduction / 100)));
                
                // Actualizar métricas principales
                document.getElementById('metricSnr').textContent = snrImprovement.toFixed(1);
                document.getElementById('metricCorr').textContent = correlationFinal.toFixed(2);
                document.getElementById('metricAtten').textContent = attenImprovement.toFixed(1);
                document.getElementById('metricAnomalies').textContent = anomalyReduction.toFixed(1);
                
                // Actualizar tarjetas de simulación
                const snrBeforeEl = document.getElementById('snrBefore');
                const snrAfterEl = document.getElementById('snrAfter');
                const resonanceBeforeEl = document.getElementById('resonanceBefore');
                const resonanceAfterEl = document.getElementById('resonanceAfter');
                const anomaliesBeforeEl = document.getElementById('anomaliesBefore');
                const anomaliesAfterEl = document.getElementById('anomaliesAfter');
                
                if (snrBeforeEl) snrBeforeEl.textContent = `${snrBefore.toFixed(1)} dB`;
                if (snrAfterEl) snrAfterEl.textContent = `${snrAfter.toFixed(1)} dB`;
                if (resonanceBeforeEl) resonanceBeforeEl.textContent = `${resonanceBefore.toFixed(1)} dB`;
                if (resonanceAfterEl) resonanceAfterEl.textContent = `${resonanceAfter.toFixed(1)} dB`;
                if (anomaliesBeforeEl) anomaliesBeforeEl.textContent = anomaliesBefore;
                if (anomaliesAfterEl) anomaliesAfterEl.textContent = anomaliesAfter;
                
                // Actualizar badges de tendencia
                const trendBadges = document.querySelectorAll('.metric-trend');
                if (trendBadges.length >= 4) {
                    trendBadges[0].innerHTML = `<i class="fas fa-arrow-up"></i> +${Math.round((snrImprovement / 15) * 100)}%`;
                    trendBadges[1].innerHTML = `<i class="fas fa-arrow-up"></i> ${correlationFinal > 0.94 ? 'Excelente' : 'Buena'}`;
                    trendBadges[2].innerHTML = `<i class="fas fa-arrow-up"></i> +${Math.round((attenImprovement / 22) * 100)}%`;
                    trendBadges[3].innerHTML = `<i class="fas fa-arrow-up"></i> ${anomalyReduction > 80 ? 'Excelente' : 'Buena'}`;
                }
                
                // Actualizar estado del indicador
                const statusDot = document.querySelector('.status-dot');
                const statusText = document.querySelector('.status-text');
                if (statusDot && statusText) {
                    if (anomaliesAfter < 5) {
                        statusDot.className = 'status-dot success';
                        statusText.textContent = 'Sistema estable';
                    } else if (anomaliesAfter < 10) {
                        statusDot.className = 'status-dot warning';
                        statusText.textContent = 'Monitoreo activo';
                    } else {
                        statusDot.className = 'status-dot danger';
                        statusText.textContent = '¡Alerta! Anomalías detectadas';
                    }
                }
                
                this.innerHTML = '<i class="fas fa-check"></i> Filtro Aplicado';
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
                const modal = document.createElement('div');
                modal.style.cssText = `
                    position: fixed;
                    inset: 0;
                    background: rgba(0,0,0,0.95);
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
                    object-fit: contain;
                `;
                
                modal.appendChild(modalImg);
                document.body.appendChild(modal);
                
                modal.addEventListener('click', function() {
                    this.remove();
                });
                
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
    // 6. CONTADOR ANIMADO
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
    // 7. SCROLL TO TOP
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
        background: var(--secondary, #ff6b35);
        color: white;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(255, 107, 53, 0.3);
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
    // 8. TOOLTIP PARA BADGES
    // ============================================================
    document.querySelectorAll('.footer-badge, .analysis-tag, .sim-badge, .chart-badge').forEach(el => {
        el.addEventListener('mouseenter', function(e) {
            const tooltip = document.createElement('div');
            tooltip.style.cssText = `
                position: fixed;
                background: var(--dark, #0a0a1a);
                color: white;
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 0.8rem;
                z-index: 9999;
                box-shadow: 0 4px 20px rgba(0,0,0,0.2);
                pointer-events: none;
                max-width: 300px;
                border: 1px solid rgba(255, 107, 53, 0.2);
            `;
            
            let text = '';
            const badgeText = el.textContent.trim();
            
            if (el.classList.contains('footer-badge')) {
                text = 'Información adicional sobre control industrial';
            } else if (el.classList.contains('analysis-tag')) {
                const tags = {
                    'Alto Impacto': 'Mejora significativa en mantenimiento',
                    'Alta Precisión': 'Elimina resonancia sin afectar otras señales',
                    'Alta Confiabilidad': 'Sistema de monitoreo confiable',
                    'Ahorro Significativo': 'Reduce costos de mantenimiento'
                };
                text = tags[badgeText] || 'Categoría de impacto del análisis';
            } else if (el.classList.contains('sim-badge')) {
                text = badgeText === 'CON RESONANCIA' ? 
                    'Vibración con resonancia en 120 Hz enmascarando anomalías' : 
                    'Vibración estable después de eliminar la resonancia';
            } else if (el.classList.contains('chart-badge')) {
                text = 'Visualización de resultados del análisis industrial';
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
    
    console.log('🏭 Caso 5: Control Industrial - Interactividad cargada');
    console.log('📊 Controles disponibles: Frecuencia, Ancho de Banda, Factor Q');
    console.log('⚙️ Presiona "Aplicar Filtro" para simular el procesamiento de vibración');
});