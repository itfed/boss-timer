#!/usr/bin/env python3
"""
Скрипт для обновления локальных таймеров из экспортированных данных
"""

import json
import os
from datetime import datetime

def update_local_timers(export_file):
    """
    Обновляет локальный файл boss_timers.json данными из экспорта
    
    Args:
        export_file (str): Путь к файлу экспорта
    """
    
    try:
        print(f"📂 Читаю файл экспорта: {export_file}")
        
        # Читаем экспортированные данные
        with open(export_file, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
        
        # Извлекаем таймеры боссов
        boss_timers = export_data.get('boss_timers', {})
        
        print(f"📊 Найдено таймеров: {len(boss_timers)}")
        
        # Преобразуем данные в формат boss_timers.json
        # Нужны только даты последних убийств
        local_timers = {}
        
        for boss_id, boss_info in boss_timers.items():
            if boss_info.get('killed', False) and 'last_kill' in boss_info:
                # Получаем время последнего убийства
                last_kill_time = boss_info['last_kill']  # формат: "HH:MM:SS"
                
                # Создаем полную дату (сегодняшняя дата + время)
                today = datetime.now().strftime("%Y-%m-%d")
                full_datetime = f"{today}T{last_kill_time}+03:00"
                
                local_timers[str(boss_id)] = full_datetime
                
                boss_name = boss_info.get('name', f'Босс #{boss_id}')
                print(f"  ✅ {boss_name}: {last_kill_time}")
        
        # Сохраняем в локальный файл
        local_file = 'boss_timers.json'
        
        print(f"\n💾 Сохраняю в файл: {local_file}")
        
        with open(local_file, 'w', encoding='utf-8') as f:
            json.dump(local_timers, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Локальные таймеры обновлены!")
        print(f"Обновлено {len(local_timers)} таймеров")
        
        # Показываем результат
        print("\n📋 Текущие таймеры:")
        for boss_id, time_str in local_timers.items():
            print(f"  Босс #{boss_id}: {time_str}")
            
        return True
        
    except FileNotFoundError:
        print(f"❌ Файл {export_file} не найден")
        return False
    except json.JSONDecodeError:
        print(f"❌ Ошибка чтения JSON файла")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def find_latest_export():
    """Находит самый свежий файл экспорта"""
    import glob
    
    export_files = glob.glob('boss_timers_export_*.json')
    if not export_files:
        return None
    
    # Сортируем по имени файла (дата в имени)
    export_files.sort(reverse=True)
    return export_files[0]

def main():
    print("=== Обновление локальных таймеров ===\n")
    
    # Ищем последний файл экспорта
    export_file = find_latest_export()
    
    if not export_file:
        print("❌ Не найдено файлов экспорта")
        print("Сначала запусти export_timers.py")
        return
    
    print(f"Найден файл: {export_file}")
    
    # Обновляем таймеры
    success = update_local_timers(export_file)
    
    if success:
        print(f"\n🎉 Готово! Локальные таймеры обновлены из {export_file}")
        print("\nТеперь можно:")
        print("1. Проверить изменения локально")
        print("2. Закоммитить изменения в Git")
        print("3. Запушить на GitHub для деплоя")

if __name__ == "__main__":
    main()