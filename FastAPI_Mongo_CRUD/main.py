from fastapi import FastAPI, status, HTTPException
from fastapi.responses import StreamingResponse
from schemas import employeeEntity, employeeEntityList
from models import EmployeeBase, Employee
from database import db_lifespan
from bson import ObjectId
import pandas as pd

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

@app.get("/employees/csv")
async def get_employees_as_CSV():
    employees = await get_employees()
    df = pd.DataFrame(employees)
    csv = df.to_csv(index=False)
    print(csv)
    return StreamingResponse(content=csv, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=employees.csv"})
    

@app.get("/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: str):
    employee = await app.employeeData.employees.find_one({"_id": ObjectId(employee_id)})
    if employee:
        return employeeEntity(employee)
    else:
        raise HTTPException(status_code=404, detail="Employee " + employee_id + " not found")


@app.post("/employees/{employee_id}", response_model=Employee)
async def update_employee(employee: EmployeeBase, employee_id: str):
    res = await app.employeeData.employees.find_one_and_update(
        {"_id": ObjectId(employee_id)}, {"$set": dict(employee)}, return_document=True
    )
    if res:
        return employeeEntity(res)
    else:
        raise HTTPException(status_code=404, detail="Employee " + employee_id + " not found")


@app.delete("/employees/{employee_id}", response_model=Employee)
async def delete_employee(employee_id: str):
    res = await app.employeeData.employees.find_one_and_delete({"_id": ObjectId(employee_id)})
    if res:
        return employeeEntity(res)
    else:
        raise HTTPException(status_code=404, detail="Employee " + employee_id + " not found")