"""Free MCP server for json-shaper-lite (stdio).

Run:  uvx json-shaper-lite mcp
  or: uvx --from json-shaper-lite json-shaper-lite-mcp
"""
import os
from typing import Annotated, Literal
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
import json_shaper_lite as lite

MAX_BYTES = 5_000_000  # 5 MB is plenty for notes and tables

mcp = FastMCP("json-shaper-lite")

READ_ONLY = dict(
    readOnlyHint=True,       # only reads; never writes or changes anything
    destructiveHint=False,
    idempotentHint=True,     # same input always gives the same JSON
    openWorldHint=False,     # no network; works on the text or local file you give it
)
FORMAT_HELP = (
    'format: "auto" (default) picks for you. Or force "kv" (key: value or key=value lines, '
    'a blank line starts a new record), "csv" (comma, semicolon, tab or | separated, first row '
    'is the header) or "markdown" (a | pipe | table, first row is the header).'
)


Format = Annotated[
    Literal["auto", "kv", "csv", "markdown"],
    Field(description='Input format. "auto" picks for you; "kv" = key: value lines, "csv" = CSV/TSV, "markdown" = a pipe table.'),
]


def _fill(fn):
    """Put the shared format help into the tool description."""
    fn.__doc__ = fn.__doc__.replace("FORMAT_HELP", FORMAT_HELP)
    return fn


def _check_format(fmt):
    if fmt not in ("auto", *lite.PARSERS):
        raise ValueError("format must be auto, kv, csv or markdown")


@mcp.tool(
    title="Turn text into JSON",
    annotations=ToolAnnotations(title="Turn text into JSON", **READ_ONLY),
)
@_fill
def shape_text_to_json(
    text: Annotated[str, Field(description="The text to turn into JSON: key: value lines, CSV/TSV or a Markdown table.")],
    format: Format = "auto",
) -> dict:
    """Turn pasted text (key: value notes, CSV/TSV or a Markdown table) into typed JSON.

    Use this when you have plain-text records or a table in the conversation and need
    clean JSON you can trust, without guessing values yourself. It is plain code, not
    an AI model, so the same text always gives the same JSON and nothing is made up.
    Do not use it when the text is already JSON, is nested data, is app logs, or is a
    file on disk (use shape_file_to_json for files).

    FORMAT_HELP

    Returns {"format": <format used>, "data": <JSON>}. data is a list of records for
    CSV and tables. For key: value text it is one object, or a list when blank lines
    split it into several records. Keys become lower_snake_case. Numbers become
    numbers, yes/no and true/false become booleans, empty or "null" becomes null.
    """
    _check_format(format)
    return lite.shape(text, format)


@mcp.tool(
    title="Turn a text file into JSON",
    annotations=ToolAnnotations(title="Turn a text file into JSON", **READ_ONLY),
)
@_fill
def shape_file_to_json(
    path: Annotated[str, Field(description="Full path to a UTF-8 text file (.txt, .csv, .tsv, .md), up to 5 MB.")],
    format: Format = "auto",
) -> dict:
    """Read a local text file (key: value notes, .csv, .tsv or a Markdown table) and return typed JSON.

    Use this when the data is in a file on this computer, so you don't have to paste
    it. The file is only read, never changed. Do not use it for Excel (.xlsx), PDF or
    other binary files, for files that are already JSON, or for app logs.

    path: full path to a UTF-8 text file, up to 5 MB.
    FORMAT_HELP

    Returns {"format": <format used>, "data": <JSON>}, the same as shape_text_to_json.
    """
    _check_format(format)
    path = os.path.expanduser(path)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"file not found: {path}")
    if os.path.getsize(path) > MAX_BYTES:
        raise ValueError("file is bigger than 5 MB")
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    return lite.shape(text, format)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
