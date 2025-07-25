import unittest
from game_assistant.optimal import solve_instance
from game_assistant.models import Village, Instance

class TestOptimalSolver(unittest.TestCase):
    def setUp(self):
        # Create a simple instance with villages and routes
        self.village1 = Village(name="VillageA", production=100, routes={"VillageB": 50, "VillageC": 30})
        self.village2 = Village(name="VillageB", production=150, routes={"VillageA": 50})
        self.village3 = Village(name="VillageC", production=-50, routes={})
        self.instance = Instance(villages=[self.village1, self.village2, self.village3])

    def test_solve_instance(self):
        result = solve_instance(self.instance)
        self.assertIsInstance(result, dict)
        self.assertIn("VillageA", result)
        self.assertIn("VillageB", result)
        self.assertIn("VillageC", result)
        self.assertGreaterEqual(len(result["VillageA"]), 0)
        self.assertGreaterEqual(len(result["VillageB"]), 0)
        self.assertGreaterEqual(len(result["VillageC"]), 0)
        print(result)

    def test_no_routes(self):
        # Create an instance with no routes
        empty_instance = Instance(villages=[Village(name="VillageD", production=100)])
        with self.assertRaises(ValueError):
            solve_instance(empty_instance)
    
    def test_no_villages(self):
        # Create an instance with no villages
        empty_instance = Instance(villages=[])
        with self.assertRaises(ValueError):
            solve_instance(empty_instance)


if __name__ == '__main__':
    unittest.main()
