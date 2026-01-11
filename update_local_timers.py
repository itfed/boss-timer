import json
import requests
from datetime import datetime, time, timedelta
import pytz

def update_local_timers(exported_timers, local_url="http://localhost:5111"):
    """
    Обновляет локальные таймеры боссов на основе экспортированных данных
    
    Args:
        exported_timers (dict): Словарь с временами убийства боссов в формате {boss_id: "HH:MM:SS" или None}
        local_url (str): URL локального сайта с таймерами
    
    Returns:
        bool: Успешность обновления
    """
    try:
        print("ОБНОВЛЕНИЕ ЛОКАЛЬНЫХ ТАЙМЕРОВ")
        print("=" * 50)
        
        # Получаем текущие таймеры с локального сайта для проверки
        try:
            current_response = requests.get(f"{local_url}/get_boss_timers", timeout=10)
            current_data = current_response.json()
            print(f"✅ Подключен к локальному сайту: {local_url}")
            print(f"✅ Найдено {len(current_data)} боссов")
        except Exception as e:
            print(f"❌ Ошибка подключения к локальному сайту: {e}")
            return False
        
        # Московская таймзона
        moscow_tz = pytz.timezone('Europe/Moscow')
        moscow_now = datetime.now(moscow_tz)
        
        # Определяем разницу между вашим местным временем и московским
        # Предполагаем, что текущая машина использует ваше локальное время (Sakhalin, UTC+11)
        local_now = datetime.now()  # Это ваше локальное время
        local_tz_offset = local_now.astimezone().utcoffset().total_seconds() / 3600  # Часовой пояс в часах
        moscow_tz_offset = 3  # Московский часовой пояс (UTC+3)
        time_diff_hours = local_tz_offset - moscow_tz_offset  # Разница во времени
        
        print(f"Ваше локальное время: {local_now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Московское время: {moscow_now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Разница времени: {time_diff_hours:+.1f} часов")
        
        updated_count = 0
        skipped_count = 0
        
        print("\nПРОЦЕСС ОБНОВЛЕНИЯ:")
        
        for boss_id_str, kill_time in exported_timers.items():
            boss_id = int(boss_id_str)
            
            if kill_time is None:
                # Босс не убит, пропускаем
                current_boss_info = current_data.get(str(boss_id), {})
                current_name = current_boss_info.get('name', f'Босс #{boss_id}')
                print(f"  Пропущен #{boss_id:2d}: {current_name} (не убит)")
                skipped_count += 1
                continue
            
            # Парсим время убийства
            try:
                time_parts = kill_time.split(':')
                hour, minute, second = map(int, time_parts)
                
                # Создаем сегодняшнюю дату с указанным временем в московской таймзоне
                today = moscow_now.date()
                naive_datetime = datetime.combine(today, time(hour, minute, second))
                
                # Локализуем в московскую таймзону
                moscow_kill_time = moscow_tz.localize(naive_datetime)
                
                # Корректируем дату если время в будущем относительно текущего московского времени
                # Это важно при разнице во времени между регионами
                if moscow_kill_time > moscow_now:
                    # Если время убийства в будущем, значит оно было вчера по московскому времени
                    moscow_kill_time = moscow_kill_time - timedelta(days=1)
                
                # Преобразуем в строку для отправки (берем только время, как ожидается)
                time_str = moscow_kill_time.strftime('%H:%M')
                
            except Exception as e:
                print(f"  Ошибка парсинга времени для босса #{boss_id}: {e}")
                continue
            
            # Отправляем запрос на ручное редактирование времени
            try:
                response = requests.post(
                    f"{local_url}/manual_edit_time/{boss_id}",
                    json={'time': time_str},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        current_boss_info = current_data.get(str(boss_id), {})
                        current_name = current_boss_info.get('name', f'Босс #{boss_id}')
                        print(f"  ✅ Обновлен #{boss_id:2d}: {current_name} - {kill_time} -> {time_str}")
                        updated_count += 1
                    else:
                        print(f"  ❌ Ошибка обновления #{boss_id}: {result.get('error', 'Неизвестная ошибка')}")
                else:
                    print(f"  ❌ Ошибка HTTP {response.status_code} для босса #{boss_id}")
                    
            except Exception as e:
                print(f"  ❌ Ошибка запроса для босса #{boss_id}: {e}")
        
        print(f"\nРЕЗУЛЬТАТ:")
        print(f"  Обновлено: {updated_count} боссов")
        print(f"  Пропущено: {skipped_count} боссов")
        print(f"  Всего обработано: {updated_count + skipped_count} боссов")
        
        print(f"\n✅ Обновление локальных таймеров завершено!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении локальных таймеров: {e}")
        return False

def update_local_timers_from_file(filename, local_url="http://localhost:5111"):
    """
    Обновляет локальные таймеры из файла экспорта
    
    Args:
        filename (str): Имя файла с экспортированными таймерами
        local_url (str): URL локального сайта с таймерами
    
    Returns:
        bool: Успешность обновления
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            exported_timers = json.load(f)
        
        print(f"Загружены таймеры из файла: {filename}")
        return update_local_timers(exported_timers, local_url)
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке таймеров из файла {filename}: {e}")
        return False

def update_single_boss(boss_id, kill_time, local_url="http://localhost:5111"):
    """
    Обновляет время убийства одного босса
    
    Args:
        boss_id (int): ID босса
        kill_time (str): Время убийства в формате "HH:MM" или "HH:MM:SS"
        local_url (str): URL локального сайта с таймерами
    
    Returns:
        bool: Успешность обновления
    """
    try:
        # Отправляем запрос на ручное редактирование времени
        response = requests.post(
            f"{local_url}/manual_edit_time/{boss_id}",
            json={'time': kill_time},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Босс #{boss_id} обновлен: {kill_time}")
                return True
            else:
                print(f"❌ Ошибка обновления босса #{boss_id}: {result.get('error', 'Неизвестная ошибка')}")
                return False
        else:
            print(f"❌ Ошибка HTTP {response.status_code} для босса #{boss_id}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка запроса для босса #{boss_id}: {e}")
        return False

if __name__ == "__main__":
    local_url = "http://localhost:5111"  # Замени на URL твоего локального сайта
    
    print("Обновление локальных таймеров...")
    print(f"Локальный сайт: {local_url}")
    print()
    
    # Пример использования:
    # 1. Обновить из файла
    # update_local_timers_from_file("exported_timers_20260112_020632.json", local_url)
    
    # 2. Или использовать встроенные данные (например, скопированные из export_timers.py)
    # exported_data = {
    #     "1": "16:35:00",
    #     "2": "17:25:26",
    #     "3": "13:35:39",
    #     # ... остальные данные
    # }
    # update_local_timers(exported_data, local_url)
    
    print("Для использования:")
    print("1. Запусти export_timers.py для получения данных с сайта")
    print("2. Затем запусти этот скрипт с указанием файла экспорта")
    print("   python update_local_timers.py")