console.log("Таймер боссов загружен!");

// Глобальные переменные
let bossData = {};
let autoRefreshInterval;

// Основная функция загрузки боссов
async function loadBosses() {
    console.log("Загрузка данных боссов...");

    try {
        const response = await fetch('/get_boss_timers');

        if (!response.ok) {
            throw new Error(`Ошибка сервера: ${response.status}`);
        }

        bossData = await response.json();
        console.log("Данные получены:", bossData);

        displayBosses();

    } catch (error) {
        console.error("Ошибка загрузки:", error);
        showError(`Не удалось загрузить данные: ${error.message}`);
    }
}

// Отображение боссов
function displayBosses() {
    const container = document.getElementById('bosses-container');

    if (!bossData || Object.keys(bossData).length === 0) {
        container.innerHTML = '<div class="error">Нет данных о боссах</div>';
        return;
    }

    let html = '';

    for (const [bossId, boss] of Object.entries(bossData)) {
        // Определяем класс статуса
        let statusClass = 'status ';
        if (boss.status === 'Не убит') statusClass += 'alive';
        else if (boss.status === 'ВОЗРОЖДАЕТСЯ') statusClass += 'respawning';
        else if (boss.status === 'В РЕСПАВНЕ') statusClass += 'respawning-now';
        else statusClass += 'ready';

        html += `
            <div class="boss-card">
                <div class="boss-header">
                    <div class="boss-name">
                        <div class="boss-icon">${boss.icon || '👾'}</div>
                        <div class="boss-title">
                            <h2>${boss.name}</h2>
                            <div class="respawn-range">${boss.respawn_range || ''}</div>
                        </div>
                    </div>
                    <div class="boss-id">#${bossId}</div>
                </div>

                <div class="boss-info">
                    <div class="info-row">
                        <span class="label">📊 Статус:</span>
                        <span class="${statusClass}">${boss.status}</span>
                    </div>

                    <div class="timer" id="timer-${bossId}">
                        ${boss.time_left}
                    </div>

                    <div class="timer-label">${boss.timer_label || 'До возрождения:'}</div>

                    ${boss.killed ? `
                    <div class="info-row">
                        <span class="label">🗡️ Убит:</span>
                        <span class="kill-time">${boss.last_kill}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">⏱️ Прошло:</span>
                        <span class="value">${boss.time_since_kill || '--:--:--'}</span>
                    </div>
                    ` : ''}

                    <div class="info-row">
                        <span class="label">🎯 Диапазон:</span>
                        <span class="value">${boss.respawn_range || '--'}</span>
                    </div>
                </div>

                <div class="boss-actions">
                    <button class="kill-btn" onclick="markBossKilled(${bossId})">
                        🗡️ Босс убит!
                    </button>
                    <button class="details-btn" onclick="showDetails(${bossId})">
                        📋 Подробнее
                    </button>
                </div>
            </div>
        `;
    }

    container.innerHTML = html;
}

// Отметить босса убитым
async function markBossKilled(bossId) {
    if (!confirm(`Отметить босса как убитого?\nЭто обновит таймер у всех!`)) {
        return;
    }

    try {
        const response = await fetch(`/boss_killed/${bossId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        const result = await response.json();

        if (result.success) {
            showNotification(`✅ ${result.message}`);
            loadBosses(); // Перезагружаем данные
        } else {
            showNotification(`❌ Ошибка: ${result.message}`);
        }

    } catch (error) {
        console.error("Ошибка:", error);
        showNotification('❌ Ошибка при отправке данных');
    }
}

// Сбросить все таймеры
async function resetAllTimers() {
    if (!confirm('ВНИМАНИЕ!\nСбросить ВСЕ таймеры?\nЭто действие нельзя отменить!')) {
        return;
    }

    try {
        const response = await fetch('/reset_all', {
            method: 'POST',
        });

        const result = await response.json();

        if (result.success) {
            showNotification(`🔄 ${result.message}`);
            loadBosses();
        }

    } catch (error) {
        console.error("Ошибка:", error);
        showNotification('❌ Ошибка при сбросе таймеров');
    }
}

// Обновить все таймеры (для кнопки)
function refreshAllTimers() {
    console.log("Ручное обновление...");
    loadBosses();
}

// ПРОСТАЯ функция для московского времени (UTC+3)
function updateMoscowTime() {
    const timeElement = document.getElementById('server-time');
    if (!timeElement) return;

    const now = new Date();

    // Получаем UTC время
    const utcHours = now.getUTCHours();
    const utcMinutes = now.getUTCMinutes();
    const utcSeconds = now.getUTCSeconds();

    // Москва = UTC + 3 часа
    let moscowHours = utcHours + 3;
    if (moscowHours >= 24) moscowHours -= 24;

    // Форматируем
    const hours = moscowHours.toString().padStart(2, '0');
    const minutes = utcMinutes.toString().padStart(2, '0');
    const seconds = utcSeconds.toString().padStart(2, '0');

    timeElement.textContent = `${hours}:${minutes}:${seconds}`;
}

// Показать детали босса
function showDetails(bossId) {
    const boss = bossData[bossId];
    if (!boss) return;

    const details = `
        Босс: ${boss.name}
        ID: ${bossId}
        Статус: ${boss.status}
        Диапазон респавна: ${boss.respawn_range}
        ${boss.killed ? `Убит: ${boss.last_kill}` : 'Еще не убит'}
        ${boss.killed ? `Прошло с убийства: ${boss.time_since_kill}` : ''}
    `;

    alert(details);
}

// Показать уведомление
function showNotification(message) {
    // Создаем элемент уведомления
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(notification);

    // Удаляем через 3 секунды
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Показать ошибку
function showError(message) {
    const container = document.getElementById('bosses-container');
    container.innerHTML = `
        <div class="error-message" style="grid-column: 1 / -1; text-align: center; padding: 50px;">
            <h3 style="color: #ff416c;">⚠️ Ошибка загрузки</h3>
            <p style="margin: 15px 0;">${message}</p>
            <button onclick="loadBosses()" style="
                padding: 10px 20px;
                background: #00c6ff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            ">
                🔄 Повторить попытку
            </button>
        </div>
    `;
}

// Добавим стили для анимаций уведомлений
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }

    .error {
        color: #ff416c;
        text-align: center;
        padding: 40px;
        grid-column: 1 / -1;
    }
`;
document.head.appendChild(style);

// Когда страница загрузится
document.addEventListener('DOMContentLoaded', function() {
    console.log("Страница загружена, инициализируем...");

    // Обновляем московское время каждую секунду
    updateMoscowTime();
    setInterval(updateMoscowTime, 1000);

    // Загружаем боссов
    loadBosses();

    // Автообновление каждые 10 секунд
    autoRefreshInterval = setInterval(loadBosses, 10000);

    console.log("Инициализация завершена!");
});

// Очистка интервалов при закрытии страницы
window.addEventListener('beforeunload', function() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
});