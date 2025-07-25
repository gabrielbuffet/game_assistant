from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpStatus
from typing import Dict

from models import Instance

def solve_instance(instance: Instance) -> Dict[str, Dict[str, int]]:
    """
    Solve the instance using linear programming to minimize the total route costs.
    Returns a dictionary with the optimal routes.
    """
    # Create the LP problem
    problem = LpProblem("Optimal_Route_Problem", LpMinimize)

    # Create variables for each route
    route_vars = {
        (village.name, to_village): LpVariable(f"route_{village.name}_{to_village}", lowBound=0, cat='Integer')
        for village in instance.villages for to_village in village.routes
    }

    # Objective function: minimize the total cost of routes
    problem += lpSum(route_vars[village.name, to_village] * village.routes[to_village]
                     for village in instance.villages for to_village in village.routes), "Total_Cost"

    # Constraints: ensure that production is met
    for village in instance.villages:
        problem += lpSum(route_vars[village.name, to_village] for to_village in village.routes) == village.production, \
            f"Production_Constraint_{village.name}"

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