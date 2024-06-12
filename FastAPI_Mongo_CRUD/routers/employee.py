from fastapi import status, HTTPException, APIRouter, Request
from fastapi.responses import StreamingResponse
from schemas import employeeEntity, employeeEntityList
from models import EmployeeBase, Employee, EmployeeMod
from bson import ObjectId
import pandas as pd
from routers.logs import post_log

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
async def update_employee(employeeMod: EmployeeMod, request: Request):
    employee = employeeEntity(await request.app.employeeData.employees.find_one({"_id": ObjectId(employeeMod.target_id)}))
    if not employee:
        raise HTTPException(status_code=404, detail="Employee " + employeeMod.target_id + " not found")
    original_employee = employee.copy()

    num_fields_changed = 0
    for key, value in employeeMod.dict().items():
        if value and key != "target_id" and key != "source_id":
            employee[key] = value
            num_fields_changed += 1
    
    if num_fields_changed == 0:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    await post_log(request, employeeMod, original_employee, num_fields_changed)

    bonus = bonus_calc(employee["salary"], employee["performance_rating"])
    employee["bonus_percent"] = bonus[0]
    employee["total_pay"] = bonus[1]
    
    print(employee)

    res = await request.app.employeeData.employees.find_one_and_replace({"_id": ObjectId(employeeMod.target_id)}, employee)
    if res:
        return employee
    else:
        raise HTTPException(status_code=404, detail="Employee " + employeeMod.target_id + " not found")


@router.delete("/employees/{employee_id}", response_model=Employee)
async def delete_employee(employee_id: str, request: Request):
    res = await request.app.employeeData.employees.find_one_and_delete({"_id": ObjectId(employee_id)})
    if res:
        return employeeEntity(res)
    else:
        raise HTTPException(status_code=404, detail="Employee " + employee_id + " not found")

