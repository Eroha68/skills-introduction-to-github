import unittest

from analyzer import analyze_text, count_sentences, tokenize


class TextAnalyzerTests(unittest.TestCase):
    def test_empty_text(self) -> None:
        result = analyze_text("")
        self.assertEqual(result["characters"], 0)
        self.assertEqual(result["words"], 0)
        self.assertEqual(result["unique_words"], 0)
        self.assertEqual(result["sentences"], 0)
        self.assertEqual(result["top_words"], [])

    def test_russian_text(self) -> None:
        text = "Привет, мир! Привет ещё раз."
        result = analyze_text(text, top_n=2)
        self.assertEqual(result["words"], 5)
        self.assertEqual(result["unique_words"], 4)
        self.assertEqual(result["sentences"], 2)
        self.assertEqual(result["top_words"][0], ("привет", 2))

    def test_unicode_and_hyphenated_words(self) -> None:
        words = tokenize("AI-сервис и state-of-the-art")
        self.assertIn("ai-сервис", words)
        self.assertIn("state-of-the-art", words)

    def test_sentence_without_terminal_punctuation(self) -> None:
        self.assertEqual(count_sentences("Одно предложение без точки"), 1)

    def test_negative_top_rejected(self) -> None:
        with self.assertRaises(ValueError):
            analyze_text("текст", top_n=-1)


if __name__ == "__main__":
    unittest.main()
