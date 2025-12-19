Сделайте в репозитории файл project.md и вставьте туда разделы:

Назначение бота (для базы «Пеликан Алаколь»).

Архитектура: VPS + systemd, GitHub, сайт, JSON, без Docker.

Функции бота:

Сбор отзывов (опросник).

Навигация (геолокация + ссылки на карты).

FAQ/инфо о базе.

Модерация отзывов (pending → одобрение/отклонение → публикация на сайт).

Роли: пользователь, админ.

Как работает модерация: pending_reviews.json → уведомление админам → кнопки → GitManager → обновление reviews.json сайта.

Этот файл будет вашим «паспортом» проекта.

2. Набор файлов кода
В репозитории бота заведите такие файлы/модули:

bot/handlers/review.py — диалог сбора отзыва и сохранение в pending_reviews.json.

bot/handlers/navigation.py — команды/кнопки навигации, отправка локации и ссылок на карты.

bot/handlers/moderation.py — уведомления админам, кнопки ✅/❌, вызов GitManager, /pending, /stats.

bot/utils/git_manager.py — git pull, обновление site-repo/json/reviews.json, commit + push.

config/__init__.py — BOT_TOKEN, ADMIN_IDS, SITE_REPO_PATH, координаты базы, адрес.

Регистрация всех хендлеров в одном месте (bot/handlers/__init__.py или в main.py).​

Структуру проекта можно взять по образцу типичного aiogram‑бота: main.py + handlers/ + config/ + utils/.​​

3. Чек‑лист деплоя на VPS
Сохраните это, например, в deploy.md:

Подготовка сервера

Установить git, python3, python3-venv.

Создать пользователя (если нужно).

Клонирование репозиториев

git clone <репо бота>

git clone <репо сайта> site-repo рядом.

Установка окружения

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

Настройка .env

BOT_TOKEN

ADMIN_IDS

SITE_REPO_PATH=/полный/путь/к/site-repo

Настройка systemd‑сервиса

Файл /etc/systemd/system/pelikan-bot.service с WorkingDirectory, ExecStart из venv.

sudo systemctl daemon-reload

sudo systemctl enable pelikan-bot

sudo systemctl start pelikan-bot

Проверка логов: sudo journalctl -u pelikan-bot -f.
​

Проверка работы

Отправить команду /start в боте.

Оставить тестовый отзыв, убедиться, что админ получил карточку с кнопками.

Нажать ✅, проверить, что отзыв появился в site-repo/json/reviews.json и затем на сайте после деплоя.

Если нужно, можно отдельным сообщением сформировать готовый шаблон project.md целиком, который вы просто скопируете в репозиторий.

