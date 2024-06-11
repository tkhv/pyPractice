from pydantic import BaseModel

class Employee(BaseModel):
    name: str
    email: str

class EmployeeInDB(Employee):
    id: str
