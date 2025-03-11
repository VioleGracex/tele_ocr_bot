# TeleOCRBot

## Описание

TeleOCRBot - это Telegram-бот, который использует Tesseract OCR для распознавания текста из различных форматов документов (PDF, JPG, PNG, DOCX и другие). Затем распознанный текст отправляется для анализа через GPT-4 с использованием GPTunnel.

## Настройка и запуск

### Установка зависимостей

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

2. Установите Tesseract OCR:
   - **Ubuntu**:
     ```bash
     sudo apt-get install tesseract-ocr
     ```
   - **MacOS**:
     ```bash
     brew install tesseract
     ```
   - **Windows**:
     Скачайте и установите Tesseract OCR с [официального сайта](https://github.com/tesseract-ocr/tesseract/wiki).

### Настройка переменных окружения

1. Создайте файл `.env` в корневом каталоге проекта и добавьте следующие строки:
   ```plaintext
   TELEGRAM_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
   GPTUNNEL_API_URL=https://gptunnel.example.com/analyze
   ```

### Запуск бота

1. Запустите бота:
   ```bash
   python main.py
   ```

2. Отправьте файл боту в Telegram и получите результат распознавания и анализа текста.

## Конфигурация

- Замените `YOUR_TELEGRAM_BOT_TOKEN` в файле `.env` на токен вашего Telegram-бота.
- Настройте URL и данные запроса в файле `gptunnel.py` для интеграции с GPTunnel.
