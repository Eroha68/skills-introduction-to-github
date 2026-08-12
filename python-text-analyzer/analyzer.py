"""Простой анализатор текста без внешних зависимостей."""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any

WORD_RE = re.compile(r"[^\W_]+(?:['’-][^\W_]+)*", re.UNICODE)
SENTENCE_END_RE = re.compile(r"[.!?]+(?:[\"'»”)]*)")


def tokenize(text: str) -> list[str]:
    """Вернуть слова в нижнем регистре с поддержкой Unicode."""
    return [match.group(0).lower() for match in WORD_RE.finditer(text)]


def count_sentences(text: str) -> int:
    """Приблизительно посчитать предложения по завершающей пунктуации."""
    stripped = text.strip()
    if not stripped:
        return 0

    without_decimal_points = re.sub(r"(?<=\d)\.(?=\d)", "", stripped)
    endings = SENTENCE_END_RE.findall(without_decimal_points)
    return len(endings) if endings else 1


def normalize_stop_words(stop_words: Iterable[str] | None) -> set[str]:
    """Нормализовать стоп-слова тем же токенизатором, что и основной текст."""
    normalized: set[str] = set()
    for item in stop_words or ():
        normalized.update(tokenize(item))
    return normalized


def analyze_text(
    text: str,
    top_n: int = 5,
    stop_words: Iterable[str] | None = None,
    min_length: int = 1,
) -> dict[str, Any]:
    """Посчитать основные метрики текста с необязательной фильтрацией слов."""
    if top_n < 0:
        raise ValueError("top_n must be >= 0")
    if min_length < 1:
        raise ValueError("min_length must be >= 1")

    words = tokenize(text)
    stop_set = normalize_stop_words(stop_words)
    analyzed_words = [
        word for word in words if len(word) >= min_length and word not in stop_set
    ]
    frequencies = Counter(analyzed_words)
    average_word_length = (
        round(sum(len(word) for word in analyzed_words) / len(analyzed_words), 2)
        if analyzed_words
        else 0.0
    )

    return {
        "characters": len(text),
        "characters_no_spaces": sum(not char.isspace() for char in text),
        "words": len(words),
        "analyzed_words": len(analyzed_words),
        "excluded_words": len(words) - len(analyzed_words),
        "average_word_length": average_word_length,
        "unique_words": len(frequencies),
        "sentences": count_sentences(text),
        "top_words": frequencies.most_common(top_n),
    }


def result_to_csv(result: dict[str, Any]) -> str:
    """Вернуть результат анализа в CSV-формате."""
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["section", "name", "value"])

    for key in (
        "characters",
        "characters_no_spaces",
        "words",
        "analyzed_words",
        "excluded_words",
        "average_word_length",
        "unique_words",
        "sentences",
    ):
        writer.writerow(["metric", key, result[key]])

    for word, count in result["top_words"]:
        writer.writerow(["top_word", word, count])

    return output.getvalue().rstrip("\r\n")


def read_input(text: str | None, file_path: str | None) -> str:
    """Получить текст из аргумента командной строки или UTF-8 файла."""
    if text is not None:
        return text
    if file_path is not None:
        return Path(file_path).read_text(encoding="utf-8")
    raise ValueError("Укажите текст или --file")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Анализирует текст и выводит статистику.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--text", help="Текст для анализа")
    source.add_argument("--file", help="Путь к UTF-8 текстовому файлу")
    parser.add_argument("--top", type=int, default=5, help="Сколько частых слов показать")
    parser.add_argument(
        "--stop-word",
        action="append",
        default=[],
        help="Исключить слово из частотного анализа; параметр можно повторять",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=1,
        help="Минимальная длина слова для частотного анализа",
    )

    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true", help="Вывести результат в JSON")
    output.add_argument("--csv", action="store_true", help="Вывести результат в CSV")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        text = read_input(args.text, args.file)
        result = analyze_text(
            text,
            top_n=args.top,
            stop_words=args.stop_word,
            min_length=args.min_length,
        )
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.csv:
        print(result_to_csv(result))
    else:
        print(f"Символов: {result['characters']}")
        print(f"Символов без пробелов: {result['characters_no_spaces']}")
        print(f"Слов всего: {result['words']}")
        print(f"Слов после фильтров: {result['analyzed_words']}")
        print(f"Исключено слов: {result['excluded_words']}")
        print(f"Средняя длина слова: {result['average_word_length']}")
        print(f"Уникальных слов: {result['unique_words']}")
        print(f"Предложений: {result['sentences']}")
        print("Частые слова:")
        for word, count in result["top_words"]:
            print(f"  {word}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
