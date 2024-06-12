def employeeEntity(employee) -> dict:
    return {
        "id": str(employee["_id"]),
        "name": employee["name"],
        "email": employee["email"],
        "phone": employee["phone"],
        "hire_date": employee["hire_date"],
        "salary": employee["salary"],
        "performance_rating": employee["performance_rating"],
        "bonus_percent": employee["bonus_percent"],
        "total_pay": employee["total_pay"],
    }

def employeeEntityList(employees) -> list:
    return [employeeEntity(employee) for employee in employees]