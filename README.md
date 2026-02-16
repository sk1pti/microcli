# 📚 MicroCLI — система микро-обучения через CLI

MicroCLI — это программа для ежедневного обучения через командную строку. Получайте небольшие задания, проверяйте свои знания и отслеживайте прогресс!

---

## 🇷🇺 Русская версия

### ✨ Возможности

- 📝 **30 заданий** — логика, математика, программирование, языки, общие знания
- 🌍 **Двуязычность** — русский и английский интерфейс
- 📊 **Статистика** — отслеживайте прогресс и streak дней
- 🎨 **Красивый интерфейс** — использует библиотеку Rich
- 🔄 **Расширяемость** — легко добавляйте новые задания

### 🚀 Установка

```bash
# Клонировать репозиторий
git clone https://github.com/sk1pti/microcli.git
cd microcli

# Установить зависимости
pip install rich

# Запустить
python microcli.py
```

### 📖 Использование

#### Выбор языка

```bash
# Русский интерфейс (по умолчанию)
python microcli.py today
python microcli.py --lang ru today

# Английский интерфейс
python microcli.py --lang en today
```

#### Команды

```bash
# Получить сегодняшнее задание
python microcli.py today

# Показать статистику
python microcli.py stats

# Выбрать категорию
python microcli.py category "Логика"
python microcli.py category "Математика"

# Показать все категории
python microcli.py categories

# Сбросить прогресс
python microcli.py reset
```

### 📁 Категории

| Категория | Заданий | Описание |
|-----------|---------|----------|
| Логика | 6 | Задачи на логическое мышление |
| Математика | 6 | Простые математические вопросы |
| Программирование | 6 | Основы Python |
| Языки | 6 | Изучение английских слов |
| Общие знания | 6 | Вопросы из разных областей |

### ➕ Добавление новых заданий

Добавьте задание в `tasks.json`:

```json
{
  "id": "my_task_001",
  "category": "Моя категория",
  "question": "Ваш вопрос?",
  "answer": "Правильный ответ",
  "explanation": "Объяснение ответа (необязательно)"
}
```

---

## 🇬🇧 English Version

### ✨ Features

- 📝 **30 tasks** — logic, math, programming, languages, trivia
- 🌍 **Bilingual** — Russian and English interface
- 📊 **Statistics** — track progress and streak days
- 🎨 **Beautiful UI** — using Rich library
- 🔄 **Extensible** — easily add new tasks

### 🚀 Installation

```bash
# Clone repository
git clone https://github.com/sk1pti/microcli.git
cd microcli

# Install dependencies
pip install rich

# Run
python microcli.py
```

### 📖 Usage

#### Language Selection

```bash
# Russian interface (default)
python microcli.py today
python microcli.py --lang ru today

# English interface
python microcli.py --lang en today
```

#### Commands

```bash
# Get today's task
python microcli.py today

# Show statistics
python microcli.py stats

# Choose category
python microcli.py category "Logic"
python microcli.py category "Math"

# Show all categories
python microcli.py categories

# Reset progress
python microcli.py reset
```

### 📁 Categories

| Category | Tasks | Description |
|----------|-------|-------------|
| Logic | 6 | Logical thinking tasks |
| Math | 6 | Simple math questions |
| Programming | 6 | Python basics |
| Languages | 6 | English vocabulary |
| Trivia | 6 | General knowledge questions |

### ➕ Adding New Tasks

Add a task to `tasks.json`:

```json
{
  "id": "my_task_001",
  "category": "My Category",
  "question": "Your question?",
  "answer": "Correct answer",
  "explanation": "Explanation (optional)"
}
```

---

## 📁 Structure

```
microcli/
├── microcli.py      # Main script
├── tasks.json       # 30 tasks database
├── progress.json   # User progress
├── utils.py        # Utility functions
├── locales/         # Translations
│   ├── ru.json     # Russian
│   └── en.json     # English
└── README.md       # This file
```

## 📝 License

MIT License

## 🤝 Contributing

Pull Requests with new tasks and improvements are welcome!
