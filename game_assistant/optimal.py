from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpStatus
from typing import Dict

from game_assistant.models import Instance

def solve_instance(instance: Instance) -> Dict[str, Dict[str, int]]:
    """
    Solve the instance using linear programming to find the optimal routes between villages.
    Args:
        instance (Instance): The instance containing villages and their routes.
    Returns:
        Dict[str, Dict[str, int]]: A dictionary where keys are village names and values
        are dictionaries of routes with amounts.
    Raises:
        ValueError: If the instance has no villages or routes.
    """
    if not instance.villages:
        raise ValueError("The instance has no villages.")
    if not any(village.routes for village in instance.villages):
        raise ValueError("The instance has no routes between villages.")
    
    # Create the LP problem
    problem = LpProblem("Optimal_Route_Problem", LpMinimize)

    # Create variables for each route
    route_vars = {
        (village.name, to_village): LpVariable(f"route_{village.name}_{to_village}", lowBound=0, cat='Integer')
        for village in instance.villages for to_village in village.routes
    }

    # Objective function: minimize the total cost of routes
    problem += lpSum(route_vars[(village.name, to_village)] * village.routes[to_village]
                     for village in instance.villages for to_village in village.routes), "Total_Cost"

    # Constraints: ensure that the net cereal balance is non-negative
    for village in instance.villages:
        outgoing = lpSum(route_vars[(village.name, to_village)] for to_village in village.routes)
        incoming = lpSum(route_vars[(other_village.name, village.name)] for other_village in instance.villages
                         if village.name in other_village.routes)
        problem += village.production - outgoing + incoming >= 0, f"Production_Constraint_{village.name}"

    # Solve the problem
    problem.solve()

    # Check the status of the solution
    if LpStatus[problem.status] != 'Optimal':
        raise ValueError("No optimal solution found.")

    # Prepare the result
    result = {village.name: {} for village in instance.villages}
    for (from_village, to_village), var in route_vars.items():
        if var.varValue > 0:
            result[from_village][to_village] = int(var.varValue)

    return result