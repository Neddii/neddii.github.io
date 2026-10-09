import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("validate_static", Path(__file__).resolve().parents[1] / "scripts/validate_static.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class StaticChecks(unittest.TestCase):
    def fixture(self, html):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name).resolve()
        (root / "index.html").write_text(html)
        return root

    def test_missing_asset_and_malformed_alt_are_detected(self):
        errors = validator.validate(self.fixture('<img src="missing.jpg"=alt"photo">'))
        self.assertTrue(any("missing local target" in e for e in errors))
        self.assertTrue(any("missing alt" in e for e in errors))

    def test_encoded_asset_query_and_external_deep_links(self):
        root = self.fixture('<img src="my%20photo.jpg?v=1" alt=""><a href="shortcuts://run-shortcut?name=Relay">Relay</a><a href="https://example.com">External</a>')
        (root / "my photo.jpg").touch()
        self.assertEqual(validator.validate(root), [])

    def test_escape_and_symlink_escape_are_detected(self):
        root = self.fixture('<img src="../outside.jpg" alt=""><img src="escape" alt="">')
        (root / "escape").symlink_to(root.parent / "outside.jpg")
        self.assertEqual(sum("escapes site" in e for e in validator.validate(root)), 2)

    def test_manifest_icons_and_precache_targets_are_checked(self):
        root = self.fixture("<p>Site</p>")
        (root / "app.webmanifest").write_text('{"start_url":"./", "icons":[{"src":"missing.png"}]}')
        (root / "sw.js").write_text('const ASSETS=["missing.html"];')
        self.assertEqual(sum("missing local target" in e for e in validator.validate(root)), 2)

    def test_inline_and_external_js_syntax_is_checked(self):
        root = self.fixture('<script>const broken = ;</script>')
        (root / "sw.js").write_text('const other = ;')
        self.assertEqual(sum("syntax error" in e for e in validator.validate(root)), 2)

    def test_bad_manifest_fails(self):
        root = self.fixture("<p>Site</p>")
        (root / "app.webmanifest").write_text('{')
        self.assertTrue(any("invalid manifest" in e for e in validator.validate(root)))
