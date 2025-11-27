#!/bin/bash

REPO_PATH=/home/andy/pelikan-bot-aiogram

cd "$REPO_PATH" || { echo "❌ Путь не найден: $REPO_PATH"; exit 1; }

echo "📂 Работаем в: $(pwd)"

# Обновить локальную ветку
echo "🔄 git pull origin main..."
git pull origin main

# Проверяем изменения
if git diff --quiet && git diff --staged --quiet; then
  echo "ℹ️ Нет изменений для коммита"
  exit 0
fi

# Добавить изменения
git add .

# Запрашиваем комментарий (с дефолтом)
read -p "💬 Сообщение коммита (Enter=Update from server): " commit_message
commit_message=${commit_message:-"Update from server"}

# Коммит
echo "✅ Коммит: $commit_message"
git commit -m "$commit_message"

# ✅ ПУШ ЧЕРЕЗ SSH (без .env и паролей!)
echo "🚀 git push origin main..."
git push origin main

echo "🎉 ✅ Изменения отправлены!"
echo "📊 Статус:"
git status

