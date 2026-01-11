import requests
import json
from datetime import datetime
import pytz

def get_boss_respawn_info(site_url="http://localhost:5111"):
    """
    Получает информацию о респе боссов с сайта
    
    Args:
        site_url (str): URL твоего сайта с таймерами
    
    Returns:
        dict: Информация о всех боссах и их таймерах
    """
    try:
        # Получаем таймеры боссов
        response = requests.get(f"{site_url}/get_boss_timers")
        response.raise_for_status()
        data = response.json()
        
        print("=" * 80)
        print("ИНФОРМАЦИЯ О РЕСПАВНЕ БОССОВ")
        print("=" * 80)
        
        # Сортируем по ID босса для последовательного вывода
        sorted_bosses = sorted(data.items(), key=lambda x: int(x[0]))
        
        for boss_id, boss_info in sorted_bosses:
            print(f"\nБосс #{boss_id}: {boss_info['name']} {boss_info['icon']}")
            print(f"  Статус: {boss_info['status']}")
            print(f"  Время до респа: {boss_info['time_left']}")
            print(f"  Таймер: {boss_info.get('timer_label', 'Нет данных')}")
            print(f"  Диапазон респа: {boss_info['respawn_range']}")
            print(f"  Мин. время: {boss_info['min_time']}")
            print(f"  Макс. время: {boss_info['max_time']}")
            
            if boss_info['killed']:
                print(f"  Последнее убийство: {boss_info['last_kill']}")
                print(f"  Мин. респавн: {boss_info['min_respawn_time']}")
                print(f"  Макс. респавн: {boss_info['max_respawn_time']}")
        
        print("\n" + "=" * 80)
        print(f"Обновлено: {datetime.now(pytz.timezone('Europe/Moscow')).strftime('%d.%m.%Y %H:%M:%S')} (МСК)")
        print("=" * 80)
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к сайту: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Ошибка при разборе JSON: {e}")
        return None
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return None

def get_specific_boss_info(boss_id, site_url="http://localhost:5111"):
    """
    Получает информацию о конкретном боссе
    
    Args:
        boss_id (int): ID босса
        site_url (str): URL твоего сайта с таймерами
    
    Returns:
        dict: Информация о конкретном боссе
    """
    try:
        response = requests.get(f"{site_url}/get_boss_timers")
        response.raise_for_status()
        data = response.json()
        
        if str(boss_id) in data:
            boss_info = data[str(boss_id)]
            print(f"\nДЕТАЛЬНАЯ ИНФОРМАЦИЯ О БОССЕ #{boss_id}")
            print("-" * 50)
            print(f"Имя: {boss_info['name']}")
            print(f"Иконка: {boss_info['icon']}")
            print(f"Статус: {boss_info['status']}")
            print(f"Время до респа: {boss_info['time_left']}")
            print(f"  Тип таймера: {boss_info.get('timer_label', 'Нет данных')}")
            print(f"Диапазон респа: {boss_info['respawn_range']}")
            print(f"Мин. время: {boss_info['min_time']}")
            print(f"Макс. время: {boss_info['max_time']}")
            print(f"Убит: {'Да' if boss_info['killed'] else 'Нет'}")
            
            if boss_info['killed']:
                print(f"Последнее убийство: {boss_info['last_kill']}")
                print(f"Мин. респавн: {boss_info['min_respawn_time']}")
                print(f"Макс. респавн: {boss_info['max_respawn_time']}")
                print(f"Прошло времени: {boss_info['time_since_kill']}")
            
            print(f"Текущее время (МСК): {boss_info['moscow_time']}")
            
            return boss_info
        else:
            print(f"Босс с ID {boss_id} не найден")
            return None
            
    except Exception as e:
        print(f"Ошибка при получении информации о боссе {boss_id}: {e}")
        return None

if __name__ == "__main__":
    # Пример использования
    site_url = "http://localhost:5111"  # Замени на URL твоего сайта
    
    print("Получение информации о респе боссов...")
    print(f"Сайт: {site_url}")
    
    # Получаем всю информацию
    all_bosses = get_boss_respawn_info(site_url)
    
    if all_bosses:
        print(f"\nНайдено {len(all_bosses)} боссов")
        
        # Пример: получить информацию о конкретном боссе (например, босс #1)
        # get_specific_boss_info(1, site_url)