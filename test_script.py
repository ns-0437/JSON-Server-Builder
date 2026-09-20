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


if __name__ == "__main__":
    unittest.main()
