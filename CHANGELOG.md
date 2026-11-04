# Changelog

What changed in json-shaper-lite, newest first.

## 1.1.0 - 2026-11-04

- New: a free MCP server, so AI apps like Claude Desktop and Cursor can use it. Start it with `uvx json-shaper-lite mcp` or `json-shaper-lite-mcp`.
- Two tools: `shape_text_to_json` for text in the chat and `shape_file_to_json` for a text file on your computer. Both only read. They never write files or use the internet.
- Listed in the official MCP Registry as `io.github.tidybytetools/json-shaper-lite`.
- Installing with pip now also installs the `mcp` package. The converter file itself still uses only Python's standard library.
- Added a Dockerfile, SECURITY.md, CONTRIBUTING.md and issue templates.

## 1.0.0 - 2026-11-04

- First release.
- Turns `key: value` notes, CSV/TSV and Markdown tables into JSON. Numbers, yes/no and empty values get the right type.
- `--json` gives one clean object for scripts and AI agents. `--quiet` hides the tip line.
- You can install it from PyPI with `pip install json-shaper-lite`.
- Needs Python 3.10 or newer.
