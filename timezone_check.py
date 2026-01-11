"""
Утилита для проверки разницы во времени между вашим местоположением и Москвой
"""
import datetime
import pytz

def check_timezone_difference():
    """Проверяет разницу во времени между вашим местоположением и Москвой"""
    # Московская таймзона
    moscow_tz = pytz.timezone('Europe/Moscow')
    moscow_time = datetime.datetime.now(moscow_tz)
    
    # Ваше локальное время
    local_time = datetime.datetime.now()
    
    # Получаем смещение в часах
    local_tz_offset = local_time.astimezone().utcoffset().total_seconds() / 3600
    moscow_tz_offset = 3  # Москва всегда UTC+3
    time_diff = local_tz_offset - moscow_tz_offset
    
    print("ИНФОРМАЦИЯ О ЧАСОВЫХ ПОЯСАХ")
    print("=" * 40)
    print(f"Ваше локальное время: {local_time.strftime('%Y-%m-%d %H:%M:%S %Z %z')}")
    print(f"Московское время:     {moscow_time.strftime('%Y-%m-%d %H:%M:%S %Z %z')}")
    print(f"Разница времени:       {time_diff:+.1f} часов")
    print()
    
    # Проверяем разницу в датах
    local_date = local_time.date()
    moscow_date = moscow_time.date()
    
    if local_date != moscow_date:
        print(f"РАЗНИЦА В ДАТАХ!")
        print(f"Ваша дата:           {local_date}")
        print(f"Московская дата:     {moscow_date}")
        print(f"Разница в днях:      {(local_date - moscow_date).days} дней")
        print()
        print("Это может вызвать проблемы при синхронизации таймеров.")
        print("Рекомендуется использовать timezone_aware_sync.py для синхронизации.")
    else:
        print("Даты совпадают - проблем с синхронизацией по дате быть не должно.")
    
    print()
    print("Для синхронизации с учетом часовых поясов используйте:")
    print("python timezone_aware_sync.py sync [remote_url] [local_url]")

if __name__ == "__main__":
    check_timezone_difference()