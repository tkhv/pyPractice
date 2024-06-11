from pydantic import BaseModel

class EmployeeBase(BaseModel):
    name: str
    email: str

class Employee(EmployeeBase):
    id: str
