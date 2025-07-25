import unittest
from game_assistant.models import Village, Instance

class TestVillage(unittest.TestCase):
    def setUp(self):
        self.village = Village(name="TestVillage", production=100, routes={"VillageA": 50, "VillageB": 30})

    def test_add_route(self):
        self.village.add_route("VillageC", 20)
        self.assertIn("VillageC", self.village.routes)
        self.assertEqual(self.village.routes["VillageC"], 20)

    def test_update_route(self):
        self.village.update_route("VillageA", 60)
        self.assertEqual(self.village.routes["VillageA"], 60)

    def test_remove_route(self):
        self.village.remove_route("VillageB")
        self.assertNotIn("VillageB", self.village.routes)
    
    def test_to_dict(self):
        expected_dict = {
            "name": "TestVillage",
            "production": 100,
            "routes": {"VillageA": 50, "VillageB": 30}
        }
        self.assertEqual(self.village.to_dict(), expected_dict)

    def test_from_dict(self):
        village_data = {
            "name": "TestVillage",
            "production": 100,
            "routes": {"VillageA": 50, "VillageB": 30}
        }
        village = Village.from_dict(village_data)
        self.assertEqual(village.name, "TestVillage")
        self.assertEqual(village.production, 100)
        self.assertEqual(village.routes, {"VillageA": 50, "VillageB": 30})
    
class TestInstance(unittest.TestCase):
    def setUp(self):
        self.village1 = Village(name="VillageA", production=100)
        self.village2 = Village(name="VillageB", production=150, routes={"VillageA": 50})
        self.instance = Instance(villages=[self.village1, self.village2])

    def test_add_route(self):
        self.instance.add_route("VillageA", "VillageB", 30)
        self.assertIn("VillageB", self.village1.routes)
        self.assertEqual(self.village1.routes["VillageB"], 30)

    def test_update_route(self):
        self.instance.update_route("VillageA", "VillageB", 60)
        self.assertEqual(self.village1.routes["VillageB"], 60)

    def test_remove_route(self):
        self.instance.remove_route("VillageB", "VillageA")
        self.assertNotIn("VillageA", self.village2.routes)

    def test_to_dict(self):
        expected_dict = {
            "villages": [self.village1.to_dict(), self.village2.to_dict()]
        }
        self.assertEqual(self.instance.to_dict(), expected_dict)

    def test_from_dict(self):
        instance_data = {
            "villages": [self.village1.to_dict(), self.village2.to_dict()]
        }
        instance = Instance.from_dict(instance_data)
        self.assertEqual(len(instance.villages), 2)
        self.assertEqual(instance.villages[0].name, "VillageA")
        self.assertEqual(instance.villages[1].name, "VillageB")

    def test_load_instance_from_file(self):
        # Assuming the file 'test_instance.json' exists with valid data
        instance = Instance.load_instance_from_file('test_instance.json')
        self.assertIsInstance(instance, Instance)
        self.assertGreater(len(instance.villages), 0)

    def test_save_instance_to_file(self):
        # Save the instance to a file and check if it can be loaded back
        Instance.save_instance_to_file(self.instance, 'test_instance.json')
        loaded_instance = Instance.load_instance_from_file('test_instance.json')
        self.assertEqual(loaded_instance.to_dict(), self.instance.to_dict())

if __name__ == '__main__':
    unittest.main()
