import io, os, sys, unittest
from contextlib import redirect_stdout, redirect_stderr
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import json_shaper_lite as js

class T(unittest.TestCase):
    def test_kv(self): self.assertEqual(js.shape("a: 1")["data"], {"a": 1})
    def test_kv_types(self):
        self.assertEqual(js.shape("Name: Ada\nAge: 36\nActive: yes\nNote: null")["data"],
                         {"name": "Ada", "age": 36, "active": True, "note": None})
    def test_kv_multiple_records(self):
        self.assertEqual(js.shape("a: 1\n\na: 2")["data"], [{"a": 1}, {"a": 2}])
    def test_csv(self): self.assertEqual(js.shape("x,y\n1,2")["data"], [{"x": 1, "y": 2}])
    def test_semicolon_csv(self):
        r = js.shape("Item;Price\nTea;2.5\nCake;4", "csv")["data"]
        self.assertEqual(r, [{"item": "Tea", "price": 2.5}, {"item": "Cake", "price": 4}])
    def test_md(self): self.assertEqual(js.shape("|a|\n|-|\n|z|")["data"], [{"a": "z"}])
    def test_detect(self):
        self.assertEqual(js.detect("|a|b|\n|-|-|\n|1|2|"), "markdown")
        self.assertEqual(js.detect("x,y\n1,2"), "csv")
        self.assertEqual(js.detect("a: 1\nb: 2"), "kv")
    def run_main(self, argv, stdin):
        out, err = io.StringIO(), io.StringIO()
        old = sys.stdin; sys.stdin = io.StringIO(stdin)
        try:
            with redirect_stdout(out), redirect_stderr(err): code = js.main(argv)
        finally: sys.stdin = old
        return code, out.getvalue(), err.getvalue()
    def test_cli_json_envelope_is_clean(self):
        code, out, err = self.run_main(["--json"], "a: 1")
        self.assertEqual(code, 0)
        self.assertIn('"ok": true', out)
        self.assertNotIn("gumroad", out)
    def test_help_has_paid_link(self):
        out = io.StringIO()
        with redirect_stdout(out), self.assertRaises(SystemExit): js.main(["--help"])
        self.assertIn("https://tidybyte.gumroad.com/l/cznmeo", out.getvalue())
    def test_bad_file(self):
        code, out, err = self.run_main(["--json", "/nope/missing.txt"], "")
        self.assertEqual(code, 1); self.assertIn('"ok": false', out)

if __name__ == "__main__": unittest.main()
