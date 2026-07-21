/**
 * SCRIPT.JS - Caso 4: Procesamiento de Imágenes Médicas
 * Interactividad y controles para filtro de imágenes
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
    // 4. CONTROLES DEL FILTRO (Simulación interactiva)
    // ============================================================
    const cutoffSlider = document.getElementById('cutoffSlider');
    const kernelSlider = document.getElementById('kernelSlider');
    const betaSlider = document.getElementById('betaSlider');
    const cutoffDisplay = document.getElementById('cutoffDisplay');
    const kernelDisplay = document.getElementById('kernelDisplay');
    const betaDisplay = document.getElementById('betaDisplay');
    const applyBtn = document.getElementById('applyFilterBtn');
    
    if (cutoffSlider && cutoffDisplay) {
        cutoffSlider.addEventListener('input', function() {
            cutoffDisplay.textContent = parseFloat(this.value).toFixed(2);
        });
    }
    
    if (kernelSlider && kernelDisplay) {
        kernelSlider.addEventListener('input', function() {
            kernelDisplay.textContent = this.value;
        });
    }
    
    if (betaSlider && betaDisplay) {
        betaSlider.addEventListener('input', function() {
            betaDisplay.textContent = parseFloat(this.value).toFixed(1);
        });
    }
    
    if (applyBtn) {
        applyBtn.addEventListener('click', function() {
            const cutoff = cutoffSlider ? parseFloat(cutoffSlider.value) : 0.3;
            const kernel = kernelSlider ? parseInt(kernelSlider.value) : 15;
            const beta = betaSlider ? parseFloat(betaSlider.value) : 5.0;
            
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando imagen...';
            this.disabled = true;
            
            setTimeout(() => {
                // Calcular métricas basadas en parámetros
                // Mejor PSNR con mayor kernel y menor cutoff
                const basePsnr = 30 + (kernel / 5) + (beta * 0.5) + ((0.3 - cutoff) * 20);
                const psnrImprovement = Math.min(Math.max(basePsnr, 8), 20);
                
                // Mejor SSIM con balance de parámetros
                const baseSsim = 0.85 + (kernel / 50) - (cutoff * 0.2) + (beta * 0.01);
                const ssimImprovement = Math.min(Math.max(baseSsim - 0.75, 0.05), 0.25);
                
                // Reducción MSE
                const baseMse = 40 + (kernel * 1.5) + (beta * 2) + ((0.3 - cutoff) * 30);
                const mseReduction = Math.min(Math.max(baseMse, 40), 85);
                
                // Preservación de bordes (disminuye con mayor kernel)
                const baseEdges = 85 - (kernel * 0.8) - (beta * 0.5) + ((0.3 - cutoff) * 20);
                const edgePreservation = Math.min(Math.max(baseEdges, 50), 90);
                
                // Calcular valores absolutos
                const psnrBefore = 25.3;
                const psnrAfter = psnrBefore + psnrImprovement;
                const ssimBefore = 0.750;
                const ssimAfter = Math.min(ssimBefore + ssimImprovement, 0.98);
                const mseBefore = 0.0420;
                const mseAfter = mseBefore * (1 - mseReduction / 100);
                
                // Actualizar métricas principales
                document.getElementById('metricPsnr').textContent = psnrImprovement.toFixed(1);
                document.getElementById('metricSsim').textContent = ssimImprovement.toFixed(3);
                document.getElementById('metricMse').textContent = mseReduction.toFixed(1);
                document.getElementById('metricEdges').textContent = edgePreservation.toFixed(1);
                
                // Actualizar tarjetas de simulación
                const psnrBeforeEl = document.getElementById('psnrBefore');
                const psnrAfterEl = document.getElementById('psnrAfter');
                const ssimBeforeEl = document.getElementById('ssimBefore');
                const ssimAfterEl = document.getElementById('ssimAfter');
                const mseBeforeEl = document.getElementById('mseBefore');
                const mseAfterEl = document.getElementById('mseAfter');
                
                if (psnrBeforeEl) psnrBeforeEl.textContent = `${psnrBefore.toFixed(1)} dB`;
                if (psnrAfterEl) psnrAfterEl.textContent = `${psnrAfter.toFixed(1)} dB`;
                if (ssimBeforeEl) ssimBeforeEl.textContent = ssimBefore.toFixed(3);
                if (ssimAfterEl) ssimAfterEl.textContent = ssimAfter.toFixed(3);
                if (mseBeforeEl) mseBeforeEl.textContent = mseBefore.toFixed(4);
                if (mseAfterEl) mseAfterEl.textContent = mseAfter.toFixed(4);
                
                // Actualizar badges de tendencia
                const trendBadges = document.querySelectorAll('.metric-trend');
                if (trendBadges.length >= 4) {
                    trendBadges[0].innerHTML = `<i class="fas fa-arrow-up"></i> +${Math.round((psnrImprovement / 12) * 100)}%`;
                    trendBadges[1].innerHTML = `<i class="fas fa-arrow-up"></i> +${Math.round((ssimImprovement / 0.15) * 100)}%`;
                    trendBadges[2].innerHTML = `<i class="fas fa-arrow-up"></i> ${mseReduction > 60 ? 'Excelente' : 'Buena'}`;
                    trendBadges[3].innerHTML = `<i class="fas fa-arrow-${edgePreservation > 70 ? 'up' : 'down'}"></i> ${edgePreservation > 70 ? 'Alta' : 'Media'}`;
                }
                
                this.innerHTML = '<i class="fas fa-check"></i> Imagen Procesada';
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
                text = 'Información adicional sobre procesamiento de imágenes médicas';
            } else if (el.classList.contains('analysis-tag')) {
                const tags = {
                    'Alto Impacto': 'Mejora significativa en diagnóstico',
                    'Alta Precisión': 'Preserva detalles anatómicos críticos',
                    'Alta Confiabilidad': 'Imagen confiable para diagnóstico',
                    'Bajo Costo': 'Implementación eficiente en hardware médico'
                };
                text = tags[badgeText] || 'Categoría de impacto del análisis';
            } else if (el.classList.contains('sim-badge')) {
                text = badgeText === 'CON RUIDO' ? 
                    'Imagen contaminada con ruido Poisson, Gaussiano y sal y pimienta' : 
                    badgeText === 'FILTRADA' ?
                    'Imagen procesada con filtro FIR Kaiser' :
                    'Imagen de referencia sin ruido';
            } else if (el.classList.contains('chart-badge')) {
                text = 'Visualización de resultados del procesamiento';
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
    
    console.log('🏥 Caso 4: Procesamiento de Imágenes Médicas - Interactividad cargada');
    console.log('📊 Controles disponibles: Frecuencia de Corte, Tamaño Kernel, Beta Kaiser');
    console.log('🖼️ Presiona "Aplicar Filtro" para simular el procesamiento de imagen');
});