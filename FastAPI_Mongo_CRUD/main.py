from fastapi import FastAPI, status, HTTPException
from schemas import employeeEntity, employeeEntityList
from models import EmployeeBase, Employee
from database import db_lifespan
from bson import ObjectId

app: FastAPI = FastAPI(lifespan=db_lifespan)

@app.get("/")
def hello_world():
    return {"Hello": "World"}


@app.post("/employees", status_code=status.HTTP_201_CREATED, response_model=Employee)
async def add_employee(employee: EmployeeBase):
    res = await app.employeeData.employees.insert_one(dict(employee))
    if res.acknowledged:
        return {"id": str(res.inserted_id), "name": employee.name, "email": employee.email}
    else:
        raise HTTPException(status_code=400, detail="Failed to add employee")


@app.get("/employees", response_model=list[Employee])
async def get_employees():
    employees = employeeEntityList(await app.employeeData.employees.find().to_list(length=100))
    return employees


@app.get("/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: str):
    employee = await app.employeeData.employees.find_one({"_id": ObjectId(employee_id)})
    if employee:
        return employeeEntity(employee)
    else:
        raise HTTPException(status_code=404, detail="Employee " + employee_id + " not found")