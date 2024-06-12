from fastapi import status, HTTPException, APIRouter, Request
from models import Employee, EmployeeMod, Changelog, LogEntry
from datetime import datetime
from bson import ObjectId
import pandas as pd

async def post_log(request: Request, employeeMod: EmployeeMod, employee: Employee, num_fields_changed: int):

  changelog = {
    "timestamp": datetime.now(),
    "target_id": employeeMod.target_id,
    "target_name": employee['name'],
    "source_id": employeeMod.source_id,
    "num_fields_changed": num_fields_changed
  }
  
  res = await request.app.employeeData.changelogs.insert_one(changelog)
  if not res:
    raise HTTPException(status_code=500, detail="Error creating changelog")
  
  for key, value in employeeMod.dict().items():
    if value and key != "target_id" and key != "source_id":
      log_entry: LogEntry = {
        "changelog_id": str(res.inserted_id),
        "field_name": key,
        "prev_val": employee[key],
        "new_val": value
      }
      res = await request.app.employeeData.log_entries.insert_one(log_entry)
      if not res:
        raise HTTPException(status_code=500, detail="Error creating changelog entry")
