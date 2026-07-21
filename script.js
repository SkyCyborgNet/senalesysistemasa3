/**
 * SCRIPT.JS - Página Principal
 * Universidad Ciudadana de Nuevo León
 * Interactividad y efectos visuales
 */

document.addEventListener('DOMContentLoaded', function() {

    // ================================================================
    // 1. MENÚ HAMBURGUESA (RESPONSIVE)
    // ================================================================
    const headerToggle = document.querySelector('.header-toggle');
    const navList = document.querySelector('.nav-list');

    if (headerToggle && navList) {
        headerToggle.addEventListener('click', function() {
            navList.classList.toggle('active');
            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-bars');
                icon.classList.toggle('fa-times');
            }
        });
    }

    // Cerrar menú al hacer clic en un enlace
    document.querySelectorAll('.nav-link').forEach(function(link) {
        link.addEventListener('click', function() {
            if (navList && window.innerWidth <= 768) {
                navList.classList.remove('active');
                const icon = headerToggle?.querySelector('i');
                if (icon) {
                    icon.classList.add('fa-bars');
                    icon.classList.remove('fa-times');
                }
            }
        });
    });

    // ================================================================
    // 2. NAVEGACIÓN ACTIVA POR SCROLL
    // ================================================================
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');

    function updateActiveNav() {
        let current = '';
        const scrollPos = window.scrollY + 120;

        sections.forEach(function(section) {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(function(link) {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    }

    window.addEventListener('scroll', updateActiveNav);

    // ================================================================
    // 3. ANIMACIÓN DE SECCIONES AL APARECER (FADE IN)
    // ================================================================
    const animatedSections = document.querySelectorAll('.section');

    const sectionObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                sectionObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    animatedSections.forEach(function(section) {
        section.style.opacity = '0';
        section.style.transform = 'translateY(30px)';
        section.style.transition = 'opacity 0.7s ease, transform 0.7s ease';
        sectionObserver.observe(section);
    });

    // ================================================================
    // 4. ANIMACIÓN DE TARJETAS DE CASOS (APARICIÓN ESCALONADA)
    // ================================================================
    const casoCards = document.querySelectorAll('.caso-card');

    const cardObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry, index) {
            if (entry.isIntersecting) {
                const delay = index * 100;
                setTimeout(function() {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, delay);
                cardObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.15,
        rootMargin: '0px 0px -30px 0px'
    });

    casoCards.forEach(function(card) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(40px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        cardObserver.observe(card);
    });

    // ================================================================
    // 5. ANIMACIÓN DE RESUMENES (APARICIÓN ESCALONADA)
    // ================================================================
    const resumenItems = document.querySelectorAll('.resumen-item');

    const resumenObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry, index) {
            if (entry.isIntersecting) {
                const delay = index * 80;
                setTimeout(function() {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateX(0)';
                }, delay);
                resumenObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.15,
        rootMargin: '0px 0px -30px 0px'
    });

    resumenItems.forEach(function(item) {
        item.style.opacity = '0';
        item.style.transform = 'translateX(-20px)';
        item.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        resumenObserver.observe(item);
    });

    // ================================================================
    // 6. SCROLL SUAVE PARA ENLACES INTERNOS
    // ================================================================
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                const headerHeight = document.querySelector('.header')?.offsetHeight || 0;
                const targetPosition = targetElement.offsetTop - headerHeight;
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // ================================================================
    // 7. BOTÓN SCROLL TO TOP
    // ================================================================
    const scrollBtn = document.createElement('button');
    scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollBtn.setAttribute('aria-label', 'Volver arriba');
    scrollBtn.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: var(--gold, #c9a83a);
        color: var(--primary, #0a2a4a);
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(201, 168, 58, 0.4);
        transition: all 0.3s ease;
        opacity: 0;
        transform: translateY(20px);
        z-index: 999;
        display: flex;
        align-items: center;
        justify-content: center;
    `;

    document.body.appendChild(scrollBtn);

    // Hover effect
    scrollBtn.addEventListener('mouseenter', function() {
        this.style.transform = 'scale(1.1)';
        this.style.boxShadow = '0 6px 30px rgba(201, 168, 58, 0.5)';
    });

    scrollBtn.addEventListener('mouseleave', function() {
        this.style.transform = 'scale(1)';
        this.style.boxShadow = '0 4px 20px rgba(201, 168, 58, 0.4)';
    });

    window.addEventListener('scroll', function() {
        if (window.scrollY > 400) {
            scrollBtn.style.opacity = '1';
            scrollBtn.style.transform = 'translateY(0)';
        } else {
            scrollBtn.style.opacity = '0';
            scrollBtn.style.transform = 'translateY(20px)';
        }
    });

    scrollBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // ================================================================
    // 8. EFECTO PARALLAX EN EL HERO (SUTIL)
    // ================================================================
    const hero = document.querySelector('.hero');
    if (hero) {
        window.addEventListener('scroll', function() {
            const scrollPos = window.scrollY;
            if (scrollPos < hero.offsetHeight) {
                const parallax = scrollPos * 0.3;
                const heroContent = hero.querySelector('.hero-content');
                if (heroContent) {
                    heroContent.style.transform = 'translateY(' + parallax + 'px)';
                    heroContent.style.opacity = 1 - (scrollPos / hero.offsetHeight) * 0.3;
                }
            }
        }, { passive: true });
    }

    // ================================================================
    // 9. EFECTO DE GLOW EN TARJETAS AL HOVER (SUTIL)
    // ================================================================
    casoCards.forEach(function(card) {
        card.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 12px 40px rgba(10, 42, 74, 0.25)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.boxShadow = '0 4px 20px rgba(10, 42, 74, 0.15)';
        });
    });

    // ================================================================
    // 10. CONTADOR DE AÑO EN FOOTER (AUTOMÁTICO)
    // ================================================================
    const footerYear = document.querySelector('.footer-bottom p');
    if (footerYear) {
        const currentYear = new Date().getFullYear();
        footerYear.textContent = footerYear.textContent.replace('2026', currentYear);
    }

    // ================================================================
    // 11. TOOLTIP PARA ENLACES DE REFERENCIAS (OPCIONAL)
    // ================================================================
    document.querySelectorAll('.referencia-item').forEach(function(item) {
        item.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(10, 42, 74, 0.03)';
            this.style.borderRadius = '8px';
            this.style.paddingLeft = '16px';
            this.style.paddingRight = '16px';
            this.style.transition = 'all 0.3s ease';
        });
        item.addEventListener('mouseleave', function() {
            this.style.backgroundColor = 'transparent';
            this.style.paddingLeft = '0';
            this.style.paddingRight = '0';
        });
    });

    // ================================================================
    // 12. CONSOLA INFORMATIVA (ESTILO PROFESIONAL)
    // ================================================================
    console.log('%c🏛️ Universidad Ciudadana de Nuevo León', 'font-size:20px; font-weight:bold; color:#c9a83a;');
    console.log('%c📚 Señales y Sistemas - Filtros Digitales', 'font-size:14px; color:#1a4a7a;');
    console.log('%c👨‍🎓 Eric David Rodríguez Flores', 'font-size:12px; color:#0a2a4a;');
    console.log('%c📅 20 de Julio de 2026', 'font-size:12px; color:#6a8aaa;');
    console.log('%c✅ 5 Casos de Estudio Implementados', 'font-size:12px; color:#2ecc71;');
    console.log('%c🚀 Diseño basado en los colores institucionales UCNL', 'font-size:12px; color:#c9a83a;');

    console.log('📊 Casos disponibles:');
    console.log('  1️⃣  Monitoreo de ECG (Pasa Bajos - Butterworth)');
    console.log('  2️⃣  Restauración de Audio (Pasa Altos - Chebyshev)');
    console.log('  3️⃣  Comunicaciones por Radio (Pasa Bandas - FIR Hamming)');
    console.log('  4️⃣  Imágenes Médicas (Pasa Bajos - FIR Kaiser)');
    console.log('  5️⃣  Control Industrial (Rechazo Banda - Notch Butterworth)');

    // ================================================================
    // 13. DETECTAR SI LAS IMÁGENES CARGARON CORRECTAMENTE
    // ================================================================
    document.querySelectorAll('img').forEach(function(img) {
        img.addEventListener('error', function() {
            console.warn('⚠️ Imagen no encontrada:', this.src);
            // Opcional: mostrar placeholder
            this.style.backgroundColor = '#e8eef5';
            this.style.display = 'flex';
            this.style.alignItems = 'center';
            this.style.justifyContent = 'center';
            this.style.color = '#6a8aaa';
            this.style.fontSize = '0.8rem';
            // No se puede establecer textContent en img, pero se puede usar alt
            this.alt = 'Imagen no disponible';
        });
    });

    console.log('✅ Página cargada exitosamente');
});