from flask import Flask, render_template, jsonify, request
import datetime
import json
import os
from datetime import timezone, timedelta

app = Flask(__name__)

# Хранение ВСЕХ данных
DATA_FILE = 'boss_timers.json'

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
                            # Предполагаем, что время уже в московском (UTC+3)
                            data[boss_id] = dt.replace(tzinfo=MOSCOW_TIMEZONE)
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
    """Кто-то убил босса - обновляем для ВСЕХ"""
    if boss_id not in BOSSES_CONFIG:
        return jsonify({'error': 'Босс не найден'}), 404

    # Обновляем время убийства на текущее МОСКОВСКОЕ время
    now = get_moscow_time()
    timers[str(boss_id)] = now

    # Сохраняем в файл
    save_timers(timers)

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
        'respawn_range': f'{boss_info["min_respawn"]}-{boss_info["max_respawn"]} часов'
    })


@app.route('/reset_all', methods=['POST'])
def reset_all():
    """Сбросить ВСЕ таймеры (админская функция)"""
    global timers
    timers = {}
    save_timers(timers)

    return jsonify({
        'success': True,
        'message': 'Все таймеры сброшены!'
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


@app.route('/health')
def health():
    now = get_moscow_time()
    return jsonify({
        'status': 'ok',
        'bosses_count': len(BOSSES_CONFIG),
        'timers_count': len(timers),
        'moscow_time': now.strftime('%H:%M:%S'),
        'timezone': 'Moscow (UTC+3)'
    })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)