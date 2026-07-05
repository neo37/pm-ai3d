# Институт Проектного Мышления — сайт (pm.ai3d.art)

Современный адаптивный сайт компании **Институт Проектного Мышления (ИПМ)** на
**Wagtail (Django CMS)**. Заменяет два старых сайта — `proekt-m.com` и `ipm.rf`.

## Ключевые особенности
- **3D-карта объектов** на MapLibre GL (стиль `openfreemap/liberty`, без токенов,
  с 3D-зданиями) и облётом камеры между проектами (`flyTo`).
- Портфолио объектов с координатами, категориями и галереями.
- 8 услуг (компетенций), страницы «О компании», «Контакты», «Документы».
- Адаптивная вёрстка (mobile-first), шрифт Inter.
- Весь контент редактируется через админку Wagtail (`/admin`).

## Стек
Python 3.12 · Django · Wagtail 7.4 · MapLibre GL 4.7 · WhiteNoise · Gunicorn

## Локальный запуск
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_site           # наполнение реальным контентом
python manage.py createsuperuser
python manage.py runserver
```
Сайт: http://127.0.0.1:8000 · Админка: http://127.0.0.1:8000/admin

## Продакшн (pm.ai3d.art)
```bash
export DJANGO_SECRET_KEY=...          # обязательно
export DJANGO_ALLOWED_HOSTS=pm.ai3d.art,www.pm.ai3d.art
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn astryx.wsgi:application --bind 0.0.0.0:8000
```
Настройки прод: `astryx/settings/production.py`.

## Структура
- `home/` — главная (герой с 3D-картой, показатели).
- `projects/` — портфолио: `ProjectPage` (lat/lng, категория, галерея),
  JSON для карты `/api/projects.json`, команда `seed_site`.
- `services/` — услуги/компетенции.
- `sitepages/` — «О компании», «Контакты», «Документы», «Политика».
- `astryx/static/js/map.js` — 3D-карта и облёт камеры.

## Изображения в HD
Скрипт `scripts/fetch_hd_images.py` догружает HD-версии изображений со старых
сайтов (в дампах остались только превью). Запускать на сервере с доступом в интернет.
