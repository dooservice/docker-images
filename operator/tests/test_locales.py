"""The console reads its texts from dooservice/locales, English for whatever a language lacks.

The keys and blanks of every language are checked in dooservice/locales itself; here, only
that the console finds its file and falls back. Run from the repository's root:

    PYTHONPATH=operator/rootfs/opt/dooservice/lib python3 -m unittest discover -s operator/tests
"""

import os
import unittest
from pathlib import Path

LOCALES = Path(__file__).resolve().parent.parent / "locales"
os.environ["DOOSERVICE_LOCALES_DIR"] = str(LOCALES)

from dooservice_console.language import Catalog, Language  # noqa: E402


class LocalesTest(unittest.TestCase):
    def test_a_language_reads_its_own_file(self):
        self.assertNotEqual(Catalog("es", LOCALES).text("starting"), Catalog("en", LOCALES).text("starting"))

    def test_an_unknown_language_reads_english(self):
        self.assertEqual(Catalog("ja", LOCALES).text("starting"), Catalog("en", LOCALES).text("starting"))

    def test_a_path_is_never_a_language(self):
        self.assertEqual(Catalog("../en", LOCALES).texts, Catalog("en", LOCALES).texts)

    def test_the_agent_is_told_the_language_by_name(self):
        self.assertEqual(Language("pt-BR").name, "Portuguese")
