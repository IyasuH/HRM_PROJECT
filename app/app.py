import os
import sys

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import uvicorn
from routes.admin_route import adminRouter
from routes.employee_route import employeeRouter
from routes.manager_route import managerRouter

from configs import conn

load_dotenv()

app = FastAPI()

@asynccontextmanager
async def lifesapn(app: FastAPI):
    # 
    yield
    # this is to close the connection
    conn.close()

app.include_router(employeeRouter, tags=["employee"],prefix="/employee")
app.include_router(adminRouter, tags=["admin"],prefix="/admin")
app.include_router(managerRouter, tags=["manager"],prefix="/manager")

@app.get("/")
def read_root(request: Request):
    """
    """
    return {"message":"Welcome"}

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=5000)