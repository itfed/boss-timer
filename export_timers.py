import requests
import json
from datetime import datetime
import pytz

def export_timers(site_url="http://localhost:5111"):
    """
    Экспортирует время убийства боссов с сайта в формате, подходящем для импорта
    
    Args:
        site_url (str): URL твоего сайта с таймерами
    
    Returns:
        dict: Словарь с временами убийства боссов
    """
    try:
        # Получаем таймеры боссов
        response = requests.get(f"{site_url}/get_boss_timers")
        response.raise_for_status()
        data = response.json()
        
        # Создаем словарь с временами убийства
        exported_timers = {}
        
        print("ЭКСПОРТ ВРЕМЕН УБИЙСТВА БОССОВ")
        print("=" * 50)
        
        # Сортируем по ID босса
        sorted_bosses = sorted(data.items(), key=lambda x: int(x[0]))
        
        for boss_id, boss_info in sorted_bosses:
            boss_id = int(boss_id)  # Преобразуем в int для совместимости
            name = boss_info['name']
            killed = boss_info['killed']
            
            if killed:
                # Если босс убит, сохраняем время убийства
                last_kill_time = boss_info['last_kill']
                exported_timers[boss_id] = last_kill_time
                
                print(f"Босс #{boss_id:2d}: {name} - Убит в {last_kill_time}")
            else:
                # Если босс не убит, сохраняем None
                exported_timers[boss_id] = None
                print(f"Босс #{boss_id:2d}: {name} - Не убит")
        
        print(f"\nВсего боссов: {len(exported_timers)}")
        print(f"Убито боссов: {sum(1 for v in exported_timers.values() if v is not None)}")
        
        # Сохраняем в файл
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exported_timers_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(exported_timers, f, ensure_ascii=False, indent=2)
        
        print(f"\nДанные экспортированы в файл: {filename}")
        
        # Также выводим в формате, удобном для копирования
        print("\nДАННЫЕ ДЛЯ ИМПОРТА (скопируй для update_local_timers):")
        print("-" * 50)
        print(json.dumps(exported_timers, ensure_ascii=False, indent=2))
        
        return exported_timers
        
    except Exception as e:
        print(f"Ошибка при экспорте таймеров: {e}")
        return None

def load_exported_timers_from_file(filename):
    """
    Загружает экспортированные таймеры из файла
    
    Args:
        filename (str): Имя файла с экспортированными таймерами
    
    Returns:
        dict: Словарь с временами убийства боссов
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Ошибка при загрузке таймеров из файла {filename}: {e}")
        return None

if __name__ == "__main__":
    site_url = "http://localhost:5111"  # Замени на URL твоего сайта
    
    print("Экспорт времени убийства боссов...")
    print(f"Сайт: {site_url}")
    print()
    
    exported_data = export_timers(site_url)
    
    if exported_data:
        print(f"\nЭкспорт завершен успешно!")
        print(f"Для импорта на локальный сайт используй update_local_timers.py")