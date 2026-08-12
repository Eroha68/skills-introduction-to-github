# Python Text Analyzer

Учебный проект: простой анализатор текста на Python без внешних библиотек.

## Что умеет

- считать символы;
- считать символы без пробелов;
- считать слова и уникальные слова;
- считать среднюю длину анализируемого слова;
- приблизительно считать предложения;
- показывать самые частые слова;
- фильтровать стоп-слова;
- исключать из частотного анализа слишком короткие слова;
- работать с русским и английским текстом;
- выводить результат обычным текстом, JSON или CSV.

## Требования

Python 3.10+.

## Запуск

Из корня репозитория:

```bash
python python-text-analyzer/analyzer.py --text "Привет, мир! Привет ещё раз."
```

JSON-вывод:

```bash
python python-text-analyzer/analyzer.py --text "Привет, мир!" --json
```

CSV-вывод:

```bash
python python-text-analyzer/analyzer.py --text "Привет, мир! Привет ещё раз." --csv
```

Фильтрация стоп-слов:

```bash
python python-text-analyzer/analyzer.py --text "И кот, и пёс, и кот." --stop-word и
```

Параметр `--stop-word` можно повторять:

```bash
python python-text-analyzer/analyzer.py --text "Это очень простой тест" --stop-word это --stop-word очень
```

Игнорировать слова короче трёх символов:

```bash
python python-text-analyzer/analyzer.py --text "я и кот дом" --min-length 3
```

Анализ UTF-8 файла:

```bash
python python-text-analyzer/analyzer.py --file example.txt --top 10
```

Параметры фильтрации влияют на `analyzed_words`, `excluded_words`, `average_word_length`, `unique_words` и `top_words`. Поле `words` всегда показывает общее число найденных слов до фильтрации.

`average_word_length` — средняя длина слов, оставшихся после применения `--stop-word` и `--min-length`, округлённая до двух знаков. Если после фильтрации слов нет, значение равно `0.0`.

## Тесты

```bash
python -m unittest discover -s python-text-analyzer -p "test_*.py" -v
```

GitHub Actions автоматически выполняет тесты на Python 3.10 и 3.12 при Pull Request в `main`. Итоговая обязательная проверка называется `Required CI`.

## Безопасность

Программа не использует сеть, API-ключи, базу данных и внешние зависимости. При `--file` она только читает указанный пользователем локальный UTF-8 файл.
