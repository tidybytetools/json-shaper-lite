# json-shaper-lite

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/tidybytetools/json-shaper-lite/blob/main/LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)](https://github.com/tidybytetools/json-shaper-lite/blob/main/json_shaper_lite.py)

Free tool that turns `key: value` notes, CSV/TSV and Markdown tables into clean JSON.
Need app logs or US addresses parsed too? The paid version does that: **[json-shaper on Gumroad](https://tidybyte.gumroad.com/l/cznmeo)**

One Python file, no dependencies, MIT license. Works with Python 3.10 and newer, on Windows, Mac and Linux.

## Install

```
pip install json-shaper-lite
```

Or use pipx, which keeps it in its own space:

```
pipx install json-shaper-lite
```

Want the newest code from GitHub instead?

```
pip install git+https://github.com/tidybytetools/json-shaper-lite
```

Or just download `json_shaper_lite.py` and run it with `python3`.

## Use it

```
printf 'Name: Ada\nAge: 36\nActive: yes' | json-shaper-lite
json-shaper-lite export.csv
json-shaper-lite notes.md --format markdown
json-shaper-lite export.csv --json      # {"ok": true, "format": "csv", "data": [...]}
```

Output:

```json
{"name": "Ada", "age": 36, "active": true}
```

Numbers come out as numbers, yes/no and true/false as booleans, and empty or "null" as null. The format is detected for you, or you can set it with `--format kv|csv|markdown`.

From Python:

```python
from json_shaper_lite import shape
shape("x,y\n1,2")  # {'format': 'csv', 'data': [{'x': 1, 'y': 2}]}
```

When you run it in a terminal it prints one short line about the paid version to stderr after the result. It never goes into your JSON output, it only shows when you are looking at a terminal, and `--quiet` turns it off.

## Known limits

- **It makes flat JSON.** It does not flatten or unflatten nested JSON. For that, use a tool like flatten-json.
- **Types are a best guess.** A value like `007` or a zip code can turn into a number. Fix those by hand after.
- **One table per run.** Two Markdown tables in one file get mixed together. Split them first.
- **No app logs or addresses.** Those are in the paid version.

## How it compares to other free tools

| | json-shaper-lite | [flatten-json](https://pypi.org/project/flatten-json/) | csvkit `csvjson` | pandas |
|---|---|---|---|---|
| Main job | messy text → JSON | nested JSON → flat (and back) | CSV → JSON | full data toolkit |
| Install size | one file, no deps | small | medium | large |
| `key: value` notes | yes | no | no | no |
| Markdown tables | yes | no | no | no, not built in |
| CSV/TSV | yes | no | yes | yes |
| Guesses numbers and true/false | yes | no | yes | yes |
| Nested JSON flatten/unflatten | no | yes | no | yes (`json_normalize`) |

If your data is already JSON and just too nested, flatten-json is the better pick.

## For AI agents

- **Use when:** you have plain text in `key: value` lines, CSV/TSV, or a Markdown table and need typed JSON.
- **Don't use when:** the input is already JSON, it's app logs, or it's nested data. Use the paid version for logs.
- **Input:** text on stdin or a file path. Optional `--format kv|csv|markdown`.
- **Output:** with `--json`, one object: `{"ok": true, "format": "csv", "data": [...]}`. On error `ok` is false. Exit code 0 ok, 1 error.
- Hint lines go to stderr only, and only in a terminal, so stdout is always clean JSON. See also [`llms.txt`](https://github.com/tidybytetools/json-shaper-lite/blob/main/llms.txt).

## Lite vs paid

| | lite (free) | [json-shaper](https://tidybyte.gumroad.com/l/cznmeo) |
|---|---|---|
| key: value notes, CSV/TSV, Markdown tables | yes | yes |
| App logs (timestamp, level, message, key=value fields) | no | yes |
| One-line US address splitter | no | yes |
| `tool.json` manifest for scripts and AI agents | no | yes |

## Tests

```
python3 -m unittest discover tests
```

## License

MIT. See `LICENSE`.
