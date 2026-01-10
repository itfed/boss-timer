# 📥 Как использовать экспорт таймеров

## Шаг 1: Установка зависимостей
```bash
pip install requests
```

## Шаг 2: Настройка скрипта
Открой файл `export_timers.py` и замени строку:
```python
SITE_URL = "https://your-site.onrender.com"  # ← ЗДЕСЬ ВСТАВЬ СВОЙ URL
```
на URL твоего сайта на Render.com, например:
```python
SITE_URL = "https://my-boss-timer.onrender.com"
```

## Шаг 3: Запуск экспорта
```bash
python export_timers.py
```

## Что делает скрипт:
1. Подключается к твоему сайту
2. Скачивает все таймеры боссов
3. Скачивает историю действий
4. Сохраняет всё в файл с именем типа: `boss_timers_export_2026-01-10_18-05-30.json`

## Результат:
- Получишь JSON файл с актуальными данными с сайта
- Файл содержит таймеры и историю действий
- Можно использовать для синхронизации с локальной версией

## Пример использования файла:
```python
import json

# Загрузить экспортированные данные
with open('boss_timers_export_2026-01-10_18-05-30.json', 'r') as f:
    data = json.load(f)

# Получить таймеры
boss_timers = data['boss_timers']

# Получить историю
history = data['actions_history']
```

## Полезные команды Git:
```bash
# Обновить локальные таймеры из экспорта
cp boss_timers_export_*.json boss_timers.json

# Закоммитить изменения
git add boss_timers.json
git commit -m "Update boss timers from site"
git push origin main
```