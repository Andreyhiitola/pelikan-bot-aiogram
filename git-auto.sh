#!/bin/bash

# Загружаем переменные из .env
if [ -f .env ]; then
  export $(cat .env | xargs)
else
  echo "Ошибка: файл .env не найден"
  exit 1
fi

REPO_PATH=/home/andy/pelikan-bot-aiogram


cd "$REPO_PATH" || exit 1

# Обновить локальную ветку
git pull origin main

# Добавить изменения
git add .

# Запрашиваем комментарий
read -p "Введите сообщение для коммита: " commit_message

if [ -z "$commit_message" ]; then
  echo "Сообщение коммита не может быть пустым."
  exit 1
fi

# Коммит
git commit -m "$commit_message"

# Пуш с аутентификацией
git push https://$GIT_USERNAME:$GIT_PASSWORD@https://github.com/Andreyhiitola/pelikan-bot-aiogram.git

echo "✅ Изменения отправлены."
