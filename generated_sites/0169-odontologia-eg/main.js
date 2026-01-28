/**
 * Premium Landing Page JavaScript
 * Interactive features for engaging client experience
 */

(function() {
    'use strict';

    // ===========================================
    // CONFIGURATION
    // ===========================================
    const CONFIG = {
        scrollOffset: 80,
        animationDelay: 100,
        counterDuration: 2000,
        typingSpeed: 50,
        lazyLoadThreshold: 0.1
    };

    // ===========================================
    // UTILITY FUNCTIONS
    // ===========================================
    const debounce = (func, wait) => {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    };

    const isInViewport = (element, threshold = 0) => {
        const rect = element.getBoundingClientRect();
        return (
            rect.top <= (window.innerHeight || document.documentElement.clientHeight) * (1 - threshold) &&
            rect.bottom >= 0
        );
    };

    // ===========================================
    // MOBILE MENU
    // ===========================================
    const initMobileMenu = () => {
        const menuBtn = document.getElementById('mobile-menu-btn');
        const mobileMenu = document.getElementById('mobile-menu');
        const menuLinks = document.querySelectorAll('#mobile-menu a');
        
        if (!menuBtn || !mobileMenu) return;

        let isOpen = false;

        const toggleMenu = () => {
            isOpen = !isOpen;
            mobileMenu.classList.toggle('hidden', !isOpen);
            menuBtn.querySelector('svg').innerHTML = isOpen 
                ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>'
                : '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>';
        };

        menuBtn.addEventListener('click', toggleMenu);

        menuLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (isOpen) toggleMenu();
            });
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (isOpen && !mobileMenu.contains(e.target) && !menuBtn.contains(e.target)) {
                toggleMenu();
            }
        });
    };

    // ===========================================
    // NAVBAR SCROLL EFFECT
    // ===========================================
    const initNavbarScroll = () => {
        const navbar = document.getElementById('navbar');
        if (!navbar) return;

        let lastScroll = 0;
        const scrollThreshold = 100;

        const handleScroll = () => {
            const currentScroll = window.scrollY;

            // Add shadow when scrolled
            navbar.classList.toggle('shadow-2xl', currentScroll > scrollThreshold);
            
            // Hide/show on scroll direction (optional)
            if (currentScroll > lastScroll && currentScroll > 500) {
                navbar.style.transform = 'translateY(-100%)';
            } else {
                navbar.style.transform = 'translateY(0)';
            }

            lastScroll = currentScroll;
        };

        window.addEventListener('scroll', debounce(handleScroll, 10));
    };

    // ===========================================
    // SMOOTH SCROLL
    // ===========================================
    const initSmoothScroll = () => {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href === '#') return;
                
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    const offsetTop = target.offsetTop - CONFIG.scrollOffset;
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                }
            });
        });
    };

    // ===========================================
    // SCROLL REVEAL ANIMATIONS
    // ===========================================
    const initScrollReveal = () => {
        const revealElements = document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale');
        
        if (!revealElements.length) return;

        const revealOnScroll = () => {
            revealElements.forEach((element, index) => {
                if (isInViewport(element, CONFIG.lazyLoadThreshold)) {
                    setTimeout(() => {
                        element.classList.add('revealed');
                    }, index * CONFIG.animationDelay);
                }
            });
        };

        // Initial check
        revealOnScroll();
        
        // On scroll
        window.addEventListener('scroll', debounce(revealOnScroll, 50));
    };

    // ===========================================
    // ANIMATED COUNTERS
    // ===========================================
    const initCounters = () => {
        const counters = document.querySelectorAll('[data-counter]');
        
        if (!counters.length) return;

        const animateCounter = (counter) => {
            const target = parseFloat(counter.dataset.counter);
            const decimals = (target.toString().split('.')[1] || '').length;
            const duration = CONFIG.counterDuration;
            const increment = target / (duration / 16);
            
            let current = 0;
            
            const updateCounter = () => {
                current += increment;
                if (current < target) {
                    counter.textContent = decimals > 0 ? current.toFixed(decimals) : Math.ceil(current);
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = target;
                }
            };
            
            updateCounter();
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
                    entry.target.classList.add('counted');
                    animateCounter(entry.target);
                }
            });
        }, { threshold: 0.5 });

        counters.forEach(counter => observer.observe(counter));
    };

    // ===========================================
    // IMAGE LIGHTBOX
    // ===========================================
    const initLightbox = () => {
        const galleryImages = document.querySelectorAll('[data-lightbox]');
        
        if (!galleryImages.length) return;

        // Create lightbox modal
        const lightbox = document.createElement('div');
        lightbox.id = 'lightbox';
        lightbox.className = 'fixed inset-0 z-[100] bg-black/95 hidden items-center justify-center p-4';
        lightbox.innerHTML = `
            <button id="lightbox-close" class="absolute top-4 right-4 text-white hover:text-gray-300 transition-colors z-10">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
            </button>
            <button id="lightbox-prev" class="absolute left-4 top-1/2 -translate-y-1/2 text-white hover:text-gray-300 transition-colors">
                <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                </svg>
            </button>
            <button id="lightbox-next" class="absolute right-4 top-1/2 -translate-y-1/2 text-white hover:text-gray-300 transition-colors">
                <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
            </button>
            <img id="lightbox-image" class="max-w-full max-h-[90vh] object-contain rounded-lg shadow-2xl" alt="">
            <div id="lightbox-counter" class="absolute bottom-4 left-1/2 -translate-x-1/2 text-white/70 text-sm"></div>
        `;
        document.body.appendChild(lightbox);

        const lightboxImg = document.getElementById('lightbox-image');
        const lightboxCounter = document.getElementById('lightbox-counter');
        let currentIndex = 0;
        const images = Array.from(galleryImages).map(img => img.src);

        const showImage = (index) => {
            currentIndex = (index + images.length) % images.length;
            lightboxImg.src = images[currentIndex].replace('w600-', 'w1200-').replace('h400-', 'h800-');
            lightboxCounter.textContent = `${currentIndex + 1} / ${images.length}`;
        };

        const openLightbox = (index) => {
            showImage(index);
            lightbox.classList.remove('hidden');
            lightbox.classList.add('flex');
            document.body.style.overflow = 'hidden';
        };

        const closeLightbox = () => {
            lightbox.classList.add('hidden');
            lightbox.classList.remove('flex');
            document.body.style.overflow = '';
        };

        galleryImages.forEach((img, index) => {
            img.style.cursor = 'pointer';
            img.addEventListener('click', () => openLightbox(index));
        });

        document.getElementById('lightbox-close').addEventListener('click', closeLightbox);
        document.getElementById('lightbox-prev').addEventListener('click', () => showImage(currentIndex - 1));
        document.getElementById('lightbox-next').addEventListener('click', () => showImage(currentIndex + 1));

        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox) closeLightbox();
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (!lightbox.classList.contains('hidden')) {
                if (e.key === 'Escape') closeLightbox();
                if (e.key === 'ArrowLeft') showImage(currentIndex - 1);
                if (e.key === 'ArrowRight') showImage(currentIndex + 1);
            }
        });
    };

    // ===========================================
    // BACK TO TOP BUTTON
    // ===========================================
    const initBackToTop = () => {
        const btn = document.createElement('button');
        btn.id = 'back-to-top';
        btn.className = 'fixed bottom-24 right-6 z-40 w-12 h-12 bg-gray-800/80 hover:bg-gray-700 text-white rounded-full shadow-lg transition-all transform translate-y-20 opacity-0 backdrop-blur-sm';
        btn.innerHTML = `
            <svg class="w-6 h-6 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"/>
            </svg>
        `;
        document.body.appendChild(btn);

        const toggleButton = () => {
            if (window.scrollY > 500) {
                btn.classList.remove('translate-y-20', 'opacity-0');
            } else {
                btn.classList.add('translate-y-20', 'opacity-0');
            }
        };

        btn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });

        window.addEventListener('scroll', debounce(toggleButton, 100));
    };

    // ===========================================
    // LAZY LOADING IMAGES
    // ===========================================
    const initLazyLoad = () => {
        const lazyImages = document.querySelectorAll('img[loading="lazy"]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                        }
                        img.classList.add('loaded');
                        imageObserver.unobserve(img);
                    }
                });
            }, { threshold: CONFIG.lazyLoadThreshold });

            lazyImages.forEach(img => imageObserver.observe(img));
        }
    };

    // ===========================================
    // FAQ ACCORDION
    // ===========================================
    const initFAQAccordion = () => {
        const faqItems = document.querySelectorAll('.faq-item');
        
        faqItems.forEach(item => {
            const summary = item.querySelector('summary');
            if (summary) {
                summary.addEventListener('click', () => {
                    // Close other open items
                    faqItems.forEach(other => {
                        if (other !== item && other.open) {
                            other.open = false;
                        }
                    });
                });
            }
        });
    };

    // ===========================================
    // REVIEWS CAROUSEL
    // ===========================================
    const initReviewsCarousel = () => {
        const carousel = document.getElementById('reviews-carousel');
        if (!carousel) return;

        const track = carousel.querySelector('.reviews-track');
        const prevBtn = document.getElementById('reviews-prev');
        const nextBtn = document.getElementById('reviews-next');
        const cards = track?.querySelectorAll('.review-card');

        if (!track || !cards?.length) return;

        let currentIndex = 0;
        const cardsPerView = window.innerWidth >= 768 ? 2 : 1;
        const maxIndex = Math.max(0, cards.length - cardsPerView);

        const updateCarousel = () => {
            const cardWidth = cards[0].offsetWidth + 24; // Include gap
            track.style.transform = `translateX(-${currentIndex * cardWidth}px)`;
            
            if (prevBtn) prevBtn.disabled = currentIndex === 0;
            if (nextBtn) nextBtn.disabled = currentIndex >= maxIndex;
        };

        prevBtn?.addEventListener('click', () => {
            if (currentIndex > 0) {
                currentIndex--;
                updateCarousel();
            }
        });

        nextBtn?.addEventListener('click', () => {
            if (currentIndex < maxIndex) {
                currentIndex++;
                updateCarousel();
            }
        });

        // Auto-play
        let autoPlay = setInterval(() => {
            if (currentIndex < maxIndex) {
                currentIndex++;
            } else {
                currentIndex = 0;
            }
            updateCarousel();
        }, 5000);

        carousel.addEventListener('mouseenter', () => clearInterval(autoPlay));
        carousel.addEventListener('mouseleave', () => {
            autoPlay = setInterval(() => {
                if (currentIndex < maxIndex) currentIndex++;
                else currentIndex = 0;
                updateCarousel();
            }, 5000);
        });

        // Handle resize
        window.addEventListener('resize', debounce(updateCarousel, 200));
    };

    // ===========================================
    // FORM VALIDATION (if contact form exists)
    // ===========================================
    const initFormValidation = () => {
        const forms = document.querySelectorAll('form[data-validate]');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                const inputs = form.querySelectorAll('input[required], textarea[required]');
                let isValid = true;

                inputs.forEach(input => {
                    if (!input.value.trim()) {
                        isValid = false;
                        input.classList.add('border-red-500');
                    } else {
                        input.classList.remove('border-red-500');
                    }
                });

                if (!isValid) {
                    e.preventDefault();
                    alert('Por favor complete todos los campos requeridos.');
                }
            });
        });
    };

    // ===========================================
    // BUSINESS HOURS - OPEN/CLOSED STATUS
    // ===========================================
    const initBusinessHours = () => {
        const hoursElement = document.getElementById('business-hours-status');
        if (!hoursElement) return;

        const hours = JSON.parse(hoursElement.dataset.hours || '{}');
        const now = new Date();
        const day = now.toLocaleDateString('es-PY', { weekday: 'long' }).toLowerCase();
        const currentTime = now.getHours() * 60 + now.getMinutes();

        const todayHours = hours[day];
        if (!todayHours || todayHours === 'Cerrado') {
            hoursElement.innerHTML = '<span class="text-red-500">● Cerrado ahora</span>';
            return;
        }

        // Parse hours (format: "08:00 - 18:00")
        const match = todayHours.match(/(\d{2}):(\d{2})\s*-\s*(\d{2}):(\d{2})/);
        if (match) {
            const openTime = parseInt(match[1]) * 60 + parseInt(match[2]);
            const closeTime = parseInt(match[3]) * 60 + parseInt(match[4]);

            if (currentTime >= openTime && currentTime <= closeTime) {
                const minutesLeft = closeTime - currentTime;
                if (minutesLeft <= 60) {
                    hoursElement.innerHTML = `<span class="text-amber-500">● Cierra pronto (${Math.round(minutesLeft)} min)</span>`;
                } else {
                    hoursElement.innerHTML = '<span class="text-green-500">● Abierto ahora</span>';
                }
            } else {
                hoursElement.innerHTML = '<span class="text-red-500">● Cerrado ahora</span>';
            }
        }
    };

    // ===========================================
    // PARALLAX EFFECT
    // ===========================================
    const initParallax = () => {
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        
        if (!parallaxElements.length) return;

        const handleParallax = () => {
            parallaxElements.forEach(element => {
                const speed = parseFloat(element.dataset.parallax) || 0.5;
                const rect = element.getBoundingClientRect();
                const scrolled = window.scrollY;
                
                if (rect.top < window.innerHeight && rect.bottom > 0) {
                    element.style.transform = `translateY(${scrolled * speed}px)`;
                }
            });
        };

        window.addEventListener('scroll', debounce(handleParallax, 10));
    };

    // ===========================================
    // COPY TO CLIPBOARD
    // ===========================================
    const initCopyToClipboard = () => {
        const copyBtns = document.querySelectorAll('[data-copy]');
        
        copyBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const text = btn.dataset.copy;
                navigator.clipboard.writeText(text).then(() => {
                    const originalText = btn.textContent;
                    btn.textContent = '¡Copiado!';
                    btn.classList.add('text-green-500');
                    setTimeout(() => {
                        btn.textContent = originalText;
                        btn.classList.remove('text-green-500');
                    }, 2000);
                });
            });
        });
    };

    // ===========================================
    // INITIALIZE ALL
    // ===========================================
    const init = () => {
        initMobileMenu();
        initNavbarScroll();
        initSmoothScroll();
        initScrollReveal();
        initCounters();
        initLightbox();
        initBackToTop();
        initLazyLoad();
        initFAQAccordion();
        initReviewsCarousel();
        initFormValidation();
        initBusinessHours();
        initParallax();
        initCopyToClipboard();

        // Add reveal classes to elements
        document.querySelectorAll('section > div > *:not(:first-child)').forEach(el => {
            if (!el.classList.contains('reveal')) {
                el.classList.add('reveal');
            }
        });

        console.log('✅ Premium Landing Page JS initialized');
    };

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
