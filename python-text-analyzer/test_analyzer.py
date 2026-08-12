import csv
import io
import unittest

from analyzer import analyze_text, count_sentences, result_to_csv, tokenize


class TextAnalyzerTests(unittest.TestCase):
    def test_empty_text(self) -> None:
        result = analyze_text("")
        self.assertEqual(result["characters"], 0)
        self.assertEqual(result["words"], 0)
        self.assertEqual(result["analyzed_words"], 0)
        self.assertEqual(result["excluded_words"], 0)
        self.assertEqual(result["average_word_length"], 0.0)
        self.assertEqual(result["unique_words"], 0)
        self.assertEqual(result["sentences"], 0)
        self.assertEqual(result["top_words"], [])

    def test_russian_text(self) -> None:
        text = "Привет, мир! Привет ещё раз."
        result = analyze_text(text, top_n=2)
        self.assertEqual(result["words"], 5)
        self.assertEqual(result["analyzed_words"], 5)
        self.assertEqual(result["unique_words"], 4)
        self.assertEqual(result["sentences"], 2)
        self.assertEqual(result["top_words"][0], ("привет", 2))

    def test_unicode_and_hyphenated_words(self) -> None:
        words = tokenize("AI-сервис и state-of-the-art")
        self.assertIn("ai-сервис", words)
        self.assertIn("state-of-the-art", words)

    def test_sentence_without_terminal_punctuation(self) -> None:
        self.assertEqual(count_sentences("Одно предложение без точки"), 1)

    def test_decimal_number_does_not_split_sentence(self) -> None:
        self.assertEqual(count_sentences("Версия 3.14 работает."), 1)

    def test_negative_top_rejected(self) -> None:
        with self.assertRaises(ValueError):
            analyze_text("текст", top_n=-1)

    def test_stop_words_are_excluded_from_frequency_analysis(self) -> None:
        result = analyze_text("И кот, и пёс, и кот.", stop_words=["и"], top_n=3)
        self.assertEqual(result["words"], 6)
        self.assertEqual(result["analyzed_words"], 3)
        self.assertEqual(result["excluded_words"], 3)
        self.assertEqual(result["top_words"][0], ("кот", 2))
        self.assertNotIn(("и", 3), result["top_words"])

    def test_minimum_word_length(self) -> None:
        result = analyze_text("я и кот дом", min_length=3)
        self.assertEqual(result["words"], 4)
        self.assertEqual(result["analyzed_words"], 2)
        self.assertEqual(result["excluded_words"], 2)
        self.assertEqual(result["unique_words"], 2)

    def test_average_word_length_uses_filtered_words(self) -> None:
        result = analyze_text("я кот дома", min_length=3)
        self.assertEqual(result["analyzed_words"], 2)
        self.assertEqual(result["average_word_length"], 3.5)

    def test_average_word_length_is_zero_when_all_words_excluded(self) -> None:
        result = analyze_text("я и", min_length=3)
        self.assertEqual(result["analyzed_words"], 0)
        self.assertEqual(result["average_word_length"], 0.0)

    def test_invalid_minimum_word_length_rejected(self) -> None:
        with self.assertRaises(ValueError):
            analyze_text("текст", min_length=0)

    def test_csv_output(self) -> None:
        result = analyze_text("Привет привет мир", top_n=2)
        rows = list(csv.reader(io.StringIO(result_to_csv(result))))
        self.assertEqual(rows[0], ["section", "name", "value"])
        self.assertIn(["metric", "words", "3"], rows)
        self.assertIn(["metric", "average_word_length", "5.33"], rows)
        self.assertIn(["top_word", "привет", "2"], rows)


if __name__ == "__main__":
    unittest.main()
