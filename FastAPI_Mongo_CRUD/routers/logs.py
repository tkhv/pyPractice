from fastapi import status, HTTPException, APIRouter, Request
from models import Employee, EmployeeMod, Changelog, LogEntry, FullLog
from schemas import changelogEntity, changelogEntityList, logEntryEntity, logEntryEntityList
from datetime import datetime
from bson import ObjectId
import pandas as pd

router = APIRouter()

async def post_log(request: Request, employeeMod: EmployeeMod, employee: Employee, num_fields_changed: int):
  print("employeeMod: ", employeeMod)
  changelog = {
    "timestamp": datetime.now(),
    "target_id": employeeMod.target_id,
    "target_name": employee['name'],
    "source_id": employeeMod.source_id,
    "num_fields_changed": num_fields_changed
  }
  
  changeLogRes = await request.app.employeeData.changelogs.insert_one(changelog)
  if not changeLogRes:
    raise HTTPException(status_code=500, detail="Error creating changelog")
  
  for key, value in employeeMod.dict().items():
    if value and key != "target_id" and key != "source_id":
      log_entry: LogEntry = {
        "changelog_id": str(changeLogRes.inserted_id),
        "field_name": key,
        "prev_val": employee[key],
        "new_val": value
      }
      res = await request.app.employeeData.log_entries.insert_one(log_entry)
      if not res:
        raise HTTPException(status_code=500, detail="Error creating changelog entry")


@router.post("/changelogs/{employee_id}/", response_model=list[Changelog])
async def get_changelogs(employee_id: str, request: Request):
  changelogs = changelogEntityList(await request.app.employeeData.changelogs.find({"target_id": employee_id}).to_list(length=100))
  return changelogs

@router.get("/changelogs/{changelog_id}", response_model=list[LogEntry])
async def get_changelog_entries(changelog_id: str, request: Request):
  changelog = logEntryEntityList(await request.app.employeeData.log_entries.find({"changelog_id": changelog_id}).to_list(length=100))
  return changelog


@router.get("/changelogs/{employee_id}/all", response_model=list[FullLog])
async def get_full_logs(employee_id: str, request: Request):
  changelogs = await get_changelogs(employee_id, request)
  full_logs = []
  for changelog in changelogs:
    log_entries = await get_changelog_entries(changelog['id'], request)
    full_log = {
      "id": changelog['id'],
      "timestamp": changelog['timestamp'],
      "target_id": changelog['target_id'],
      "target_name": changelog['target_name'],
      "source_id": changelog['source_id'],
      "num_fields_changed": changelog['num_fields_changed'],
      "log_entries": log_entries
    }
    full_logs.append(full_log)
  return full_logs
