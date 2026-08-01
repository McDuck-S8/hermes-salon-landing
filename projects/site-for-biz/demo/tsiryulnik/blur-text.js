/* blur-text.js — vanilla JS port of BlurText from react-bits/svelte-bits
 * Паттерн: слова появляются по одному с блюром при скролле
 * Использование: <p class="blur-text" data-delay="150">Текст для анимации</p>
 */
(function() {
    function initBlurText() {
        document.querySelectorAll('.blur-text').forEach(el => {
            const text = el.textContent.trim();
            const delay = parseInt(el.dataset.delay || '150');
            const animateBy = el.dataset.animate || 'words'; // 'words' or 'letters'

            const segments = animateBy === 'letters' ? text.split('') : text.split(' ');
            el.innerHTML = '';
            el.style.display = 'flex';
            el.style.flexWrap = 'wrap';

            segments.forEach((seg, i) => {
                const span = document.createElement('span');
                span.className = 'blur-word';
                span.style.transitionDelay = (i * delay) + 'ms';
                span.textContent = seg === ' ' ? '\u00A0' : seg;
                if (animateBy === 'words' && i < segments.length - 1) {
                    span.appendChild(document.createTextNode('\u00A0'));
                }
                el.appendChild(span);
            });

            const observer = new IntersectionObserver(([entry]) => {
                if (entry.isIntersecting) {
                    el.classList.add('blur-text-active');
                    observer.unobserve(el);
                }
            }, { threshold: 0.1 });
            observer.observe(el);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initBlurText);
    } else {
        initBlurText();
    }
})();
