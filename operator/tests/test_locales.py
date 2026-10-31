"""The console's locale files, checked against English, the complete reference.

A translation may leave a text out, and English is printed instead; it must not add a
key English lacks, nor a placeholder the English text does not fill. Run from the
repository's root:

    PYTHONPATH=operator/rootfs/opt/dooservice/lib python3 -m unittest discover -s operator/tests
"""

import string
import unittest

from dooservice_console.constants import DEFAULT_LANGUAGE, LOCALES_DIR
from dooservice_console.language import Catalog


class LocalesTest(unittest.TestCase):
    """Every locale keeps to English's keys and placeholders."""

    def setUp(self):
        self.english = Catalog(DEFAULT_LANGUAGE).load(DEFAULT_LANGUAGE)
        self.locales = {path.stem: Catalog(path.stem).load(path.stem) for path in LOCALES_DIR.glob("*.toml")}

    def placeholders(self, text):
        return {name for _, name, _, _ in string.Formatter().parse(text) if name}

    def test_locales_only_use_english_keys(self):
        for code, texts in self.locales.items():
            with self.subTest(code=code):
                self.assertEqual(set(texts) - set(self.english), set())

    def test_locales_only_use_english_placeholders(self):
        for code, texts in self.locales.items():
            for key, text in texts.items():
                with self.subTest(code=code, key=key):
                    self.assertLessEqual(self.placeholders(text), self.placeholders(self.english.get(key, "")))


if __name__ == "__main__":
    unittest.main()
