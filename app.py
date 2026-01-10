from flask import Flask, render_template, jsonify, request
import datetime
import json
import os
from datetime import timezone, timedelta

app = Flask(__name__)

# Хранение ВСЕХ данных
DATA_FILE = 'boss_timers.json'
HISTORY_FILE = 'actions_history.json'

# Московское время (UTC+3)
MOSCOW_UTC_OFFSET = timedelta(hours=3)
MOSCOW_TIMEZONE = timezone(MOSCOW_UTC_OFFSET)

def get_moscow_time():
    """Получить текущее московское время (UTC+3)"""
    # Получаем текущее время в UTC
    utc_now = datetime.datetime.now(timezone.utc)
    # +3 часа для мск
    moscow_now = utc_now.astimezone(MOSCOW_TIMEZONE)
    return moscow_now

# МИНИМАЛЬНОЕ и МАКСИМАЛЬНОЕ время в часах
BOSSES_CONFIG = {
    1: {
        'id': 1,
        'name': 'Мистический дух',
        'min_respawn': 4,  # минимальное
        'max_respawn': 5,  # максимальное
        'icon': '👻',
        'description': 'Респавн: 4-5 часов'
    },
    2: {
        'id': 2,
        'name': 'Петушара',
        'min_respawn': 1,  # минимальное
        'max_respawn': 2,  # максимальное
        'icon': '🐓',
        'description': 'Респавн: 1-2 часа'
    },
    3: {
        'id': 3,
        'name': 'Тайфун',
        'min_respawn': 12,  # минимальное
        'max_respawn': 20,  # максимальное
        'icon': '🌪',
        'description': 'Респавн: 12-20 часа'
    },
    4: {
        'id': 4,
        'name': 'Гордон',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '👹',
        'description': 'Респавн: 12-16 часа'
    },
    5: {
        'id': 5,
        'name': 'Лилит/Анаким',
        'min_respawn': 12,  # минимальное
        'max_respawn': 20,  # максимальное
        'icon': '',
        'description': 'Респавн: 12-20 часа'
    },
    6: {
        'id': 6,
        'name': 'Галаксия',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '🌌',
        'description': 'Респавн: 12-16 часа'
    },
    7: {
        'id': 7,
        'name': 'Шадит',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '🦉',
        'description': 'Респавн: 12-16 часа'
    },
    8: {
        'id': 8,
        'name': 'Шуриэль',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '👼🏿',
        'description': 'Респавн: 12-16 часа'
    },
    9: {
        'id': 9,
        'name': 'Анаис',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '🪽',
        'description': 'Респавн: 12-16 часа'
    },
    10: {
        'id': 10,
        'name': 'Шакс',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '🦪',
        'description': 'Респавн: 12-16 часа'
    },
    11: {
        'id': 11,
        'name': 'Гестия',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '🦋',
        'description': 'Респавн: 12-16 часа'
    },
    12: {
        'id': 12,
        'name': 'Палатанос',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '🪾',
        'description': 'Респавн: 12-16 часа'
    },
    13: {
        'id': 13,
        'name': 'Голем',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '🥫',
        'description': 'Респавн: 12-16 часа'
    },
    14: {
        'id': 14,
        'name': 'Голконда',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '🐂',
        'description': 'Респавн: 12-16 часа'
    },
    15: {
        'id': 15,
        'name': 'Шиид',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '🦂',
        'description': 'Респавн: 12-16 часа'
    },
    16: {
        'id': 16,
        'name': 'Глаки',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '🐢',
        'description': 'Респавн: 12-16 часа'
    },
    17: {
        'id': 17,
        'name': 'Ипос',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '🐎',
        'description': 'Респавн: 12-16 часа'
    },
    18: {
        'id': 18,
        'name': 'Хорус',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '🐻‍❄️',
        'description': 'Респавн: 12-16 часа'
    },
    19: {
        'id': 19,
        'name': 'Беква',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '🐙',
        'description': 'Респавн: 12-16 часа'
    },
    20: {
        'id': 20,
        'name': 'Кло',
        'min_respawn': 10,  # минимальное
        'max_respawn': 14,  # максимальное
        'icon': '🦑',
        'description': 'Респавн: 12-16 часа'
    },
    21: {
        'id': 21,
        'name': 'Эмбер',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '🦀',
        'description': 'Респавн: 12-16 часа'
    },
    22: {
        'id': 22,
        'name': 'Бракки',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '🐎',
        'description': 'Респавн: 12-16 часа'
    },
    23: {
        'id': 23,
        'name': 'Ашакиэль',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '🐏',
        'description': 'Респавн: 12-16 часа'
    },
    24: {
        'id': 24,
        'name': 'Нага',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '🀄️',
        'description': 'Респавн: 12-16 часа'
    },
    25: {
        'id': 25,
        'name': 'Декарбия',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '🦫',
        'description': 'Респавн: 12-16 часа'
    },
    26: {
        'id': 26,
        'name': 'Танатос',
        'min_respawn': 10,  # минимальное
        'max_respawn': 14,  # максимальное
        'icon': '🐎',
        'description': 'Респавн: 12-16 часа'
    },
    27: {
        'id': 27,
        'name': 'Налетчик',
        'min_respawn': 10,  # минимальное
        'max_respawn': 14,  # максимальное
        'icon': '🐦‍🔥',
        'description': 'Респавн: 12-16 часа'
    },
    28: {
        'id': 28,
        'name': 'Тайр',
        'min_respawn': 12,  # минимальное
        'max_respawn': 16,  # максимальное
        'icon': '🦔',
        'description': 'Респавн: 12-16 часа'
    }
}


def load_timers():
    """Загружаем таймеры из файла"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Конвертируем строки времени обратно в datetime с московской таймзоной
                for boss_id, kill_time in data.items():
                    if kill_time:
                        # Парсим время
                        dt = datetime.datetime.fromisoformat(kill_time)
                        # Если время уже имеет таймзону
                        if dt.tzinfo:
                            # Конвертируем в московское время
                            data[boss_id] = dt.astimezone(MOSCOW_TIMEZONE)
                        else:
                            # Время без таймзоны - интерпретируем как UTC и конвертируем в Москву
                            utc_time = dt.replace(tzinfo=timezone.utc)
                            data[boss_id] = utc_time.astimezone(MOSCOW_TIMEZONE)
                return data
        except Exception as e:
            print(f"Ошибка загрузки файла: {e}")
            return {}
    return {}


def save_timers(timers):
    """Сохраняем таймеры в файл"""
    # Конвертируем datetime в строки для сохранения
    timers_to_save = {}
    for boss_id, kill_time in timers.items():
        if kill_time:
            # Убедимся, что время в московской таймзоне
            if kill_time.tzinfo is None:
                kill_time = kill_time.replace(tzinfo=MOSCOW_TIMEZONE)
            else:
                kill_time = kill_time.astimezone(MOSCOW_TIMEZONE)
            timers_to_save[str(boss_id)] = kill_time.isoformat()
        else:
            timers_to_save[str(boss_id)] = None

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(timers_to_save, f, ensure_ascii=False, indent=2)


# Загружаем текущие таймеры
timers = load_timers()
# Храним время последнего нажатия для каждого босса (серверная блокировка)
last_kill_timestamps = {}


def load_history():
    """Загружаем историю действий"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
                # Конвертируем строки времени обратно в datetime
                for record in history:
                    if 'timestamp' in record and record['timestamp']:
                        dt = datetime.datetime.fromisoformat(record['timestamp'])
                        if dt.tzinfo:
                            record['timestamp'] = dt.astimezone(MOSCOW_TIMEZONE)
                        else:
                            record['timestamp'] = dt.replace(tzinfo=MOSCOW_TIMEZONE)
                        # Добавляем форматированные поля
                        record['timestamp_formatted'] = record['timestamp'].strftime('%d.%m.%Y %H:%M:%S')
                        record['time_only'] = record['timestamp'].strftime('%H:%M:%S')
                return history
        except Exception as e:
            print(f"Ошибка загрузки истории: {e}")
            return []
    return []


def save_history(history):
    """Сохраняем историю действий"""
    # Конвертируем datetime в строки для сохранения
    history_to_save = []
    for record in history:
        record_copy = record.copy()
        if 'timestamp' in record_copy and record_copy['timestamp']:
            if record_copy['timestamp'].tzinfo is None:
                record_copy['timestamp'] = record_copy['timestamp'].replace(tzinfo=MOSCOW_TIMEZONE)
            else:
                record_copy['timestamp'] = record_copy['timestamp'].astimezone(MOSCOW_TIMEZONE)
            record_copy['timestamp'] = record_copy['timestamp'].isoformat()
        history_to_save.append(record_copy)
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history_to_save, f, ensure_ascii=False, indent=2)


def add_to_history(action_type, boss_id, details=None):
    """Добавляем запись в историю"""
    history = load_history()
    
    record = {
        'id': len(history) + 1,
        'timestamp': get_moscow_time(),
        'action_type': action_type,  # 'kill', 'reset', 'manual_edit', 'undo'
        'boss_id': boss_id,
        'boss_name': BOSSES_CONFIG.get(boss_id, {}).get('name', f'Босс #{boss_id}'),
        'details': details or {}
    }
    
    history.append(record)
    # Ограничиваем историю последними 100 записями
    if len(history) > 100:
        history = history[-100:]
    
    save_history(history)
    return record


# Загружаем историю
history = load_history()


@app.route('/')
def index():
    """Главная страница сайта"""
    # Передаем текущее московское время в шаблон
    moscow_time = get_moscow_time().strftime('%H:%M:%S')
    return render_template('index.html', bosses=BOSSES_CONFIG, moscow_time=moscow_time)


@app.route('/get_boss_timers')
def get_boss_timers():
    """Получить ВСЕ таймеры боссов"""
    result = {}
    now = get_moscow_time()  # Используем московское время

    for boss_id, boss_info in BOSSES_CONFIG.items():
        last_kill_time = timers.get(str(boss_id))

        if not last_kill_time:
            # Босс еще не убивали
            result[boss_id] = {
                'name': boss_info['name'],
                'icon': boss_info['icon'],
                'status': 'Не убит',
                'time_left': '--:--:--',
                'respawn_range': f'{boss_info["min_respawn"]}-{boss_info["max_respawn"]}ч',
                'killed': False,
                'min_time': '--:--:--',
                'max_time': '--:--:--',
                'description': boss_info['description']
            }
        else:
            # Вычисляем минимальное и максимальное время появления
            min_respawn_time = last_kill_time + datetime.timedelta(hours=boss_info['min_respawn'])
            max_respawn_time = last_kill_time + datetime.timedelta(hours=boss_info['max_respawn'])

            # Сколько прошло с момента убийства
            time_since_kill = now - last_kill_time

            # Сколько времени до минимального респавна
            time_to_min = min_respawn_time - now
            time_to_max = max_respawn_time - now

            if time_to_max.total_seconds() <= 0:
                status = 'ПОЯВИЛСЯ!'
                time_left_str = '00:00:00'
                timer_label = 'Появился!'
                min_time_str = 'Прошло'
                max_time_str = 'Прошло'

            elif time_to_min.total_seconds() <= 0:

                status = 'В РЕСПАВНЕ'

                total_seconds = int(time_to_max.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                time_left_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                timer_label = 'До макс. респавна:'
                min_time_str = 'Прошло'
                max_time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            else:
                # Еще не прошло минимальное время
                status = 'ВОЗРОЖДАЕТСЯ'

                # Время до минимального респавна
                total_seconds_min = int(time_to_min.total_seconds())
                hours_min = total_seconds_min // 3600
                minutes_min = (total_seconds_min % 3600) // 60
                seconds_min = total_seconds_min % 60

                # Время до максимального респавна
                total_seconds_max = int(time_to_max.total_seconds())
                hours_max = total_seconds_max // 3600
                minutes_max = (total_seconds_max % 3600) // 60
                seconds_max = total_seconds_max % 60

                time_left_str = f"{hours_min:02d}:{minutes_min:02d}:{seconds_min:02d}"
                timer_label = 'До мин. респавна:'
                min_time_str = f"{hours_min:02d}:{minutes_min:02d}:{seconds_min:02d}"
                max_time_str = f"{hours_max:02d}:{minutes_max:02d}:{seconds_max:02d}"

            result[boss_id] = {
                'name': boss_info['name'],
                'icon': boss_info['icon'],
                'status': status,
                'time_left': time_left_str,
                'timer_label': timer_label,
                'respawn_range': f'{boss_info["min_respawn"]}-{boss_info["max_respawn"]}ч',
                'min_time': min_time_str,
                'max_time': max_time_str,
                'killed': True,
                'last_kill': last_kill_time.strftime('%H:%M:%S'),
                'min_respawn_time': min_respawn_time.strftime('%H:%M:%S'),
                'max_respawn_time': max_respawn_time.strftime('%H:%M:%S'),
                'description': boss_info['description'],
                'time_since_kill': str(time_since_kill).split('.')[0],  # Убираем микросекунды
                'moscow_time': now.strftime('%H:%M:%S')
            }

    return jsonify(result)


@app.route('/boss_killed/<int:boss_id>', methods=['POST'])
def boss_killed(boss_id):
    """Кто-то убил босса - обновляем для ВСЕХ с проверкой блокировки"""
    if boss_id not in BOSSES_CONFIG:
        return jsonify({'error': 'Босс не найден'}), 404

    # Проверяем серверную блокировку (5 минут)
    now = get_moscow_time()
    last_kill_time = last_kill_timestamps.get(boss_id)
    
    print(f"DEBUG: Проверка блокировки для босса {boss_id}")
    print(f"DEBUG: Текущее время: {now}")
    print(f"DEBUG: Последнее нажатие: {last_kill_time}")
    
    if last_kill_time:
        time_diff = now - last_kill_time
        print(f"DEBUG: Разница времени: {time_diff.total_seconds()} секунд")
        if time_diff.total_seconds() < 300:  # 5 минут = 300 секунд
            remaining_time = 300 - time_diff.total_seconds()
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            print(f"DEBUG: Босс заблокирован, осталось {minutes}:{seconds:02d}")
            return jsonify({
                'error': f'Босс заблокирован! Подожди еще {minutes}:{seconds:02d}'
            }), 429  # Too Many Requests
    else:
        print(f"DEBUG: Нет предыдущих нажатий для босса {boss_id}")

    # Обновляем время убийства на текущее МОСКОВСКОЕ время
    old_time = timers.get(str(boss_id))
    timers[str(boss_id)] = now
    
    # Сохраняем время последнего нажатия для блокировки
    last_kill_timestamps[boss_id] = now
    print(f"DEBUG: Сохранено время нажатия для босса {boss_id}: {now}")
    print(f"DEBUG: Текущее состояние last_kill_timestamps: {last_kill_timestamps}")

    # Сохраняем в файл
    save_timers(timers)

    # Добавляем в историю
    details = {
        'previous_time': old_time.isoformat() if old_time else None,
        'new_time': now.isoformat()
    }
    history_record = add_to_history('kill', boss_id, details)

    # Вычисляем времена респавна
    boss_info = BOSSES_CONFIG[boss_id]
    min_respawn_time = now + datetime.timedelta(hours=boss_info['min_respawn'])
    max_respawn_time = now + datetime.timedelta(hours=boss_info['max_respawn'])

    return jsonify({
        'success': True,
        'message': f'{boss_info["name"]} отмечен как убитый!',
        'kill_time': now.strftime('%H:%M:%S'),
        'boss_id': boss_id,
        'min_respawn_time': min_respawn_time.strftime('%H:%M:%S'),
        'max_respawn_time': max_respawn_time.strftime('%H:%M:%S'),
        'respawn_range': f'{boss_info["min_respawn"]}-{boss_info["max_respawn"]} часов',
        'history_id': history_record['id']
    })


@app.route('/reset_all', methods=['POST'])
def reset_all():
    """Сбросить ВСЕ таймеры (админская функция)"""
    global timers
    
    # Сохраняем старые значения для истории
    old_timers = timers.copy()
    
    timers = {}
    save_timers(timers)
    
    # Добавляем в историю
    details = {'old_timers': {k: v.isoformat() if v else None for k, v in old_timers.items()}}
    history_record = add_to_history('reset', 0, details)  # 0 = все боссы

    return jsonify({
        'success': True,
        'message': 'Все таймеры сброшены!',
        'history_id': history_record['id']
    })


@app.route('/get_moscow_time')
def get_moscow_time_api():
    """API для получения московского времени"""
    now = get_moscow_time()
    return jsonify({
        'moscow_time': now.strftime('%H:%M:%S'),
        'full_time': now.isoformat(),
        'date': now.strftime('%d.%m.%Y')
    })


@app.route('/get_history')
def get_history():
    """Получить историю действий"""
    history = load_history()
    
    # Форматируем для фронтенда
    formatted_history = []
    for record in reversed(history[-20:]):  # Последние 20 действий
        formatted_record = record.copy()
        if 'timestamp' in formatted_record:
            formatted_record['timestamp_formatted'] = formatted_record['timestamp'].strftime('%d.%m.%Y %H:%M:%S')
            formatted_record['time_only'] = formatted_record['timestamp'].strftime('%H:%M:%S')
        formatted_history.append(formatted_record)
    
    return jsonify(formatted_history)


@app.route('/manual_edit_time/<int:boss_id>', methods=['POST'])
def manual_edit_time(boss_id):
    """Ручное редактирование времени убийства"""
    if boss_id not in BOSSES_CONFIG:
        return jsonify({'error': 'Босс не найден'}), 404
    
    data = request.get_json()
    if not data or 'time' not in data:
        return jsonify({'error': 'Не указано время'}), 400
    
    try:
        # Парсим время из строки
        time_str = data['time']
        # Ожидаем формат HH:MM или HH:MM:SS
        time_parts = time_str.split(':')
        if len(time_parts) == 2:
            time_parts.append('00')  # Добавляем секунды если их нет
        
        hour, minute, second = map(int, time_parts)
        
        # Получаем сегодняшнюю дату
        today = get_moscow_time().date()
        new_time = datetime.datetime(
            year=today.year,
            month=today.month,
            day=today.day,
            hour=hour,
            minute=minute,
            second=second,
            tzinfo=MOSCOW_TIMEZONE
        )
        
        # Проверяем, что время не в будущем
        now = get_moscow_time()
        if new_time > now:
            return jsonify({'error': 'Время не может быть в будущем'}), 400
        
        # Сохраняем старое значение
        old_time = timers.get(str(boss_id))
        
        # Обновляем время
        timers[str(boss_id)] = new_time
        save_timers(timers)
        
        # Добавляем в историю
        details = {
            'previous_time': old_time.isoformat() if old_time else None,
            'new_time': new_time.isoformat(),
            'edited_manually': True
        }
        history_record = add_to_history('manual_edit', boss_id, details)
        
        # Вычисляем времена респавна
        boss_info = BOSSES_CONFIG[boss_id]
        min_respawn_time = new_time + datetime.timedelta(hours=boss_info['min_respawn'])
        max_respawn_time = new_time + datetime.timedelta(hours=boss_info['max_respawn'])
        
        return jsonify({
            'success': True,
            'message': f'Время убийства {boss_info["name"]} обновлено!',
            'new_time': new_time.strftime('%H:%M:%S'),
            'min_respawn_time': min_respawn_time.strftime('%H:%M:%S'),
            'max_respawn_time': max_respawn_time.strftime('%H:%M:%S'),
            'history_id': history_record['id']
        })
        
    except ValueError as e:
        return jsonify({'error': f'Неверный формат времени: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Ошибка: {str(e)}'}), 500


@app.route('/reset_boss_timer/<int:boss_id>', methods=['POST'])
def reset_boss_timer(boss_id):
    """Сбросить таймер конкретного босса"""
    if str(boss_id) in timers:
        # Сохраняем старое значение для истории
        old_time = timers[str(boss_id)]
        
        # Удаляем таймер
        del timers[str(boss_id)]
        save_timers(timers)
        
        # Добавляем в историю
        details = {'old_time': old_time.isoformat() if old_time else None}
        add_to_history('auto_reset', boss_id, details)
        
        boss_name = BOSSES_CONFIG.get(boss_id, {}).get('name', f'Босс #{boss_id}')
        
        return jsonify({
            'success': True,
            'message': f'Таймер {boss_name} автоматически сброшен',
            'boss_id': boss_id
        })
    
    return jsonify({'error': 'Босс не найден или таймер уже сброшен'}), 404


@app.route('/clear_history', methods=['POST'])
def clear_history():
    """Очистить всю историю действий"""
    global history
    
    history_count = len(history)
    history = []
    save_history(history)
    
    return jsonify({
        'success': True,
        'message': f'История очищена ({history_count} записей удалено)!',
        'cleared_count': history_count
    })


@app.route('/undo_last_action', methods=['POST'])
def undo_last_action():
    """Откатить последнее действие"""
    history_list = load_history()
    
    if not history_list:
        return jsonify({'error': 'История пуста'}), 400
    
    # Получаем последнюю запись
    last_action = history_list[-1]
    action_type = last_action['action_type']
    boss_id = last_action['boss_id']
    details = last_action.get('details', {})
    
    # Откатываем действие
    if action_type == 'kill' or action_type == 'manual_edit':
        # Возвращаем предыдущее время или удаляем запись
        previous_time = details.get('previous_time')
        if previous_time:
            # Восстанавливаем предыдущее время
            prev_dt = datetime.datetime.fromisoformat(previous_time)
            if prev_dt.tzinfo:
                prev_dt = prev_dt.astimezone(MOSCOW_TIMEZONE)
            else:
                prev_dt = prev_dt.replace(tzinfo=MOSCOW_TIMEZONE)
            timers[str(boss_id)] = prev_dt
        else:
            # Удаляем запись (был первый kill)
            timers.pop(str(boss_id), None)
        
        save_timers(timers)
        
    elif action_type == 'reset':
        # Восстанавливаем все таймеры
        old_timers = details.get('old_timers', {})
        for bid, time_str in old_timers.items():
            if time_str:
                dt = datetime.datetime.fromisoformat(time_str)
                if dt.tzinfo:
                    dt = dt.astimezone(MOSCOW_TIMEZONE)
                else:
                    dt = dt.replace(tzinfo=MOSCOW_TIMEZONE)
                timers[bid] = dt
            else:
                timers.pop(bid, None)
        save_timers(timers)
    
    # Добавляем запись об откате
    undo_details = {
        'undone_action_id': last_action['id'],
        'undone_action_type': action_type,
        'boss_name': last_action['boss_name']
    }
    add_to_history('undo', boss_id, undo_details)
    
    # Удаляем откаченное действие из истории
    history_list.pop()
    save_history(history_list)
    
    return jsonify({
        'success': True,
        'message': f'Действие "{action_type}" для {last_action["boss_name"]} отменено!',
        'undone_action': last_action
    })


@app.route('/health')
def health():
    now = get_moscow_time()
    return jsonify({
        'status': 'ok',
        'bosses_count': len(BOSSES_CONFIG),
        'timers_count': len(timers),
        'history_count': len(load_history()),
        'moscow_time': now.strftime('%H:%M:%S'),
        'timezone': 'Moscow (UTC+3)'
    })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)