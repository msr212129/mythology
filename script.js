const CULTURE_LABELS = {
    'греческая': 'Греция',
    'скандинавская': 'Скандинавия',
    'славянская': 'Славяне',
};

document.addEventListener('DOMContentLoaded', () => {
    const data = window.mythologyData || [];

    if (data.length) {
        renderAboutStats(data);
        renderGodsSection(data);
        renderArtifactsCarousel(data);
        initMinigame(data);
        renderConclusion(data);
    } else {
        showDataError();
    }

    initScrollAnimations();
    initCarousels();
    initSmoothScroll();
});

function showDataError() {
    const grid = document.getElementById('gods-grid');
    if (grid) {
        grid.innerHTML = `
            <p class="data-error">
                Данные не загружены. Запустите <code>python parser.py</code> и обновите страницу.
            </p>
        `;
    }
}

function renderAboutStats(data) {
    const statsEl = document.getElementById('data-stats');
    if (!statsEl) return;

    const counts = countByCulture(data);
    statsEl.textContent =
        `Из Википедии собрано ${data.length} богов: ` +
        `${counts['греческая'] || 0} греческих, ` +
        `${counts['скандинавская'] || 0} скандинавских, ` +
        `${counts['славянская'] || 0} славянских.`;
}

function countByCulture(data) {
    return data.reduce((acc, item) => {
        acc[item.культура] = (acc[item.культура] || 0) + 1;
        return acc;
    }, {});
}

function renderGodsSection(data) {
    const grid = document.getElementById('gods-grid');
    const filter = document.getElementById('culture-filter');
    if (!grid || !filter) return;

    const cultures = ['all', ...Object.keys(CULTURE_LABELS)];
    let activeCulture = 'all';

    const renderCards = () => {
        const filtered = activeCulture === 'all'
            ? data
            : data.filter(item => item.культура === activeCulture);

        grid.innerHTML = filtered.map(item => `
            <article class="card god-card">
                <div class="card-icon">${item.символ || '✨'}</div>
                <span class="culture-badge">${CULTURE_LABELS[item.культура] || item.культура}</span>
                <h3>${escapeHtml(item.имя_бога)}</h3>
                <p>${escapeHtml(item.функция)}</p>
            </article>
        `).join('');

        grid.querySelectorAll('.card').forEach(card => {
            card.classList.add('hidden');
            scrollObserver.observe(card);
        });
    };

    filter.innerHTML = cultures.map(culture => {
        const label = culture === 'all' ? 'Все культуры' : CULTURE_LABELS[culture];
        const active = culture === activeCulture ? ' active' : '';
        return `<button class="filter-btn${active}" data-culture="${culture}">${label}</button>`;
    }).join('');

    filter.addEventListener('click', (event) => {
        const button = event.target.closest('.filter-btn');
        if (!button) return;

        activeCulture = button.dataset.culture;
        filter.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.culture === activeCulture);
        });
        renderCards();
    });

    renderCards();
}

function renderArtifactsCarousel(data) {
    const track = document.getElementById('artifacts-track');
    if (!track) return;

    track.innerHTML = data.map(item => `
        <div class="artifact-card">
            <div class="artifact-icon">${item.символ || '✨'}</div>
            <h3>${escapeHtml(item.имя_бога)}</h3>
            <p class="artifact-culture">${CULTURE_LABELS[item.культура] || item.культура}</p>
            <p>${escapeHtml(item.функция)}</p>
        </div>
    `).join('');
}

function initMinigame(data) {
    const btnDraw = document.getElementById('draw-runes');
    const resultBox = document.getElementById('rune-result');
    const resultIcon = document.getElementById('result-icon');
    const resultTitle = document.getElementById('result-title');
    const resultDesc = document.getElementById('result-desc');

    if (!btnDraw || !data.length) return;

    btnDraw.addEventListener('click', () => {
        resultBox.classList.remove('hidden');
        btnDraw.disabled = true;
        btnDraw.style.opacity = '0.5';

        let ticks = 0;
        const maxTicks = 20;
        const intervalTime = 100;

        const roulette = setInterval(() => {
            const randomGod = data[Math.floor(Math.random() * data.length)];
            resultIcon.textContent = randomGod.символ || '✨';
            resultTitle.textContent = randomGod.имя_бога;
            resultDesc.textContent = 'Читаем нити судьбы...';
            ticks++;

            if (ticks >= maxTicks) {
                clearInterval(roulette);
                const finalGod = data[Math.floor(Math.random() * data.length)];
                resultIcon.textContent = finalGod.символ || '✨';
                resultTitle.textContent = `${finalGod.имя_бога} · ${CULTURE_LABELS[finalGod.культура]}`;
                resultDesc.textContent = finalGod.функция;

                btnDraw.disabled = false;
                btnDraw.style.opacity = '1';
                btnDraw.textContent = 'Бросить руны еще раз 🎲';
            }
        }, intervalTime);
    });
}

function renderConclusion(data) {
    const conclusionText = document.getElementById('conclusion-text');
    if (!conclusionText) return;

    const counts = countByCulture(data);
    conclusionText.innerHTML = `
        Парсер Википедии собрал <strong>${data.length}</strong> записей о богах
        (${counts['греческая'] || 0} греческих, ${counts['скандинавская'] || 0} скандинавских,
        ${counts['славянская'] || 0} славянских). Несмотря на разные имена и атрибуты,
        описания повторяют одни и те же роли: гром, море, мудрость, любовь, смерть.
        <strong>Человеческая психология универсальна.</strong>
    `;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

const scrollObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.1 });

function initScrollAnimations() {
    document.querySelectorAll('.graph-container, .conclusion-box').forEach(el => {
        el.classList.add('hidden');
        scrollObserver.observe(el);
    });
}

function initCarousels() {
    document.querySelectorAll('.carousel-wrapper').forEach(wrapper => {
        const track = wrapper.querySelector('.carousel-track');
        const prevBtn = wrapper.querySelector('.carousel-prev');
        const nextBtn = wrapper.querySelector('.carousel-next');

        if (prevBtn && nextBtn && track) {
            prevBtn.addEventListener('click', () => {
                const cardWidth = track.firstElementChild.offsetWidth + 30;
                track.scrollBy({ left: -cardWidth, behavior: 'smooth' });
            });

            nextBtn.addEventListener('click', () => {
                const cardWidth = track.firstElementChild.offsetWidth + 30;
                track.scrollBy({ left: cardWidth, behavior: 'smooth' });
            });
        }
    });
}

function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
}
