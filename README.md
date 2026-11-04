# json-shaper-lite

Free tool that turns `key: value` notes, CSV/TSV and Markdown tables into clean JSON.
Need app logs or US addresses parsed too? The paid version does that: **[json-shaper on Gumroad](https://tidybyte.gumroad.com/l/cznmeo)**

One Python file, no dependencies, MIT license. Works with Python 3.8 and newer, on Windows, Mac and Linux.

## Install

```
pip install json-shaper-lite
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
