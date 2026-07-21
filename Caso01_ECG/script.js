/**
 * SCRIPT.JS - Caso 1: Monitoreo de ECG
 * Interactividad, animaciones y controles
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
    // 4. CONTROLES DEL FILTRO (Simulación interactiva)
    // ============================================================
    const cutoffSlider = document.getElementById('cutoffSlider');
    const orderSlider = document.getElementById('orderSlider');
    const cutoffDisplay = document.getElementById('cutoffDisplay');
    const orderDisplay = document.getElementById('orderDisplay');
    const applyBtn = document.getElementById('applyFilterBtn');
    
    if (cutoffSlider && orderSlider) {
        cutoffSlider.addEventListener('input', function() {
            cutoffDisplay.textContent = this.value;
        });
        
        orderSlider.addEventListener('input', function() {
            orderDisplay.textContent = this.value;
        });
    }
    
    if (applyBtn) {
        applyBtn.addEventListener('click', function() {
            // Simular recálculo del filtro
            const cutoff = cutoffSlider ? cutoffSlider.value : 40;
            const order = orderSlider ? orderSlider.value : 4;
            
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
            this.disabled = true;
            
            setTimeout(() => {
                // Actualizar métricas simuladas (en una implementación real, esto llamaría a una API)
                const snrImprovement = 20 + (order * 2) + (cutoff / 10);
                const corr = 0.90 + (order / 30);
                const energy = 85 + (cutoff / 10);
                
                document.getElementById('metricSnr').textContent = snrImprovement.toFixed(1);
                document.getElementById('metricCorr').textContent = corr.toFixed(2);
                document.getElementById('metricEnergy').textContent = energy.toFixed(1);
                
                // Actualizar también las etiquetas de SNR en la simulación
                const snrBefore = document.getElementById('snrBefore');
                const snrAfter = document.getElementById('snrAfter');
                const snrImprovementEl = document.getElementById('snrImprovement');
                
                if (snrBefore) snrBefore.textContent = `${(-5 - order/2).toFixed(1)} dB`;
                if (snrAfter) snrAfter.textContent = `${(snrImprovement - 5).toFixed(1)} dB`;
                if (snrImprovementEl) snrImprovementEl.textContent = `+${snrImprovement.toFixed(1)} dB`;
                
                this.innerHTML = '<i class="fas fa-check"></i> Filtro Aplicado';
                this.disabled = false;
                
                setTimeout(() => {
                    this.innerHTML = '<i class="fas fa-sync"></i> Aplicar Filtro';
                }, 2000);
            }, 1500);
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
    function animateCounter(element, target, duration = 2000) {
        if (!element) return;
        const start = 0;
        const startTime = performance.now();
        
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = start + (target - start) * eased;
            
            if (target % 1 === 0) {
                element.textContent = Math.round(current);
            } else {
                element.textContent = current.toFixed(target.toString().split('.')[1]?.length || 0);
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
                const value = parseFloat(element.textContent);
                if (!isNaN(value)) {
                    element.textContent = '0';
                    animateCounter(element, value, 1500);
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
        background: var(--secondary, #e74c3c);
        color: white;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(231, 76, 60, 0.3);
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
    document.querySelectorAll('.footer-badge, .analysis-tag, .sim-badge').forEach(el => {
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
            `;
            
            let text = '';
            if (el.classList.contains('footer-badge')) {
                text = 'Información adicional sobre el proyecto';
            } else if (el.classList.contains('analysis-tag')) {
                text = 'Categoría de impacto del análisis';
            } else if (el.classList.contains('sim-badge')) {
                text = el.textContent.trim() === 'CRUDA' ? 
                    'Señal sin procesar con ruido significativo' : 
                    'Señal procesada con el filtro aplicado';
            }
            
            tooltip.textContent = text || 'Más información';
            document.body.appendChild(tooltip);
            
            const rect = el.getBoundingClientRect();
            tooltip.style.top = (rect.bottom + 10) + 'px';
            tooltip.style.left = (rect.left + rect.width/2 - tooltip.offsetWidth/2) + 'px';
            
            el.addEventListener('mouseleave', function() {
                tooltip.remove();
            }, { once: true });
        });
    });
    
    console.log('🚀 Caso 1: Monitoreo de ECG - Interactividad cargada');
});