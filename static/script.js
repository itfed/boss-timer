console.log("Таймер боссов загружен!");

// Глобальные переменные
let bossData = {};
let autoRefreshInterval;
let historyData = [];
let lastKillTimestamps = {}; // Храним время последнего убийства для каждого босса
let historyCollapsed = {}; // Храним состояние свернутости истории для каждого босса

// Глобальные переменные для моря и глубины (теперь используем серверные таймеры)
let seaTimer = 2 * 60 * 60; // 2 часа в секундах
let depthTimer = 2 * 60 * 60; // 2 часа в секундах
let seaRunning = false;
let depthRunning = false;
let seaInterval = null;
let depthInterval = null;

// Загружаем сохраненные времена нажатий из localStorage
function loadKillTimestamps() {
    try {
        const saved = localStorage.getItem('bossKillTimestamps');
        if (saved) {
            lastKillTimestamps = JSON.parse(saved);
            console.log("Загружены сохраненные времена нажатий:", lastKillTimestamps);
        }
    } catch (e) {
        console.error("Ошибка загрузки времён нажатий:", e);
        lastKillTimestamps = {};
    }
}

// Сохраняем времена нажатий в localStorage
function saveKillTimestamps() {
    try {
        localStorage.setItem('bossKillTimestamps', JSON.stringify(lastKillTimestamps));
    } catch (e) {
        console.error("Ошибка сохранения времён нажатий:", e);
    }
}

// Инициализация при загрузке страницы
loadKillTimestamps();

// Автообновление состояния кнопок каждые 30 секунд
setInterval(async () => {
    try {
        // Загружаем актуальные данные с сервера
        await loadBosses();
        console.log("Автообновление состояния кнопок");
    } catch (error) {
        console.log("Автообновление не удалось:", error);
    }
}, 30000); // 30 секунд

// Функция для переключения отображения истории босса
function toggleBossHistory(bossId) {
    const historyContainer = document.getElementById(`history-${bossId}`);
    const header = historyContainer.previousElementSibling;
    const toggleIcon = header.querySelector('.toggle-icon');
    
    if (historyContainer.style.display === 'none' || !historyContainer.style.display) {
        // Развернуть
        historyContainer.style.display = 'block';
        toggleIcon.textContent = '▲';
        historyCollapsed[bossId] = false;
        
        // Загружаем историю если она еще не загружена
        if (historyContainer.innerHTML.includes('Загрузка')) {
            displayBossHistory(bossId);
        }
    } else {
        // Свернуть
        historyContainer.style.display = 'none';
        toggleIcon.textContent = '▼';
        historyCollapsed[bossId] = true;
    }
}

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
        
        // Загружаем историю
        await loadHistory();

    } catch (error) {
        console.error("Ошибка загрузки:", error);
        showError(`Не удалось загрузить данные: ${error.message}`);
    }
}

// Отображение боссов
function displayBosses() {
    console.log("=== displayBosses вызван ===");
    console.log("bossData:", bossData);
    
    const container = document.getElementById('bosses-container');

    if (!bossData || Object.keys(bossData).length === 0) {
        container.innerHTML = '<div class="error">Нет данных о боссах</div>';
        return;
    }

    let html = '';

// Сортируем боссов по приоритету:
    // 1. Петушара (ID 2) - всегда первый
    // 2. В РЕСПАВНЕ (ближе к появлению - выше)
    // 3. ВОЗРОЖДАЕТСЯ (ближе к мин. респавну - выше)
    // 4. Не убит (в конце)
    const sortedBosses = Object.entries(bossData).sort((a, b) => {
        const [idA, bossA] = a;
        const [idB, bossB] = b;
        
        // Петушара всегда первый (ID 2)
        if (idA === '2') return -1;
        if (idB === '2') return 1;
        
        // Не убитые в самый конец
        const killedA = bossA.killed || false;
        const killedB = bossB.killed || false;
        
        if (!killedA && !killedB) return 0; // Оба не убиты
        if (!killedA) return 1; // A не убит - в конец
        if (!killedB) return -1; // B не убит - в конец
        
        // Оба убиты - сортируем по статусу и времени
        const statusA = bossA.status;
        const statusB = bossB.status;
        
        // В РЕСПАВНЕ выше чем ВОЗРОЖДАЕТСЯ
        if (statusA === 'В РЕСПАВНЕ' && statusB === 'ВОЗРОЖДАЕТСЯ') return -1;
        if (statusA === 'ВОЗРОЖДАЕТСЯ' && statusB === 'В РЕСПАВНЕ') return 1;
        
        // Внутри одного статуса - сортируем по времени (меньше времени = выше)
        const timeLeftA = bossA.time_left || '99:99:99';
        const timeLeftB = bossB.time_left || '99:99:99';
        
        return timeLeftA.localeCompare(timeLeftB);
    });

    for (const [bossId, boss] of sortedBosses) {
        // Определяем класс статуса
        let statusClass = 'status ';
        if (boss.status === 'Не убит') {
            statusClass += 'alive';
            boss.status = 'НЕ УБИТ'; // Изменяем текст на большие буквы
        }
        else if (boss.status === 'ВОЗРОЖДАЕТСЯ') statusClass += 'respawning';
        else if (boss.status === 'В РЕСПАВНЕ') statusClass += 'respawning-now';
        else statusClass += 'ready';

        html += `
            <div class="boss-card">
                <div class="first-row">
                    <div class="boss-header">
                        <div class="boss-icon">${boss.icon || '👾'}</div>
                        <div class="boss-title">
                            <h2>${boss.name}</h2>
                            <div class="respawn-range">${boss.respawn_range || ''}</div>
                        </div>
                    </div>

                    <!-- Статус отдельно -->
                    <div class="boss-status">
                        <span class="${statusClass}">${boss.status}</span>
                    </div>

                    <div class="timer-section">
                        <div class="timer" id="timer-${bossId}">
                            ${boss.time_left}
                        </div>
                        <div class="timer-label">${boss.timer_label || 'До возрождения:'}</div>
                    </div>

                    <!-- Информация об убийстве -->
                    <div class="boss-kill-info">
                        <div class="info-row">
                            <span class="label">🗡️ Убит:</span>
                            <span class="kill-time" onclick="${boss.killed ? `openEditModal(${bossId})` : ''}">
                                ${boss.last_kill || '--:--:--'}
                            </span>
                        </div>
                        <div class="info-row">
                            <span class="label">⏱️ Появится с:</span>
                            <span class="value">${boss.min_respawn_time || '--:--:--'}</span>
                        </div>
                    </div>

                    <!-- Кнопка истории в первой строке -->
                    <div class="boss-history-trigger" onclick="toggleBossHistoryInRow(${bossId})">
                        <span class="history-text">История:</span>
                        <span class="toggle-icon">▼</span>
                    </div>

                    <div class="boss-actions">
                        <button class="kill-btn" onclick="markBossKilled(${bossId})">
                            Босс убит!
                        </button>
                    </div>
                </div>
                
                <div class="second-row">
                    <div class="boss-history">
                        <div class="history-list-small" id="history-${bossId}" style="display: none;">
                            <div class="loading-history">Загрузка...</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    container.innerHTML = html;
    
    // Обновляем визуальное состояние кнопок после отображения
    updateKillButtonStates();
}

// Новая функция для переключения истории в первой строке
function toggleBossHistoryInRow(bossId) {
    const trigger = event.currentTarget;
    const historyList = document.getElementById(`history-${bossId}`);
    
    if (historyList.style.display === 'none' || !historyList.style.display) {
        // Показываем историю
        historyList.style.display = 'block';
        trigger.classList.add('expanded');
        
        // Загружаем историю если еще не загружена
        if (historyList.querySelector('.loading-history')) {
            displayBossHistory(bossId);
        }
    } else {
        // Скрываем историю
        historyList.style.display = 'none';
        trigger.classList.remove('expanded');
    }
}

// Проверить, можно ли нажать кнопку убийства
function canKillBoss(bossId) {
    const lastKillTime = lastKillTimestamps[bossId];
    if (!lastKillTime) return true; // Никогда не нажимали
    
    const now = Date.now();
    const fiveMinutes = 5 * 60 * 1000; // 5 минут в миллисекундах
    
    return (now - lastKillTime) >= fiveMinutes;
}

// Обновить визуальное состояние кнопок
function updateKillButtonStates() {
    // Находим все кнопки убийства
    const killButtons = document.querySelectorAll('.kill-btn');
    
    killButtons.forEach(button => {
        // Извлекаем bossId из onclick атрибута
        const onclickAttr = button.getAttribute('onclick');
        const bossIdMatch = onclickAttr?.match(/markBossKilled\((\d+)\)/);
        
        if (bossIdMatch) {
            const bossId = bossIdMatch[1];
            
            if (!canKillBoss(bossId)) {
                // Блокируем кнопку
                button.disabled = true;
                button.classList.add('disabled');
                button.textContent = 'Уже нажали';
                
                // Добавляем таймер обратного отсчета
                const lastKillTime = lastKillTimestamps[bossId];
                const remainingTime = 5 * 60 * 1000 - (Date.now() - lastKillTime);
                const seconds = Math.ceil(remainingTime / 1000);
                const minutes = Math.floor(seconds / 60);
                const secs = seconds % 60;
                
                if (seconds > 0) {
                    button.title = `Доступно через ${minutes}:${secs.toString().padStart(2, '0')}`;
                }
            } else {
                // Разблокируем кнопку
                button.disabled = false;
                button.classList.remove('disabled');
                button.textContent = 'Босс убит!';
                button.title = '';
            }
        }
    });
}

// Отметить босса убитым
async function markBossKilled(bossId) {
    // Проверяем блокировку
    if (!canKillBoss(bossId)) {
        const lastKillTime = lastKillTimestamps[bossId];
        const remainingTime = 5 * 60 * 1000 - (Date.now() - lastKillTime);
        const minutes = Math.ceil(remainingTime / 60000);
        
        showNotification(`❌ Уже нажали! Подожди еще ${minutes} мин.`);
        return;
    }
    
    // Улучшенный диалог подтверждения
    const bossName = bossData[bossId]?.name || `Босс #${bossId}`;
    
    const confirmed = await showConfirmDialog(
        `⚠️ ВНИМАНИЕ!`,
        `Ты уверен, что хочешь отметить "${bossName}" как убитого?<br><br>`
    );
    
    if (!confirmed) return;

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
            // Сохраняем время последнего нажатия
            lastKillTimestamps[bossId] = Date.now();
            saveKillTimestamps(); // Сохраняем в localStorage
            await loadBosses(); // Перезагружаем данные
            // Обновляем визуальное состояние кнопок
            updateKillButtonStates();
        } else {
            showNotification(`❌ ${result.error || result.message}`);
        }

    } catch (error) {
        console.error("Ошибка:", error);
        showNotification('❌ Ошибка при отправке данных');
    }
}

// Сбросить все таймеры
async function resetAllTimers() {
    if (!confirm('Сбросить ВСЕ таймеры?')) {
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

// Авто-сброс таймеров боссов (устарело - теперь делается на сервере)
function checkAndResetBossTimers() {
    // Больше не используется - сброс происходит на сервере
    // при достижении максимального времени респавна
    console.log("Авто-сброс таймеров отключен - обработка на сервере");
}

// Сброс таймера конкретного босса
async function resetBossTimer(bossId) {
    try {
        const response = await fetch(`/reset_boss_timer/${bossId}`, {
            method: 'POST',
        });
        
        if (response.ok) {
            console.log(`Таймер босса ${bossId} сброшен`);
            await loadBosses(); // Обновляем интерфейс
        }
    } catch (error) {
        console.error(`Ошибка сброса таймера босса ${bossId}:`, error);
    }
}

// ПРОСТАЯ функция для московского времени (UTC+3)
function updateServerTime() {
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

// Загрузка истории
async function loadHistory() {
    try {
        console.log("Запрашиваем историю...");
        const response = await fetch('/get_history');
        console.log("Статус ответа:", response.status);
        
        historyData = await response.json();
        console.log("Полученные данные истории:", historyData);
        
        // Обновляем историю для каждого босса
        for (const bossId in bossData) {
            displayBossHistory(bossId);
        }
        
        // Обновляем глобальную историю
        displayGlobalHistory();
        
    } catch (error) {
        console.error("Ошибка загрузки истории:", error);
        showNotification('❌ Ошибка загрузки истории');
    }
}

// Отобразить историю для конкретного босса
function displayBossHistory(bossId) {
    console.log(`=== displayBossHistory для босса ${bossId} ===`);
    
    const container = document.getElementById(`history-${bossId}`);
    console.log(`Ищем контейнер для босса ${bossId}:`, container);
    
    if (!container) {
        console.warn(`Контейнер истории для босса ${bossId} не найден`);
        return;
    }
    
    console.log("Вся история:", historyData);
    const bossHistory = historyData.filter(record => 
        record.boss_id == bossId && (record.action_type === 'kill' || record.action_type === 'manual_edit')
    ).sort((a, b) => b.id - a.id) // Сортируем по убыванию ID (новые первыми)
    .slice(0, 3); // Берем первые 3 (самые новые)
    
    console.log(`История для босса ${bossId}:`, bossHistory);
    
    if (bossHistory.length === 0) {
        container.innerHTML = '<div class="no-history">Нет истории</div>';
        return;
    }
    
    let html = '';
    bossHistory.forEach(record => {
        const actionText = record.action_type === 'kill' ? 'Убит' : 'Изменено';
        const actionClass = record.action_type === 'kill' ? 'kill-action' : 'edit-action';
        
        // Проверяем наличие time_only
        const timeDisplay = record.time_only || record.timestamp_formatted || '--:--:--';
        
        html += `
            <div class="history-item-small ${actionClass}">
                <span class="action-type">${actionText}</span>
                <span class="action-time">${timeDisplay}</span>
            </div>
        `;
    });
    
    container.innerHTML = html;
    console.log(`Обновлён контейнер для босса ${bossId}`);
}

// Отобразить глобальную историю
function displayGlobalHistory() {
    const container = document.getElementById('kill-history');
    if (!container) return;
    
    if (historyData.length === 0) {
        container.innerHTML = '<div class="no-history">История пуста</div>';
        return;
    }
    
    let html = '';
    historyData.sort((a, b) => b.id - a.id) // Сортируем по убыванию ID
              .slice(0, 10) // Берем первые 10 (самые новые)
              .forEach(record => {
        let icon = '📝';
        let actionText = '';
        
        switch(record.action_type) {
            case 'kill':
                icon = '🗡️';
                actionText = 'убил';
                break;
            case 'manual_edit':
                icon = '⏰';
                actionText = 'изменил время';
                break;
            case 'reset':
                icon = '🔄';
                actionText = 'сбросил все таймеры';
                break;
            case 'undo':
                icon = '↩️';
                actionText = 'отменил действие';
                break;
        }
        
        html += `
            <div class="history-item">
                <div class="history-boss">
                    <span class="history-icon">${icon}</span>
                    <span class="history-action">${record.boss_name} ${actionText}</span>
                </div>
                <div class="history-time">${record.time_only}</div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Открыть модальное окно редактирования
function openEditModal(bossId) {
    const boss = bossData[bossId];
    if (!boss) return;
    
    const currentTime = boss.last_kill || '';
    
    const modalHtml = `
        <div class="modal-overlay" id="edit-modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>⏰ Редактировать время убийства</h3>
                    <button class="modal-close" onclick="closeModal()">×</button>
                </div>
                <div class="modal-body">
                    <p><strong>Босс:</strong> ${boss.name}</p>
                    <p><strong>Текущее время:</strong> ${currentTime || 'Не задано'}</p>
                    
                    <div class="form-group">
                        <label for="edit-time">Новое время (ЧЧ:ММ):</label>
                        <input type="text" id="edit-time" placeholder="14:30" maxlength="5">
                        <small>Формат: ЧЧ:ММ (например: 14:30)</small>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-cancel" onclick="closeModal()">Отмена</button>
                    <button class="btn-confirm" onclick="saveManualEdit(${bossId})">Сохранить</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Фокус на поле ввода
    setTimeout(() => {
        document.getElementById('edit-time').focus();
    }, 100);
}

// Закрыть модальное окно
function closeModal() {
    const modal = document.getElementById('edit-modal');
    if (modal) {
        modal.remove();
    }
}

// Сохранить ручное редактирование
async function saveManualEdit(bossId) {
    const timeInput = document.getElementById('edit-time');
    const timeValue = timeInput.value.trim();
    
    if (!timeValue) {
        showNotification('❌ Введи время');
        return;
    }
    
    // Простая валидация формата
    const timeRegex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/;
    if (!timeRegex.test(timeValue)) {
        showNotification('❌ Неверный формат времени (ЧЧ:ММ)');
        return;
    }
    
    try {
        const response = await fetch(`/manual_edit_time/${bossId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ time: timeValue })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`✅ ${result.message}`);
            closeModal();
            await loadBosses(); // Перезагружаем данные
        } else {
            showNotification(`❌ ${result.error}`);
        }
        
    } catch (error) {
        console.error("Ошибка:", error);
        showNotification('❌ Ошибка при сохранении');
    }
}

// Очистить историю
async function clearHistory() {
    if (historyData.length === 0) {
        showNotification('ℹ️ История уже пуста');
        return;
    }
    
    const confirmed = await showConfirmDialog(
        '🗑️ Очистка истории',
        `Ты уверен, что хочешь очистить всю историю?<br><br>` +
        `<strong>Будет удалено:</strong> ${historyData.length} записей<br>`
    );
    
    if (!confirmed) return;
    
    try {
        const response = await fetch('/clear_history', {
            method: 'POST',
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`✅ ${result.message}`);
            await loadBosses(); // Перезагружаем все данные
        } else {
            showNotification(`❌ ${result.error}`);
        }
        
    } catch (error) {
        console.error("Ошибка:", error);
        showNotification('❌ Ошибка при очистке истории');
    }
}

// Откатить последнее действие
async function undoLastAction() {
    if (historyData.length === 0) {
        showNotification('❌ История пуста');
        return;
    }
    
    // Сортируем по ID по убыванию и берем самую новую запись
    const sortedHistory = [...historyData].sort((a, b) => b.id - a.id);
    const lastAction = sortedHistory[0];
    let actionDesc = '';
    
    switch(lastAction.action_type) {
        case 'kill':
            actionDesc = `убийство ${lastAction.boss_name}`;
            break;
        case 'manual_edit':
            actionDesc = `изменение времени ${lastAction.boss_name}`;
            break;
        case 'reset':
            actionDesc = 'сброс всех таймеров';
            break;
        default:
            actionDesc = 'действие';
    }
    
    const confirmed = await showConfirmDialog(
        '↩️ Откат действия',
        `Ты уверен, что хочешь отменить последнее действие?<br><br>` +
        `<strong>Будет отменено:</strong> ${actionDesc}<br>` +
        `<strong>Время:</strong> ${lastAction.time_only}`
    );
    
    if (!confirmed) return;
    
    try {
        const response = await fetch('/undo_last_action', {
            method: 'POST',
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`✅ ${result.message}`);
            await loadBosses(); // Перезагружаем все данные
            
            // Снимаем блокировку для отмененного босса
            if (lastAction.boss_id) {
                delete lastKillTimestamps[lastAction.boss_id];
                console.log(`Снята блокировка для босса ${lastAction.boss_id}`);
            }
            
            // Сохраняем обновленные времена
            saveKillTimestamps();
            
            // Обновляем визуальное состояние кнопок
            updateKillButtonStates();
        } else {
            showNotification(`❌ ${result.error}`);
        }
        
    } catch (error) {
        console.error("Ошибка:", error);
        showNotification('❌ Ошибка при откате');
    }
}

// Улучшенный диалог подтверждения
function showConfirmDialog(title, message) {
    return new Promise((resolve) => {
        const dialogHtml = `
            <div class="modal-overlay" id="confirm-dialog">
                <div class="modal-content confirm-dialog">
                    <div class="modal-header">
                        <h3>${title}</h3>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button class="btn-cancel" onclick="handleConfirm(false)">Отмена</button>
                        <button class="btn-confirm" onclick="handleConfirm(true)">Подтвердить</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', dialogHtml);
        
        window.handleConfirm = function(result) {
            const dialog = document.getElementById('confirm-dialog');
            if (dialog) dialog.remove();
            resolve(result);
        };
    });
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
    
    /* Стили для модальных окон */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 2000;
    }
    
    .modal-content {
        background: #1e1e2e;
        border-radius: 15px;
        padding: 0;
        min-width: 400px;
        max-width: 90vw;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .modal-header {
        padding: 20px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .modal-header h3 {
        margin: 0;
        color: #00c6ff;
    }
    
    .modal-close {
        background: none;
        border: none;
        color: #aaa;
        font-size: 24px;
        cursor: pointer;
        padding: 0;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .modal-body {
        padding: 20px;
    }
    
    .modal-footer {
        padding: 15px 20px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: flex-end;
        gap: 10px;
    }
    
    .btn-cancel, .btn-confirm {
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-weight: bold;
    }
    
    .btn-cancel {
        background: rgba(255, 255, 255, 0.1);
        color: white;
    }
    
    .btn-confirm {
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color: white;
    }
    
    .form-group {
        margin: 15px 0;
    }
    
    .form-group label {
        display: block;
        margin-bottom: 5px;
        color: #aaa;
    }
    
    .form-group input {
        width: 100%;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(0, 0, 0, 0.3);
        color: white;
        font-size: 16px;
    }
    
    .form-group small {
        display: block;
        margin-top: 5px;
        color: #777;
        font-size: 12px;
    }
    
    /* Стили для истории */
    .boss-history {
        margin-top: 20px;
        padding-top: 15px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .boss-history h4 {
        color: #00c6ff;
        margin-bottom: 10px;
        font-size: 1rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .history-list-small {
        max-height: 120px;
        overflow-y: auto;
    }
    
    .history-item-small {
        display: flex;
        justify-content: space-between;
        padding: 8px 12px;
        margin-bottom: 5px;
        border-radius: 6px;
        font-size: 0.9rem;
    }
    
    .kill-action {
        background: rgba(76, 175, 80, 0.1);
        border-left: 3px solid #4caf50;
    }
    
    .edit-action {
        background: rgba(255, 193, 7, 0.1);
        border-left: 3px solid #FFC107;
    }
    
    .action-type {
        font-weight: bold;
    }
    
    .action-time {
        color: #aaa;
        font-family: 'Courier New', monospace;
    }
    
    .no-history {
        color: #777;
        font-style: italic;
        text-align: center;
        padding: 10px;
    }
    
    .confirm-dialog .modal-body p {
        line-height: 1.6;
    }
`;
document.head.appendChild(style);

// Инициализация таймеров моря и глубины (загружаем с сервера)
async function initSeaDepthTimers() {
    try {
        const response = await fetch('/get_sea_depth_timers');
        const data = await response.json();
        
        seaTimer = data.sea_timer;
        depthTimer = data.depth_timer;
        seaRunning = data.sea_running;
        depthRunning = data.depth_running;
        
        updateSeaDisplay();
        updateDepthDisplay();
        
        // Запускаем интервалы обновления если таймеры активны
        if (seaRunning) startSeaTimer();
        if (depthRunning) startDepthTimer();
    } catch (error) {
        console.error('Ошибка загрузки общих таймеров:', error);
        // Используем значения по умолчанию
        updateSeaDisplay();
        updateDepthDisplay();
    }
}

// Запуск таймера моря
function startSeaTimer() {
    if (seaInterval) clearInterval(seaInterval);
    
    seaInterval = setInterval(() => {
        if (seaRunning && seaTimer > 0) {
            seaTimer--;
            updateSeaDisplay();
            
            // Останавливаем таймер когда он достигает 0
            if (seaTimer <= 0) {
                seaRunning = false;
                updateSeaDisplay();
                showNotification('🔔 Таймер Море завершен!');
            }
        }
    }, 1000);
}

// Запуск таймера глубины
function startDepthTimer() {
    if (depthInterval) clearInterval(depthInterval);
    
    depthInterval = setInterval(() => {
        if (depthRunning && depthTimer > 0) {
            depthTimer--;
            updateDepthDisplay();
            
            // Останавливаем таймер когда он достигает 0
            if (depthTimer <= 0) {
                depthRunning = false;
                updateDepthDisplay();
                showNotification('🔔 Таймер Глубина завершен!');
            }
        }
    }, 1000);
}

// Обновление отображения моря
function updateSeaDisplay() {
    const seaElement = document.getElementById('sea-timer');
    if (seaElement) {
        seaElement.textContent = formatTime(seaTimer);
        // Добавляем визуальный индикатор остановки
        if (!seaRunning) {
            seaElement.style.color = '#888888'; // Серый когда остановлен
        } else {
            seaElement.style.color = '#00FFFF'; // Голубой когда работает
        }
    }
}

// Обновление отображения глубины
function updateDepthDisplay() {
    const depthElement = document.getElementById('depth-timer');
    if (depthElement) {
        depthElement.textContent = formatTime(depthTimer);
        // Добавляем визуальный индикатор остановки
        if (!depthRunning) {
            depthElement.style.color = '#888888'; // Серый когда остановлен
        } else {
            depthElement.style.color = '#00FFFF'; // Голубой когда работает
        }
    }
}

// Сброс таймера моря (оставляю для совместимости)
function resetSeaTimer() {
    updateSeaDepthTimer('sea', 'reset');
}

// Переключение таймера моря (плей/пауза)
function toggleSeaTimer() {
    updateSeaDepthTimer('sea', seaRunning ? 'stop' : 'start');
}

// Остановка таймера моря (установка на 2 часа и остановка)
// stopSeaTimer удален - используем toggleSeaTimer

// Сброс таймера глубины (оставляю для совместимости)
function resetDepthTimer() {
    updateSeaDepthTimer('depth', 'reset');
}

// Переключение таймера глубины (плей/пауза)
function toggleDepthTimer() {
    updateSeaDepthTimer('depth', depthRunning ? 'stop' : 'start');
}

// Остановка таймера глубины (установка на 2 часа и остановка)
// stopDepthTimer удален - используем toggleDepthTimer

// Обновление таймера через API
async function updateSeaDepthTimer(timerType, action) {
    try {
        const response = await fetch(`/update_sea_depth_timer/${timerType}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action: action })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Обновляем состояние таймера
            if (timerType === 'sea') {
                seaTimer = data.sea_timer || 2 * 60 * 60;
                seaRunning = data.sea_running !== undefined ? data.sea_running : seaRunning;
                
                // Перезапускаем интервал если таймер запущен
                if (seaInterval) clearInterval(seaInterval);
                if (seaRunning) startSeaTimer();
                
                updateSeaDisplay();
            } else if (timerType === 'depth') {
                depthTimer = data.depth_timer || 2 * 60 * 60;
                depthRunning = data.depth_running !== undefined ? data.depth_running : depthRunning;
                
                // Перезапускаем интервал если таймер запущен
                if (depthInterval) clearInterval(depthInterval);
                if (depthRunning) startDepthTimer();
                
                updateDepthDisplay();
            }
            
            showNotification(data.message);
        } else {
            showNotification(`Ошибка: ${data.message || data.error}`);
        }
    } catch (error) {
        console.error('Ошибка обновления таймера:', error);
        showNotification('Ошибка связи с сервером');
    }
}

// Форматирование времени (ЧЧ:ММ:СС)
function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// Когда страница загрузится
document.addEventListener('DOMContentLoaded', function() {
    console.log("Страница загружена, инициализируем...");
    
    // Загружаем сохраненные времена нажатий
    loadKillTimestamps();
    
    // Инициализируем таймеры моря и глубины
    initSeaDepthTimers();
    
    // Загружаем данные боссов
    loadBosses();
    
    // Обновляем время сервера
    updateServerTime();
    setInterval(updateServerTime, 1000);
});

// Очистка интервалов при закрытии страницы
window.addEventListener('beforeunload', function() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
});