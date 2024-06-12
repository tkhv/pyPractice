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

def changelogEntity(changelog) -> dict:
    return {
        "id": str(changelog["_id"]),
        "timestamp": changelog["timestamp"],
        "target_id": changelog["target_id"],
        "target_name": changelog["target_name"],
        "source_id": changelog["source_id"],
        "num_fields_changed": changelog["num_fields_changed"]
    }

def changelogEntityList(changelogs) -> list:
    return [changelogEntity(changelog) for changelog in changelogs]

def logEntryEntity(log_entry) -> dict:
    return {
        "id": str(log_entry["_id"]),
        "changelog_id": log_entry["changelog_id"],
        "field_name": log_entry["field_name"],
        "prev_val": log_entry["prev_val"],
        "new_val": log_entry["new_val"]
    }

def logEntryEntityList(log_entries) -> list:
    return [logEntryEntity(log_entry) for log_entry in log_entries]