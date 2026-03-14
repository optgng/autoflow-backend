#!/bin/bash

# Имя итогового файла
OUTPUT_FILE="project_tests.txt"

# Директории для сканирования (по умолчанию src и tests)
TARGET_DIRS=${@:-src tests}

# Очищаем итоговый файл, если он уже существует
> "$OUTPUT_FILE"

echo "Начинаю сбор файлов из директорий: $TARGET_DIRS"

for DIR in $TARGET_DIRS; do
    if [ -d "$DIR" ]; then
        # Находим все текстовые файлы (исключая бинарники, node_modules, .git и т.д.)
        # При необходимости добавьте фильтр по расширениям: -name "*.js" -o -name "*.py"
        find "$DIR" -type f -not -path "*/node_modules/*" -not -path "*/__pycache__/*" | while read -r FILE; do
            # Записываем путь к файлу и визуальный разделитель
            echo "================================================================================" >> "$OUTPUT_FILE"
            echo "File path: $FILE" >> "$OUTPUT_FILE"
            echo "================================================================================" >> "$OUTPUT_FILE"
            
            # Добавляем содержимое файла
            cat "$FILE" >> "$OUTPUT_FILE"
            
            # Добавляем отступы между файлами
            echo -e "\n\n" >> "$OUTPUT_FILE"
        done
    else
        echo "⚠️ Директория '$DIR' не найдена. Пропускаю..."
    fi
done

echo "✅ Все файлы успешно собраны в $OUTPUT_FILE"

