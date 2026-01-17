// Функциональность поиска по боссам
let searchTimeout;

function setupBossSearch() {
    const searchInput = document.getElementById('boss-search');
    const clearButton = document.getElementById('clear-search');
    
    if (!searchInput || !clearButton) return;
    
    // Обработчик ввода
    searchInput.addEventListener('input', function() {
        const query = this.value.trim().toLowerCase();
        
        // Показываем/скрываем кнопку очистки
        clearButton.style.display = query ? 'flex' : 'none';
        
        // Откладываем поиск на 300мс для лучшей производительности
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            filterBosses(query);
        }, 300);
    });
    
    // Обработчик очистки
    clearButton.addEventListener('click', function() {
        searchInput.value = '';
        clearButton.style.display = 'none';
        filterBosses('');
    });
    
    // Обработчик Escape
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            searchInput.value = '';
            clearButton.style.display = 'none';
            filterBosses('');
            searchInput.blur();
        }
    });
}

function filterBosses(query) {
    const bossCards = document.querySelectorAll('.boss-card');
    
    bossCards.forEach(card => {
        const bossNameElement = card.querySelector('.boss-title h2');
        const bossName = bossNameElement ? bossNameElement.textContent.toLowerCase() : '';
        
        if (query === '' || bossName.includes(query)) {
            card.style.display = 'flex';
            card.style.opacity = '1';
        } else {
            card.style.display = 'none';
            card.style.opacity = '0.3';
        }
    });
}

// Инициализация поиска при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    setupBossSearch();
});