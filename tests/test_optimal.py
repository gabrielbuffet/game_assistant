import unittest
from game_assistant.optimal import solve_instance
from game_assistant.models import Village, Instance

class TestOptimalSolver(unittest.TestCase):
    def setUp(self):
        self.instance = Instance()
        self.instance.add_village(Village(name="VillageA", production=100))
        self.instance.add_village(Village(name="VillageB", production=50))
        self.instance.add_village(Village(name="VillageC", production=-30))
        self.instance.add_route("VillageA", "VillageB", 20)
        self.instance.add_route("VillageB", "VillageC", 10)

    def test_solve_instance(self):
        solution = solve_instance(self.instance, forbidden_routes=set())
        self.assertIn("VillageA", solution)
        self.assertIn("VillageB", solution)
        self.assertIn("VillageC", solution)

    def test_no_villages(self):
        empty_instance = Instance()
        with self.assertRaises(ValueError):
            solve_instance(empty_instance, forbidden_routes=set())

    def test_forbidden_routes(self):
        forbidden_routes = {("VillageA", "VillageC")}
        solution = solve_instance(self.instance, forbidden_routes=forbidden_routes)
        self.assertNotIn("VillageC", solution["VillageA"])

if __name__ == '__main__':
    unittest.main()
