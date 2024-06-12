from fastapi import FastAPI
from database import db_lifespan
from routers import employee, logs

app: FastAPI = FastAPI(lifespan=db_lifespan)
app.include_router(employee.router)
app.include_router(logs.router)

@app.get("/")
def hello_world():
    return {"Hello": "World"}


# Modification history
"""
_id, ObjectType, Object_name, Activity, Modified_by, Modified_date, 
#, employee, harsha, modified, harsha, 2021-09-15

history_details, history_id, object_name, prev_val, new_val.
_, #, employee, email, h@h.com, b@h.com
_, #, employee, name, john, jon

audit
sort
filter
download - csv, xlsx, pdf, json, print
"""