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