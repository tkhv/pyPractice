from fastapi import status, HTTPException, APIRouter, Request
from fastapi.responses import StreamingResponse, FileResponse
from schemas import employeeEntity, employeeEntityList
from models import EmployeeBase, Employee, EmployeeMod
from bson import ObjectId
import pandas as pd
from routers.logs import post_log
from typing import Optional
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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
        return Employee(employee)
    else:
        raise HTTPException(status_code=400, detail="Failed to add employee")


@router.get("/employees")
async def get_employees(request: Request, sort_by: Optional[str] = None, salary_gte: Optional[float] = None, salary_lte: Optional[float] = None, performance_rating_gte: Optional[int] = None, performance_rating_lte: Optional[int] = None, response_file_type: Optional[str] = None):
    if sort_by is not None and sort_by not in Employee.model_fields:
        raise HTTPException(status_code=400, detail="Invalid sort_by field")

    employees = employeeEntityList(await request.app.employeeData.employees.find().to_list(length=100))

    if salary_gte is not None:
        employees = [employee for employee in employees if employee["salary"] >= salary_gte]
    if salary_lte is not None:
        employees = [employee for employee in employees if employee["salary"] <= salary_lte]
    if performance_rating_gte is not None:
        employees = [employee for employee in employees if employee["performance_rating"] >= performance_rating_gte]
    if performance_rating_lte is not None:
        employees = [employee for employee in employees if employee["performance_rating"] <= performance_rating_lte]

    if sort_by is not None:
        # Sort in descending order
        employees = sorted(employees, key=lambda x: x[sort_by], reverse=True)

    if response_file_type == "csv":
        df = pd.DataFrame(employees)
        csv = df.to_csv(index=False)
        return StreamingResponse(content=csv, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=employees.csv"})
    elif response_file_type == "xlsx":
        df = pd.DataFrame(employees)
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Employees')
        buffer.seek(0)
        return StreamingResponse(
            content=buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=employees.xlsx"}
        )
    elif response_file_type == "pdf":
        df = pd.DataFrame(employees)
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Adding the data to the PDF
        c.drawString(30, height - 40, "Employees Report")
        c.drawString(30, height - 60, f"Total Employees: {len(employees)}")
        
        # Define the start position
        start_y = height - 100
        line_height = 15

        for i, row in df.iterrows():
            if start_y - line_height < 40:  # Check if we need to add a new page
                c.showPage()
                start_y = height - 40
            text = ', '.join([f"{col}: {row[col]}" for col in df.columns])
            c.drawString(30, start_y, text)
            start_y -= line_height

        c.showPage()
        c.save()
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=employees.pdf"}
        )

    return list[Employee](employees)

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

