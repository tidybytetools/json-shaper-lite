"""Starts the MCP server over stdio (both ways it can start), lists tools, and calls them."""
import asyncio, json, os, sys, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    ClientSession = None

READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}


def _data(res):
    """The tool result as Python data (structured content if present, else the JSON text)."""
    if res.structuredContent is not None:
        sc = res.structuredContent
        return sc.get("result", sc) if set(sc) == {"result"} else sc
    return json.loads(res.content[0].text)


async def _session(args, fn):
    params = StdioServerParameters(command=sys.executable, args=args, cwd=ROOT)
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            return await fn(s)


@unittest.skipIf(ClientSession is None, "mcp not installed")
class MCP(unittest.TestCase):
    def test_tools_and_annotations(self):
        async def go(s):
            return (await s.list_tools()).tools
        tools = asyncio.run(_session([os.path.join(ROOT, "json_shaper_lite_mcp.py")], go))
        self.assertEqual(sorted(t.name for t in tools), ["shape_file_to_json", "shape_text_to_json"])
        for t in tools:
            self.assertTrue(t.title)
            self.assertIn("Use this when", t.description)
            self.assertNotIn("FORMAT_HELP", t.description)
            for k, v in READ_ONLY.items():
                self.assertIs(getattr(t.annotations, k), v, f"{t.name} {k}")

    def test_calls(self):
        async def go(s):
            kv = await s.call_tool("shape_text_to_json", {"text": "Name: Ada\nAge: 36\nActive: yes"})
            md = await s.call_tool("shape_text_to_json", {"text": "| a | b |\n|---|---|\n| 1 | x |"})
            f = await s.call_tool("shape_file_to_json", {"path": os.path.join(HERE, "fixtures", "menu.tsv")})
            bad_fmt = await s.call_tool("shape_text_to_json", {"text": "a: 1", "format": "xml"})
            missing = await s.call_tool("shape_file_to_json", {"path": "/nope/missing.csv"})
            return kv, md, f, bad_fmt, missing
        kv, md, f, bad_fmt, missing = asyncio.run(_session([os.path.join(ROOT, "json_shaper_lite_mcp.py")], go))
        self.assertEqual(_data(kv), {"format": "kv", "data": {"name": "Ada", "age": 36, "active": True}})
        self.assertEqual(_data(md), {"format": "markdown", "data": [{"a": 1, "b": "x"}]})
        self.assertEqual(_data(f), {"format": "csv", "data": [
            {"item": "Tea", "price": 2.5, "in_stock": True},
            {"item": "Cake", "price": 4, "in_stock": False}]})
        self.assertTrue(bad_fmt.isError)
        self.assertTrue(missing.isError)

    def test_cli_mcp_subcommand_starts_server(self):
        async def go(s):
            return [t.name for t in (await s.list_tools()).tools]
        names = asyncio.run(_session([os.path.join(ROOT, "json_shaper_lite.py"), "mcp"], go))
        self.assertIn("shape_text_to_json", names)


if __name__ == "__main__":
    unittest.main()
