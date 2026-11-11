import io, os, sys, unittest
from contextlib import redirect_stdout, redirect_stderr
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import json_shaper_lite as js


def run_main(argv, stdin):
    out, err = io.StringIO(), io.StringIO()
    old = sys.stdin
    sys.stdin = io.StringIO(stdin)
    try:
        with redirect_stdout(out), redirect_stderr(err):
            code = js.main(argv)
    finally:
        sys.stdin = old
    return code, out.getvalue(), err.getvalue()


class RaggedRows(unittest.TestCase):
    def test_csv_short_row_padded_with_null(self):
        self.assertEqual(js.shape("x,y\n4", "csv")["data"],
                         [{"x": 4, "y": None}])

    def test_csv_long_row_raises(self):
        with self.assertRaises(ValueError):
            js.shape("x,y\n1,2,3", "csv")

    def test_markdown_short_row_padded_with_null(self):
        self.assertEqual(js.shape("|x|y|\n|-|-|\n|4|", "markdown")["data"],
                         [{"x": 4, "y": None}])

    def test_markdown_long_row_raises(self):
        with self.assertRaises(ValueError):
            js.shape("|x|y|\n|-|-|\n|1|2|3|", "markdown")

    def test_cli_long_row_is_clean_error(self):
        code, out, err = run_main(["--format", "csv"], "x,y\n1,2,3\n")
        self.assertEqual(code, 1)
        self.assertIn("row 2", err)

    def test_cli_json_envelope_long_row(self):
        code, out, err = run_main(["--format", "csv", "--json"], "x,y\n1,2,3\n")
        self.assertEqual(code, 1)
        self.assertIn('"ok": false', out)


if __name__ == "__main__":
    unittest.main()
