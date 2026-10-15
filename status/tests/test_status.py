"""The status page: which card an address gets, and what the page shows of it.

    cd status && python3 -m unittest discover tests
"""

import json
from pathlib import Path
import tempfile
import unittest

from dooservice_status.card import Card, Cards, Host
from dooservice_status.cases import Case
from dooservice_status.page import Page


class HostTest(unittest.TestCase):
    def test_lowercased_and_without_port(self) -> None:
        self.assertEqual(Host.of("ERP.Acme.pe:443"), "erp.acme.pe")

    def test_nothing_that_could_leave_the_directory(self) -> None:
        for header in ("../etc/passwd", "a/b", "..", ".hidden", "a..b", "", "a b", "x" * 300):
            self.assertEqual(Host.of(header), "", header)


class CardsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = Path(tempfile.mkdtemp())
        self.cards = Cards(self.directory)

    def write(self, host: str, data: object) -> None:
        (self.directory / f"{host}.json").write_text(json.dumps(data))

    def test_no_card_is_no_odoo(self) -> None:
        self.assertEqual(self.cards.of("erp.acme.pe"), Card(Case.UNKNOWN))

    def test_a_card_with_progress(self) -> None:
        self.write("erp.acme.pe", {"case": "updating", "step": "Updating modules", "progress": 40})
        self.assertEqual(self.cards.of("erp.acme.pe"), Card(Case.UPDATING, "Updating modules", 40))

    def test_progress_kept_within_bounds(self) -> None:
        self.write("erp.acme.pe", {"case": "creating", "progress": 140})
        self.assertEqual(self.cards.of("erp.acme.pe").progress, 100)

    def test_a_card_it_cannot_read_is_no_odoo(self) -> None:
        self.write("erp.acme.pe", {"case": "on fire"})
        self.assertEqual(self.cards.of("erp.acme.pe").case, Case.UNKNOWN)
        (self.directory / "bad.pe.json").write_text("{")
        self.assertEqual(self.cards.of("bad.pe").case, Case.UNKNOWN)


class PageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.page = Page()

    def test_every_case_renders(self) -> None:
        for case in Case:
            html = self.page.render(Card(case))
            self.assertIn("data-dooservice-status", html)
            self.assertIn("support@dooservice.sh", html)
            self.assertIn("soporte@apiservicesac.com", html)

    def test_progress_shows_its_step_escaped(self) -> None:
        html = self.page.render(Card(Case.CREATING, "<b>Installing</b>", 62))
        self.assertIn("&lt;b&gt;Installing&lt;/b&gt;", html)
        self.assertIn('aria-valuenow="62"', html)

    def test_no_odoo_invites_to_discover(self) -> None:
        self.assertIn("Discover Dooservice", self.page.render(Card(Case.UNKNOWN)))
        self.assertIn("Open Dooservice", self.page.render(Card(Case.STOPPED)))

    def test_no_odoo_names_the_address_it_was_asked_for(self) -> None:
        html = self.page.render(Card(Case.UNKNOWN), "erp.acme.pe")
        self.assertIn("<mark>erp.acme.pe</mark> does not exist (anymore?)", html)
        self.assertIn("My projects", html)
        self.assertNotIn("<mark>", self.page.render(Card(Case.STOPPED), "erp.acme.pe"))


if __name__ == "__main__":
    unittest.main()
