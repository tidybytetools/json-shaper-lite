#!/usr/bin/env python3
"""json-shaper-lite (MIT): free edition. Pro adds log parsing + address splitting: turn messy text into clean JSON. This file uses only the Python standard library; the MCP server (json_shaper_lite_mcp.py) needs the mcp package."""
import argparse, csv, io, json, re, sys

__version__ = "1.1.2"
PRO_URL = "https://tidybyte.gumroad.com/l/cznmeo"
PRO_LINE = f"Need log files parsed too? json-shaper (paid) does that: {PRO_URL}"

def _num(v):
    v = v.strip()
    if re.fullmatch(r"-?\d+", v): return int(v)
    if re.fullmatch(r"-?\d*\.\d+", v): return float(v)
    if v.lower() in ("true", "yes"): return True
    if v.lower() in ("false", "no"): return False
    if v.lower() in ("null", "none", ""): return None
    return v

def _key(k):
    return re.sub(r"[^a-z0-9]+", "_", k.strip().lower()).strip("_")

def parse_kv(text):
    """'Key: value' or 'key=value' lines. Blank lines separate records."""
    records, cur = [], {}
    for line in text.splitlines():
        if not line.strip():
            if cur: records.append(cur); cur = {}
            continue
        m = re.match(r"\s*([^:=]+?)\s*[:=]\s*(.*)$", line)
        if m: cur[_key(m.group(1))] = _num(m.group(2))
    if cur: records.append(cur)
    return records[0] if len(records) == 1 else records

def _record(head, row, lineno):
    if len(row) > len(head):
        raise ValueError(f"row {lineno} has {len(row)} fields, expected {len(head)}")
    row = row + [""] * (len(head) - len(row))
    return {h: _num(c) for h, c in zip(head, row)}

def parse_csv(text):
    sample = text[:2048]
    try: dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error: dialect = csv.excel
    rows = [r for r in csv.reader(io.StringIO(text.strip()), dialect) if any(c.strip() for c in r)]
    if not rows: return []
    head = [_key(h) for h in rows[0]]
    return [_record(head, r, i) for i, r in enumerate(rows[1:], start=2)]

def parse_markdown_table(text):
    lines = [l.strip() for l in text.splitlines() if l.strip().startswith("|")]
    lines = [l for l in lines if not re.fullmatch(r"\|[\s:\-|]+\|?", l)]
    cells = [[c.strip() for c in l.strip("|").split("|")] for l in lines]
    if not cells: return []
    head = [_key(h) for h in cells[0]]
    return [_record(head, r, i) for i, r in enumerate(cells[1:], start=2)]

def detect(text):
    t = text.strip()
    lines = [l for l in t.splitlines() if l.strip()]
    if not lines: return "kv"
    if sum(l.strip().startswith("|") for l in lines) >= 2: return "markdown"
    if sum(bool(re.match(r"\s*[^:=,;|\t]+?\s*[:=]\s*", l)) for l in lines) >= len(lines) * 0.6: return "kv"
    return "csv"

PARSERS = {"kv": parse_kv, "csv": parse_csv, "markdown": parse_markdown_table}

def shape(text, fmt="auto"):
    fmt = detect(text) if fmt == "auto" else fmt
    return {"format": fmt, "data": PARSERS[fmt](text)}

def run_mcp():
    """Start the stdio MCP server (needs the mcp package, which pip installs for you)."""
    try:
        import json_shaper_lite_mcp
    except ImportError as e:
        print(f"error: the MCP server needs the mcp package ({e}). Run: pip install json-shaper-lite", file=sys.stderr)
        return 1
    json_shaper_lite_mcp.main()
    return 0

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["mcp"]:
        return run_mcp()
    p = argparse.ArgumentParser(prog="json-shaper-lite", description="Turn messy text into clean JSON. Run `json-shaper-lite mcp` to start the MCP server (to read a file named mcp, use ./mcp).", epilog=PRO_LINE)
    p.add_argument("file", nargs="?", help="input file (default: stdin)")
    p.add_argument("-f", "--format", default="auto", choices=["auto"] + list(PARSERS))
    p.add_argument("--json", action="store_true", help="machine-readable envelope: {ok, format, data}")
    p.add_argument("--indent", type=int, default=2)
    p.add_argument("-q", "--quiet", action="store_true", help="don't print the one-line note about the paid version")
    p.add_argument("--version", action="version", version=__version__)
    a = p.parse_args(argv)
    try:
        text = open(a.file, encoding="utf-8").read() if a.file else sys.stdin.read()
        res = shape(text, a.format)
        out = {"ok": True, **res} if a.json else res["data"]
        print(json.dumps(out, indent=a.indent, ensure_ascii=False))
        if not a.quiet and not a.json and sys.stderr.isatty():
            print(PRO_LINE, file=sys.stderr)
        return 0
    except Exception as e:
        if a.json:
            print(json.dumps({"ok": False, "error": str(e)})); return 1
        print(f"error: {e}", file=sys.stderr); return 1

if __name__ == "__main__":
    sys.exit(main())
