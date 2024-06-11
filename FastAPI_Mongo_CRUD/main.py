from fastapi import FastAPI, status, HTTPException
from schemas import employeeEntity, employeeEntityList
from models import Employee, EmployeeInDB
from database import db_lifespan

app: FastAPI = FastAPI(lifespan=db_lifespan)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/employees")
async def get_employees():
    employees = employeeEntityList(await app.employeeData.employees.find().to_list(length=100))
    return employees

@app.post("/employees", status_code=status.HTTP_201_CREATED, response_model=EmployeeInDB)
async def add_employee(employee: Employee):
    res = await app.employeeData.employees.insert_one(dict(employee))
    if res.acknowledged:
        return {"id": str(res.inserted_id), "name": employee.name, "email": employee.email}
    else:
        raise HTTPException(status_code=400, detail="Failed to add employee")
    