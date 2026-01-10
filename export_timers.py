#!/usr/bin/env python3
"""
Скрипт для экспорта таймеров боссов с сайта Render.com
"""

import requests
import json
from datetime import datetime
import os

def export_boss_timers(site_url):
    """
    Экспортирует таймеры боссов с указанного сайта
    
    Args:
        site_url (str): https://boss-timer-ngl0.onrender.com
    """
    
    try:
        print(f"Подключаюсь к сайту: {site_url}")
        
        # Получаем данные таймеров
        response = requests.get(f"{site_url}/get_boss_timers", timeout=10)
        response.raise_for_status()  # Проверка на ошибки
        
        boss_data = response.json()
        print(f"Получено данных о {len(boss_data)} боссах")
        
        # Получаем историю действий
        history_response = requests.get(f"{site_url}/get_history", timeout=10)
        history_response.raise_for_status()
        history_data = history_response.json()
        print(f"Получено {len(history_data)} записей в истории")
        
        # Создаем имя файла с текущей датой
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"boss_timers_export_{timestamp}.json"
        
        # Сохраняем данные
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "site_url": site_url,
            "boss_timers": boss_data,
            "actions_history": history_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Данные успешно сохранены в файл: {filename}")
        print("\nСодержание:")
        print(f"- Боссов: {len(boss_data)}")
        print(f"- Записей в истории: {len(history_data)}")
        
        # Показываем краткую информацию о боссах
        print("\n📊 Статус боссов:")
        for boss_id, boss_info in boss_data.items():
            status = boss_info.get('status', 'Неизвестно')
            name = boss_info.get('name', f'Босс #{boss_id}')
            print(f"  {name}: {status}")
            
        return filename
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения: {e}")
        print("Проверь, что:")
        print("1. Сайт доступен")
        print("2. URL указан правильно")
        print("3. Есть интернет соединение")
        return None
        
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return None

def main():
    # URL твоего сайта на Render.com
    SITE_URL = "https://boss-timer-ngl0.onrender.com"
    
    print("=== Экспорт таймеров боссов ===")
    print(f"Целевой сайт: {SITE_URL}")
    print()
    
    filename = export_boss_timers(SITE_URL)
    
    if filename:
        print(f"\n📁 Файл сохранен: {os.path.abspath(filename)}")
        print("Теперь ты можешь использовать этот файл для синхронизации!")

if __name__ == "__main__":
    main()