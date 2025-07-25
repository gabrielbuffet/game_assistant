from typing import Optional
import json
import os
import numpy as np

class Village:
    def __init__(self, name: str, production: int, routes: Optional[dict[str,int]] = {}):
        self.name = name
        self.production = production
        self.routes = routes

    def update_route(self, target_village: str, amount: int) -> None:
        if target_village not in self.routes:
            raise ValueError(f"Target village '{target_village}' does not exist in routes. Please add it first using add_route.")
        if amount < 0:
            raise ValueError("Amount must be non-negative.")
        self.routes[target_village] = amount

    def add_route(self, target_village: str, amount: int) -> None:
        if target_village in self.routes:
            raise ValueError(f"Route to '{target_village}' already exists. Use update_route to change the amount.")
        if amount < 0:
            raise ValueError("Amount must be non-negative.")
        
        self.routes[target_village] = amount
    def remove_route(self, target_village: str) -> None:
        if target_village not in self.routes:
            raise ValueError(f"Route to '{target_village}' does not exist.")
        del self.routes[target_village]

    def __str__(self) -> str:
        return f"Village(name={self.name}, production={self.production}, routes={self.routes})"

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "production": self.production,
            "routes": self.routes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Village':
        return cls(
            name=data.get("name", ""),
            production=data.get("production", 0),
            routes=data.get("routes", {})
        )

    @staticmethod
    def load_villages_from_file(file_path: str) -> list['Village']:
        villages = []
        if not os.path.exists(file_path):
            return villages
        
        with open(file_path, 'r') as file:
            data = json.load(file)
            for village_data in data.get("villages", []):
                village = Village.from_dict(village_data)
                villages.append(village)
        
        return villages
    
    @staticmethod
    def save_villages_to_file(villages: list['Village'], file_path: str) -> None:
        data = {
            "villages": [village.to_dict() for village in villages]
        }
        
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

class Instance:
    def __init__(self, villages: Optional[list[Village]] = None):
        self.villages = villages if villages is not None else []
        self.villages_map = {village.name: village for village in self.villages}
        self.routes_matrix = self._calculate_routes_matrix()

    def _calculate_routes_matrix(self) -> np.ndarray:
        size = len(self.villages)
        matrix = np.zeros((size, size), dtype=int)
        
        for i, village in enumerate(self.villages):
            for route_name, amount in village.routes.items():
                if route_name in self.villages_map:
                    j = self.villages.index(self.villages_map[route_name])
                    matrix[i][j] = amount

        return matrix
 
    def add_village(self, village: Village) -> None:
        if village.name in self.villages_map:
            raise ValueError(f"Village '{village.name}' already exists.")
        self.villages.append(village)
        self.villages_map[village.name] = village
        self.routes_matrix = self._calculate_routes_matrix()

    def get_village(self, name: str) -> Optional[Village]:
        return self.villages_map.get(name)

    def remove_village(self, name: str) -> None:
        village = self.get_village(name)
        if not village:
            raise ValueError(f"Village '{name}' does not exist.")
        self.villages.remove(village)
        del self.villages_map[name]
        self.routes_matrix = self._calculate_routes_matrix()

    def update_village(self, name: str, production: int, routes: Optional[dict[str,int]] = None) -> None:
        village = self.get_village(name)
        if not village:
            raise ValueError(f"Village '{name}' does not exist.")
        
        village.production = production
        if routes is not None:
            village.routes = routes
        self.routes_matrix = self._calculate_routes_matrix()
    
    def add_route(self, from_village: str, to_village: str, amount: int) -> None:
        village = self.get_village(from_village)
        if not village:
            raise ValueError(f"Village '{from_village}' does not exist, please add it first.")
        if to_village not in self.villages_map:
            raise ValueError(f"Target village '{to_village}' does not exist, please add it first.")
        village.add_route(to_village, amount)
        self.routes_matrix = self._calculate_routes_matrix()

    def update_route(self, from_village: str, to_village: str, amount: int) -> None:
        village = self.get_village(from_village)
        if not village:
            raise ValueError(f"Village '{from_village}' does not exist.")
        if to_village not in village.routes:
            raise ValueError(f"Route to '{to_village}' does not exist in village '{from_village}'.")
        village.update_route(to_village, amount)
        self.routes_matrix = self._calculate_routes_matrix()

    def remove_route(self, from_village: str, to_village: str) -> None:
        village = self.get_village(from_village)
        if not village:
            raise ValueError(f"Village '{from_village}' does not exist.")
        if to_village not in village.routes:
            raise ValueError(f"Route to '{to_village}' does not exist in village '{from_village}'.")
        village.remove_route(to_village)
        self.routes_matrix = self._calculate_routes_matrix()

    def __str__(self) -> str:
        return f"Instance(villages={self.villages})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def to_dict(self) -> dict:
        return {
            "villages": [village.to_dict() for village in self.villages]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Instance':
        villages = [Village.from_dict(village_data) for village_data in data.get("villages", [])]
        return cls(villages=villages)
    
    @staticmethod
    def load_instance_from_file(file_path: str) -> 'Instance':
        if not os.path.exists(file_path):
            return Instance()
        
        with open(file_path, 'r') as file:
            data = json.load(file)
            return Instance.from_dict(data)
        
    @staticmethod
    def save_instance_to_file(instance: 'Instance', file_path: str) -> None:
        data = instance.to_dict()
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

# Example usage:
# village1 = Village(name="VillageA", production=100)
# village2 = Village(name="VillageB", production=150, routes={"VillageA": 50})
# instance = Instance(villages=[village1, village2])
# instance.add_route("VillageA", "VillageB", 30)
# print(instance.routes_matrix)
# Village.save_villages_to_file(instance.villages, "villages.json")
# loaded_villages = Village.load_villages_from_file("villages.json")
# print(loaded_villages)
# instance.save_instance_to_file("instance.json")
# loaded_instance = Instance.load_instance_from_file("instance.json")
# print(loaded_instance)