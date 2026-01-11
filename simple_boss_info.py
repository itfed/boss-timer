import requests
import json
from datetime import datetime
import pytz

def get_simple_boss_info(site_url="http://localhost:5111"):
    """
    Простой скрипт для получения информации о респе боссов
    
    Args:
        site_url (str): URL твоего сайта с таймерами
    
    Returns:
        dict: Упрощенная информация о боссах
    """
    try:
        # Получаем таймеры боссов
        response = requests.get(f"{site_url}/get_boss_timers")
        response.raise_for_status()
        data = response.json()
        
        print("ТАЙМЕРЫ БОССОВ:")
        print("-" * 50)
        
        # Сортируем по ID босса
        sorted_bosses = sorted(data.items(), key=lambda x: int(x[0]))
        
        for boss_id, boss_info in sorted_bosses:
            name = boss_info['name']
            icon = boss_info['icon']
            status = boss_info['status']
            time_left = boss_info['time_left']
            
            if boss_info['killed']:
                # Босс убит, показываем таймер
                print(f"{int(boss_id):2d}. {name} {icon} - {status}: {time_left}")
            else:
                # Босс не убит
                print(f"{int(boss_id):2d}. {name} {icon} - {status}")
        
        print(f"\nОбновлено: {datetime.now(pytz.timezone('Europe/Moscow')).strftime('%H:%M:%S')} (МСК)")
        
        return data
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

def get_boss_by_name(name_query, site_url="http://localhost:5111"):
    """
    Поиск босса по имени
    
    Args:
        name_query (str): Часть имени босса для поиска
        site_url (str): URL твоего сайта с таймерами
    """
    try:
        response = requests.get(f"{site_url}/get_boss_timers")
        response.raise_for_status()
        data = response.json()
        
        found_bosses = []
        name_query = name_query.lower()
        
        for boss_id, boss_info in data.items():
            if name_query in boss_info['name'].lower():
                found_bosses.append((boss_id, boss_info))
        
        if found_bosses:
            print(f"\nНайдено боссов по запросу '{name_query}':")
            for boss_id, boss_info in found_bosses:
                status = boss_info['status']
                time_left = boss_info['time_left']
                if boss_info['killed']:
                    print(f"  #{boss_id}: {boss_info['name']} {boss_info['icon']} - {status}: {time_left}")
                else:
                    print(f"  #{boss_id}: {boss_info['name']} {boss_info['icon']} - {status}")
        else:
            print(f"Босс с именем, содержащим '{name_query}', не найден")
        
    except Exception as e:
        print(f"Ошибка при поиске: {e}")

if __name__ == "__main__":
    site_url = "http://localhost:5111"  # Замени на URL твоего сайта
    
    print("Получение информации о боссах...")
    print(f"Сайт: {site_url}")
    print()
    
    # Получаем упрощенную информацию
    get_simple_boss_info(site_url)
    
    # Пример поиска конкретного босса
    # get_boss_by_name("дух", site_url)
    # get_boss_by_name("тайфун", site_url)