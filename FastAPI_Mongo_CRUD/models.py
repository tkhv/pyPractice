from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EmployeeBase(BaseModel):
    name: str
    email: str
    phone: int
    hire_date: datetime
    salary: float
    performance_rating: int


class Employee(EmployeeBase):
    id: str
    bonus_percent: int
    total_pay: float


class EmployeeMod(BaseModel):
    target_id: str
    source_id: str
    email: Optional[str] = None
    phone: Optional[int] = None
    salary: Optional[float] = None
    performance_rating: Optional[int] = None


class Changelog(BaseModel):
    id: Optional[str] = None
    timestamp: datetime
    target_id: str
    target_name: str
    source_id: str
    num_fields_changed: int


class LogEntry(BaseModel):
    id: Optional[str] = None
    changelog_id: str
    field_name: str
    prev_val: Optional[str | float | int | bool]
    new_val: Optional[str | float | int | bool]

