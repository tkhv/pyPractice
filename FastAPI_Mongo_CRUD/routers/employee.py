from fastapi import status, HTTPException, APIRouter, Request
from fastapi.responses import StreamingResponse
from schemas import employeeEntity, employeeEntityList
from models import EmployeeBase, Employee
from bson import ObjectId
import pandas as pd

router = APIRouter()

# Returns bonus percentage and total pay
def bonus_calc(salary: float, performance_rating: int) -> {int, float}:
    # bonus only for performance rating > 2
    # Base bonuses: 10% for <100k, 15% for 100k-200k, 20% for >200k
    # Performance bonus: +5% for rating 4, +10% for rating 5
    if performance_rating < 3:
        return 0, salary
    
    if salary < 100000:
        bonus = 10
    elif salary < 200000:
        bonus = 15
    else:
        bonus = 20

    if performance_rating == 4:
        bonus += 5
    elif performance_rating == 5:
        bonus += 10

    total_pay = salary + (salary * bonus / 100)
    return bonus, total_pay


@router.post("/employees", status_code=status.HTTP_201_CREATED, response_model=Employee)
async def add_employee(employeeBase: EmployeeBase, request: Request):
    bonus = bonus_calc(employeeBase.salary, employeeBase.performance_rating)
    employee = {
        "name": employeeBase.name,
        "email": employeeBase.email,
        "phone": employeeBase.phone,
        "hire_date": employeeBase.hire_date,
        "salary": employeeBase.salary,
        "performance_rating": employeeBase.performance_rating,
        "bonus_percent": bonus[0],
        "total_pay": bonus[1]
    }

    res = await request.app.employeeData.employees.insert_one((employee))
    if res.acknowledged:
        employee["id"] = str(res.inserted_id)
        return employee
    else:
        raise HTTPException(status_code=400, detail="Failed to add employee")


@router.get("/employees", response_model=list[Employee])
async def get_employees(request: Request):
    employees = employeeEntityList(await request.app.employeeData.employees.find().to_list(length=100))
    return employees


@router.get("/employees/csv")
async def get_employees_as_CSV(request: Request):
    employees = await get_employees(request=request)
    df = pd.DataFrame(employees)
    csv = df.to_csv(index=False)
    print(csv)
    return StreamingResponse(content=csv, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=employees.csv"})


@router.get("/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: str, request: Request):
    employee = await request.app.employeeData.employees.find_one({"_id": ObjectId(employee_id)})
    if employee:
        return employeeEntity(employee)
    else:
        raise HTTPException(status_code=404, detail="Employee " + employee_id + " not found")


@router.post("/employees/{employee_id}", response_model=Employee)
async def update_employee(employee: EmployeeBase, employee_id: str, request: Request):
    res = await request.app.employeeData.employees.find_one_and_update(
        {"_id": ObjectId(employee_id)}, {"$set": dict(employee)}, return_document=True
    )
    if res:
        return employeeEntity(res)
    else:
        raise HTTPException(status_code=404, detail="Employee " + employee_id + " not found")


@router.delete("/employees/{employee_id}", response_model=Employee)
async def delete_employee(employee_id: str, request: Request):
    res = await request.app.employeeData.employees.find_one_and_delete({"_id": ObjectId(employee_id)})
    if res:
        return employeeEntity(res)
    else:
        raise HTTPException(status_code=404, detail="Employee " + employee_id + " not found")
