/**
 * SCRIPT.JS - Caso 3: Comunicaciones por Radio
 * Interactividad para filtro FIR pasa bandas
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
    // 4. CONTROLES DEL FILTRO FIR (Simulación interactiva)
    // ============================================================
    const lowcutSlider = document.getElementById('lowcutSlider');
    const highcutSlider = document.getElementById('highcutSlider');
    const tapsSlider = document.getElementById('tapsSlider');
    const windowSelect = document.getElementById('windowSelect');
    const lowcutDisplay = document.getElementById('lowcutDisplay');
    const highcutDisplay = document.getElementById('highcutDisplay');
    const tapsDisplay = document.getElementById('tapsDisplay');
    const windowDisplay = document.getElementById('windowDisplay');
    const applyBtn = document.getElementById('applyFilterBtn');
    
    if (lowcutSlider && lowcutDisplay) {
        lowcutSlider.addEventListener('input', function() {
            lowcutDisplay.textContent = this.value;
        });
    }
    
    if (highcutSlider && highcutDisplay) {
        highcutSlider.addEventListener('input', function() {
            highcutDisplay.textContent = this.value;
        });
    }
    
    if (tapsSlider && tapsDisplay) {
        tapsSlider.addEventListener('input', function() {
            tapsDisplay.textContent = this.value;
        });
    }
    
    if (windowSelect && windowDisplay) {
        windowSelect.addEventListener('change', function() {
            windowDisplay.textContent = this.options[this.selectedIndex].text;
        });
    }
    
    if (applyBtn) {
        applyBtn.addEventListener('click', function() {
            const lowcut = lowcutSlider ? parseInt(lowcutSlider.value) : 95;
            const highcut = highcutSlider ? parseInt(highcutSlider.value) : 105;
            const taps = tapsSlider ? parseInt(tapsSlider.value) : 101;
            const windowType = windowSelect ? windowSelect.value : 'hamming';
            
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando señal...';
            this.disabled = true;
            
            setTimeout(() => {
                // Calcular métricas basadas en parámetros
                const bandwidth = highcut - lowcut;
                const order = taps - 1;
                
                // SNR mejora con mayor orden y banda más estrecha
                const baseSNR = 15 + (order / 10) + (20 / Math.max(bandwidth, 5));
                const snrImprovement = Math.min(baseSNR, 40);
                
                // Aislamiento mejora con mayor orden
                const baseIsolation = 10 + (order / 8) + (10 / Math.max(bandwidth, 5));
                const isolationImprovement = Math.min(baseIsolation, 30);
                
                // Reducción BER mejora con mayor orden
                const berReduction = 70 + (order / 5) + (20 / Math.max(bandwidth, 5));
                const berReductionFinal = Math.min(berReduction, 98);
                
                // Correlación mejora con mayor orden
                const correlation = 0.90 + (order / 200);
                const correlationFinal = Math.min(correlation, 0.99);
                
                // Actualizar métricas
                document.getElementById('metricSnr').textContent = snrImprovement.toFixed(1);
                document.getElementById('metricCorr').textContent = correlationFinal.toFixed(2);
                document.getElementById('metricIsolation').textContent = isolationImprovement.toFixed(1);
                document.getElementById('metricBER').textContent = berReductionFinal.toFixed(1);
                
                // Actualizar tarjetas de simulación
                const snrBefore = -5.2;
                const snrAfter = snrBefore + snrImprovement;
                const berBefore = 0.0890;
                const berAfter = berBefore * (1 - berReductionFinal / 100);
                const isolationBefore = 8.3;
                const isolationAfter = isolationBefore + isolationImprovement;
                
                const snrBeforeEl = document.getElementById('snrBefore');
                const snrAfterEl = document.getElementById('snrAfter');
                const berBeforeEl = document.getElementById('berBefore');
                const berAfterEl = document.getElementById('berAfter');
                const isolationBeforeEl = document.getElementById('isolationBefore');
                const isolationAfterEl = document.getElementById('isolationAfter');
                
                if (snrBeforeEl) snrBeforeEl.textContent = `${snrBefore.toFixed(1)} dB`;
                if (snrAfterEl) snrAfterEl.textContent = `${snrAfter.toFixed(1)} dB`;
                if (berBeforeEl) berBeforeEl.textContent = berBefore.toFixed(4);
                if (berAfterEl) berAfterEl.textContent = berAfter.toFixed(4);
                if (isolationBeforeEl) isolationBeforeEl.textContent = `${isolationBefore.toFixed(1)} dB`;
                if (isolationAfterEl) isolationAfterEl.textContent = `${isolationAfter.toFixed(1)} dB`;
                
                this.innerHTML = '<i class="fas fa-check"></i> Señal Aislada';
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
        background: var(--secondary, #00d4ff);
        color: white;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3);
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
                border: 1px solid rgba(0, 212, 255, 0.2);
            `;
            
            let text = '';
            const badgeText = el.textContent.trim();
            
            if (el.classList.contains('footer-badge')) {
                text = 'Información adicional sobre comunicaciones militares';
            } else if (el.classList.contains('analysis-tag')) {
                const tags = {
                    'Alto Impacto': 'Mejora significativa en comunicaciones',
                    'Alta Precisión': 'Fase lineal garantizada',
                    'Alta Confiabilidad': 'Comunicación robusta y segura',
                    'Calidad Superior': 'Cumple estándares militares'
                };
                text = tags[badgeText] || 'Categoría de impacto del análisis';
            } else if (el.classList.contains('sim-badge')) {
                text = badgeText === 'CON INTERFERENCIA' ? 
                    'Señal contaminada por canales adyacentes' : 
                    'Señal aislada con filtro FIR Hamming';
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
    
    console.log('📡 Caso 3: Comunicaciones por Radio - Interactividad cargada');
    console.log('📊 Controles disponibles: Frecuencias, Taps, Ventana');
    console.log('🎯 Presiona "Aplicar Filtro" para simular el aislamiento de banda');
});