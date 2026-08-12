"""Простой анализатор текста без внешних зависимостей."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
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

    endings = SENTENCE_END_RE.findall(stripped)
    return len(endings) if endings else 1


def analyze_text(text: str, top_n: int = 5) -> dict[str, Any]:
    """Посчитать основные метрики текста."""
    if top_n < 0:
        raise ValueError("top_n must be >= 0")

    words = tokenize(text)
    frequencies = Counter(words)

    return {
        "characters": len(text),
        "characters_no_spaces": sum(not char.isspace() for char in text),
        "words": len(words),
        "unique_words": len(frequencies),
        "sentences": count_sentences(text),
        "top_words": frequencies.most_common(top_n),
    }


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
    parser.add_argument("--json", action="store_true", help="Вывести результат в JSON")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        text = read_input(args.text, args.file)
        result = analyze_text(text, args.top)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Символов: {result['characters']}")
        print(f"Символов без пробелов: {result['characters_no_spaces']}")
        print(f"Слов: {result['words']}")
        print(f"Уникальных слов: {result['unique_words']}")
        print(f"Предложений: {result['sentences']}")
        print("Частые слова:")
        for word, count in result["top_words"]:
            print(f"  {word}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
