#!/bin/bash

# Script for safe production database connection
set -e

# Цвета для вывода
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${RED}⚠️  ВНИМАНИЕ: ПОДКЛЮЧЕНИЕ К ПРОДАКШН БАЗЕ ДАННЫХ ⚠️${NC}"
echo -e "${YELLOW}Вы собираетесь подключиться к продакшн базе данных!${NC}"
echo ""
echo "Это может быть опасно, так как:"
echo "1. Вы можете случайно изменить продакшн данные"
echo "2. Миграции будут применены к продакшн БД"
echo "3. Ошибки в коде могут повлиять на живую систему"
echo ""

# Проверяем наличие файла с продакшн настройками
if [ ! -f ".env.prod-db" ]; then
    echo -e "${RED}Ошибка: файл .env.prod-db не найден!${NC}"
    echo "Создайте файл .env.prod-db на основе .env.prod-db.example"
    echo "и заполните его настройками продакшн БД"
    exit 1
fi

# Проверяем обязательные переменные
source .env.prod-db
if [ -z "$DB_HOST" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ] || [ -z "$DB_NAME" ]; then
    echo -e "${RED}Ошибка: не все обязательные переменные заданы в .env.prod-db${NC}"
    echo "Необходимы: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME"
    exit 1
fi

echo -e "${YELLOW}Настройки подключения:${NC}"
echo "Host: $DB_HOST"
echo "User: $DB_USER"
echo "Database: $DB_NAME"
echo ""

# Подтверждение
read -p "Вы уверены, что хотите продолжить? Введите 'YES' для подтверждения: " confirm
if [ "$confirm" != "YES" ]; then
    echo "Операция отменена."
    exit 0
fi

# Опция: только чтение или полный доступ
echo ""
echo "Выберите режим работы:"
echo "1. Только чтение (без миграций)"
echo "2. Полный доступ (с миграциями) - ОПАСНО!"
read -p "Введите номер (1 или 2): " mode

case $mode in
    1)
        echo -e "${GREEN}Запуск в режиме только чтения...${NC}"
        # Экспортируем переменную для отключения миграций
        export SKIP_MIGRATIONS=true
        docker-compose -f docker-compose.dev.yaml --profile prod-db up --build
        ;;
    2)
        echo -e "${RED}Запуск в режиме полного доступа с миграциями...${NC}"
        read -p "Последнее предупреждение! Введите 'I_UNDERSTAND_THE_RISKS': " final_confirm
        if [ "$final_confirm" != "I_UNDERSTAND_THE_RISKS" ]; then
            echo "Операция отменена."
            exit 0
        fi
        docker-compose -f docker-compose.dev.yaml --profile prod-db up --build
        ;;
    *)
        echo "Неверный выбор. Операция отменена."
        exit 1
        ;;
esac
