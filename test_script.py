import unittest

import script


def routes_for(nodes):
    node_map, children = script.build_graph(nodes)
    return script.traverse_graph(node_map, children)


class CycleTests(unittest.TestCase):
    def test_cycle_terminates_and_keeps_routes(self):
        nodes = [
            {"id": "1", "source": None, "target": "2", "properties": {"type": "entry"}},
            {"id": "2", "source": "1", "target": "1", "properties": {"endpoint": "/a", "method": "GET"}},
        ]
        routes, _ = routes_for(nodes)
        self.assertEqual(list(routes), ["/a"])


class GeneratedCodeTests(unittest.TestCase):
    def generate(self, routes):
        import tempfile, os
        out = os.path.join(tempfile.mkdtemp(), "server.js")
        script.generate_server_js(routes, {"cors": False, "logging": False}, output_file=out)
        with open(out, encoding="utf-8") as f:
            return f.read()

    def test_quotes_in_endpoint_and_name_are_escaped(self):
        routes = {'/x"});process.exit(1);//': {"method": "get", "name": 'a"b', "auth": False, "admin": False}}
        code = self.generate(routes)
        self.assertIn('app.get("/x\\"});process.exit(1);//"', code)
        self.assertIn('"Response from a\\"b"', code)

    def test_unknown_method_is_rejected(self):
        routes = {"/x": {"method": "get); evil(", "name": "n", "auth": False, "admin": False}}
        with self.assertRaises(ValueError):
            self.generate(routes)


class DanglingTargetTests(unittest.TestCase):
    def test_missing_target_gives_a_clear_error(self):
        nodes = [{"id": "1", "source": None, "target": "99", "properties": {}}]
        with self.assertRaisesRegex(ValueError, "'99'.*not defined"):
            routes_for(nodes)


if __name__ == "__main__":
    unittest.main()
