"""
Скрипт для синхронизации таймеров с учетом часовых поясов
"""
import requests
import json
from datetime import datetime, timedelta
import pytz

def get_moscow_time():
    """Получить текущее московское время"""
    moscow_tz = pytz.timezone('Europe/Moscow')
    return datetime.now(moscow_tz)

def get_local_time():
    """Получить текущее локальное время"""
    return datetime.now()

def sync_timers_with_timezone_handling(site_url="http://localhost:5111", local_url="http://localhost:5111"):
    """
    Синхронизирует таймеры с учетом часовых поясов
    """
    try:
        print("СИНХРОНИЗАЦИЯ ТАЙМЕРОВ С УЧЕТОМ ЧАСОВЫХ ПОЯСОВ")
        print("=" * 60)
        
        # Получаем информацию о таймерах с сайта
        response = requests.get(f"{site_url}/get_boss_timers")
        response.raise_for_status()
        remote_data = response.json()
        
        # Получаем текущие таймеры с локального сайта
        current_response = requests.get(f"{local_url}/get_boss_timers", timeout=10)
        current_response.raise_for_status()
        local_data = current_response.json()
        
        print(f"✅ Подключен к удаленному сайту: {site_url}")
        print(f"✅ Подключен к локальному сайту: {local_url}")
        print(f"✅ Найдено {len(remote_data)} боссов")
        
        # Получаем времена
        moscow_time = get_moscow_time()
        local_time = get_local_time()
        
        # Определяем разницу между временем
        moscow_tz_offset = 3  # UTC+3 для Москвы
        local_tz_offset = local_time.astimezone().utcoffset().total_seconds() / 3600
        time_diff = local_tz_offset - moscow_tz_offset
        
        print(f"Московское время: {moscow_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Локальное время: {local_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Разница времени: {time_diff:+.1f} часов")
        
        updated_count = 0
        skipped_count = 0
        
        print("\nПРОЦЕСС СИНХРОНИЗАЦИИ:")
        
        for boss_id_str, boss_info in remote_data.items():
            boss_id = int(boss_id_str)
            
            if not boss_info.get('killed'):
                # Босс не убит, пропускаем
                current_boss_info = local_data.get(str(boss_id), {})
                current_name = current_boss_info.get('name', f'Босс #{boss_id}')
                print(f"  Пропущен #{boss_id:2d}: {current_name} (не убит)")
                skipped_count += 1
                continue
            
            # Получаем информацию о времени убийства
            remote_kill_time_str = boss_info.get('last_kill')
            if not remote_kill_time_str:
                skipped_count += 1
                continue
            
            # Разбираем время
            time_parts = remote_kill_time_str.split(':')
            hour, minute, second = map(int, time_parts)
            
            # Создаем datetime объект с использованием даты из московского времени
            # Но учитываем, что дата может отличаться из-за часового пояса
            moscow_kill_date = moscow_time.date()
            naive_kill_datetime = datetime.combine(moscow_kill_date, datetime.min.time().replace(hour=hour, minute=minute, second=second))
            
            # Локализуем в московскую таймзону
            moscow_kill_time = pytz.timezone('Europe/Moscow').localize(naive_kill_datetime)
            
            # Если время убийства в будущем по сравнению с текущим московским временем,
            # значит оно было вчера
            if moscow_kill_time > moscow_time:
                moscow_kill_time = moscow_kill_time - timedelta(days=1)
            
            # Конвертируем в строку времени для отправки
            time_str = moscow_kill_time.strftime('%H:%M')
            
            # Обновляем локальный таймер
            try:
                response = requests.post(
                    f"{local_url}/manual_edit_time/{boss_id}",
                    json={'time': time_str},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        current_boss_info = local_data.get(str(boss_id), {})
                        current_name = current_boss_info.get('name', f'Босс #{boss_id}')
                        print(f"  ✅ Синхронизирован #{boss_id:2d}: {current_name} - {remote_kill_time_str} -> {time_str}")
                        updated_count += 1
                    else:
                        print(f"  ❌ Ошибка синхронизации #{boss_id}: {result.get('error', 'Неизвестная ошибка')}")
                else:
                    print(f"  ❌ Ошибка HTTP {response.status_code} для босса #{boss_id}")
                    
            except Exception as e:
                print(f"  ❌ Ошибка запроса для босса #{boss_id}: {e}")
        
        print(f"\nРЕЗУЛЬТАТ СИНХРОНИЗАЦИИ:")
        print(f"  Синхронизировано: {updated_count} боссов")
        print(f"  Пропущено: {skipped_count} боссов")
        print(f"  Всего обработано: {updated_count + skipped_count} боссов")
        
        print(f"\n✅ Синхронизация таймеров завершена!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при синхронизации таймеров: {e}")
        return False

def get_detailed_boss_info(site_url="http://localhost:5111"):
    """
    Получить подробную информацию о таймерах боссов
    """
    try:
        response = requests.get(f"{site_url}/get_boss_timers")
        response.raise_for_status()
        data = response.json()
        
        print("ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О БОССАХ:")
        print("-" * 80)
        
        # Сортируем по ID босса
        sorted_bosses = sorted(data.items(), key=lambda x: int(x[0]))
        
        for boss_id, boss_info in sorted_bosses:
            name = boss_info['name']
            icon = boss_info['icon']
            status = boss_info['status']
            time_left = boss_info['time_left']
            
            print(f"Босс #{boss_id}: {name} {icon}")
            print(f"  Статус: {status}")
            print(f"  Время до респа: {time_left}")
            print(f"  Убит: {'Да' if boss_info.get('killed') else 'Нет'}")
            
            if boss_info.get('killed'):
                print(f"  Время убийства: {boss_info.get('last_kill', 'N/A')}")
                print(f"  Мин. респавн: {boss_info.get('min_respawn_time', 'N/A')}")
                print(f"  Макс. респавн: {boss_info.get('max_respawn_time', 'N/A')}")
            
            print()
        
        # Показываем московское время
        try:
            health_response = requests.get(f"{site_url}/health")
            health_response.raise_for_status()
            health_data = health_response.json()
            print(f"Московское время: {health_data.get('moscow_time', 'N/A')} (МСК)")
        except:
            print(f"Московское время: N/A")
        
        return data
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

if __name__ == "__main__":
    import sys
    
    print("Инструмент синхронизации таймеров с учетом часовых поясов")
    print()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "sync":
            # Синхронизация
            remote_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:5111"
            local_url = sys.argv[3] if len(sys.argv) > 3 else "http://localhost:5111"
            
            print(f"Синхронизация с {remote_url} -> {local_url}")
            sync_timers_with_timezone_handling(remote_url, local_url)
        elif sys.argv[1] == "info":
            # Информация
            url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:5111"
            print(f"Получение информации с {url}")
            get_detailed_boss_info(url)
        else:
            print("Использование:")
            print("  python timezone_aware_sync.py sync [remote_url] [local_url] - Синхронизировать таймеры")
            print("  python timezone_aware_sync.py info [url] - Получить информацию о боссах")
    else:
        print("Выберите действие:")
        print("  python timezone_aware_sync.py sync - Синхронизировать с localhost")
        print("  python timezone_aware_sync.py info - Показать информацию")