from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpStatus, PULP_CBC_CMD
from typing import Optional

from game_assistant.models import Instance

def solve_instance(instance: Instance, forbidden_routes: Optional[set] = set()) -> dict[str, dict[str, int]]:
    """
    Solve the instance using linear programming to find the optimal routes between villages.
    Args:
        instance (Instance): The instance containing villages and their routes.
        forbidden_routes (set): A set of tuples representing forbidden routes.
    Returns:
        Dict[str, Dict[str, int]]: A dictionary where keys are village names and values
        are dictionaries of routes with amounts.
    Raises:
        ValueError: If the instance has no villages or routes.
    """
    if not instance.villages:
        raise ValueError("Instance has no villages.")
    
    n = len(instance.villages)

    allowed_routes = [
        (i, j) for i in range(n) for j in range(n)
        if i != j and (instance.villages[i].name, instance.villages[j].name) not in forbidden_routes
    ]

    if not allowed_routes:
        raise ValueError("No allowed routes available after applying forbidden routes.")
    
    total_prod = sum(village.production for village in instance.villages)
    if total_prod < 0:
        raise ValueError("Total production is negative, cannot solve instance.")
    
    problem = LpProblem("VillageRouting", LpMinimize)

    x = {
        (i, j): LpVariable(f"x_{i}_{j}", lowBound=0, cat='Integer')
        for i, j in allowed_routes
    }
    
    problem += lpSum(x[i, j] for i, j in allowed_routes), "Total_Routes"

    for i, village in enumerate(instance.villages):
        if village.production >= 0:
            problem += lpSum(x[i, j] for j in range(n) if (i, j) in allowed_routes) <= village.production, f"Production_Constraint_{i}"
        else:
            problem += lpSum(x[j, i] for j in range(n) if (j, i) in allowed_routes) >= -village.production, f"Consumption_Constraint_{i}"

    for (i, j), var in x.items():
        var.setInitialValue(instance.routes_matrix[i, j])
    
    solver = PULP_CBC_CMD(msg=False, warmStart=True)
    problem.solve(solver)

    status = LpStatus[problem.status]
    if status != 'Optimal':
        raise ValueError(f"Problem status is not optimal: {status}")
    
    result = {}
    for i, village in enumerate(instance.villages):
        result[village.name] = {}
        for j in range(n):
            if (i, j) in x and x[i, j].varValue > 0:
                target_village = instance.villages[j].name
                result[village.name][target_village] = int(x[i, j].varValue)

    return result
