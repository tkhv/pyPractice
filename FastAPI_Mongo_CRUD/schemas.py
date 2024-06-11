def employeeEntity(employee) -> dict:
    return {
        "id": str(employee["_id"]),
        "name": employee["name"],
        "email": employee["email"],
    }

def employeeEntityList(employees) -> list:
    return [employeeEntity(employee) for employee in employees]