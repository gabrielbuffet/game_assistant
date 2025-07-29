from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpStatus
from typing import Optional

from game_assistant.models import Instance

def solve_instance(instance: Instance, forbidden_routes: Optional[set] = set()) -> dict[str, dict[str, int]]:
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

    # for i, village in enumerate(instance.villages):
    #     if village.production >= 0:
    #         problem += lpSum(x[i, j] for j in range(n) if (i, j) in allowed_routes) <= village.production, f"Production_Constraint_{i}"
    #     else:
    #         problem += lpSum(x[j, i] for j in range(n) if (j, i) in allowed_routes) >= -village.production, f"Consumption_Constraint_{i}"

    for i, village in enumerate(instance.villages):
        inflow = lpSum(x[j, i] for j in range(n) if (j, i) in allowed_routes)
        outflow = lpSum(x[i, j] for j in range(n) if (i, j) in allowed_routes)
        if village.production > 0:
            problem += outflow <= village.production, f"Production_Constraint_{i}"
            problem += inflow == 0, f"Inflows_Zero_{i}"
        elif village.production < 0:
            problem += inflow == -village.production, f"Consumption_Constraint_{i}"
            problem += outflow == 0, f"Outflows_Zero_{i}"
        else:
            problem += inflow == outflow, f"Balance_Constraint_{i}"
        



    # for (i, j), var in x.items():
    #     var.setInitialValue(instance.routes_matrix[i, j])
    
    # solver = PULP_CBC_CMD(msg=False, warmStart=True)
    # problem.solve(solver)
    problem.solve()
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
