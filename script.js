document.addEventListener('DOMContentLoaded', () => {
    // Анимация появления элементов при прокрутке
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Добавляем классы для анимации к карточкам и секциям
    document.querySelectorAll('.card, .graph-container, .conclusion-box').forEach(el => {
        el.classList.add('hidden');
        observer.observe(el);
    });

    // Логика Каруселей
    document.querySelectorAll('.carousel-wrapper').forEach(wrapper => {
        const track = wrapper.querySelector('.carousel-track');
        const prevBtn = wrapper.querySelector('.carousel-prev');
        const nextBtn = wrapper.querySelector('.carousel-next');

        if (prevBtn && nextBtn && track) {
            prevBtn.addEventListener('click', () => {
                const cardWidth = track.firstElementChild.offsetWidth + 30; // 30 is gap
                track.scrollBy({ left: -cardWidth, behavior: 'smooth' });
            });

            nextBtn.addEventListener('click', () => {
                const cardWidth = track.firstElementChild.offsetWidth + 30;
                track.scrollBy({ left: cardWidth, behavior: 'smooth' });
            });
        }
    });

    // Логика Мини-игры "Генератор архетипа" (с эффектом рулетки)
    const archetypes = [
        { icon: '⚡', title: 'Громовержец', desc: 'Ваш архетип — лидер и защитник. Вы берете ответственность на себя и способны разрубить любую проблему, как Зевс, Тор или Перун.' },
        { icon: '🌸', title: 'Божество любви', desc: 'Ваш архетип — созидатель. Вы приносите в мир гармонию, красоту и страсть, подобно Афродите, Фрейе или Ладе.' },
        { icon: '👁️', title: 'Трикстер / Мудрец', desc: 'Ваш архетип — интеллектуал. Вы находите нестандартные решения и обладаете тайными знаниями, как Один, Велес или Гермес.' },
        { icon: '💀', title: 'Хранитель тайн', desc: 'Ваш архетип — страж границ. Вы спокойны, глубоки и не боитесь смотреть в лицо неизвестности, как Аид, Хель или Марена.' },
        { icon: '🧵', title: 'Творец судьбы', desc: 'Ваш архетип — стратег. Вы плетете нити событий и видите картину целиком, подобно Норнам или Макоши.' },
        { icon: '☀️', title: 'Божество Солнца', desc: 'Ваш архетип — источник света. Вы согреваете окружающих, дарите надежду и всегда находитесь в центре внимания, как Аполлон или Даждьбог.' },
        { icon: '🌊', title: 'Владыка Морей', desc: 'Ваш архетип — стихия. Ваши эмоции глубоки, как океан. Вы можете быть спокойным штилем или сокрушительным штормом, как Посейдон или Ньёрд.' },
        { icon: '🔥', title: 'Кузнец / Творец', desc: 'Ваш архетип — мастер. Вы создаете невероятные вещи своими руками и упорным трудом, подобно Гефесту или Сварогу.' },
        { icon: '🏹', title: 'Охотник / Воин', desc: 'Ваш архетип — целеустремленность. Вы всегда достигаете своей цели и защищаете слабых, как Артемида или Тюр.' },
        { icon: '🌾', title: 'Покровитель природы', desc: 'Ваш архетип — гармония. Вы черпаете силы в лесах и полях, заботясь обо всем живом, как Деметра или Фрейр.' }
    ];

    const btnDraw = document.getElementById('draw-runes');
    const resultBox = document.getElementById('rune-result');
    const resultIcon = document.getElementById('result-icon');
    const resultTitle = document.getElementById('result-title');
    const resultDesc = document.getElementById('result-desc');

    if (btnDraw) {
        btnDraw.addEventListener('click', () => {
            resultBox.classList.remove('hidden');
            btnDraw.disabled = true;
            btnDraw.style.opacity = '0.5';
            
            // Эффект рулетки (карусели)
            let ticks = 0;
            const maxTicks = 20; // Сколько раз сменится картинка
            const intervalTime = 100; // Скорость смены (мс)

            const roulette = setInterval(() => {
                const randomArc = archetypes[Math.floor(Math.random() * archetypes.length)];
                resultIcon.textContent = randomArc.icon;
                resultTitle.textContent = randomArc.title;
                resultDesc.textContent = 'Читаем нити судьбы...';
                ticks++;

                if (ticks >= maxTicks) {
                    clearInterval(roulette);
                    // Финальный результат
                    const finalArc = archetypes[Math.floor(Math.random() * archetypes.length)];
                    resultIcon.textContent = finalArc.icon;
                    resultTitle.textContent = finalArc.title;
                    resultDesc.textContent = finalArc.desc;
                    
                    btnDraw.disabled = false;
                    btnDraw.style.opacity = '1';
                    btnDraw.textContent = 'Бросить руны еще раз 🎲';
                }
            }, intervalTime);
        });
    }

    // Плавная прокрутка для якорных ссылок
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});