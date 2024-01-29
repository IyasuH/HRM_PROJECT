from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
import mysql.connector
from dotenv import load_dotenv

import os

from models.employee import employeeScehmaRead, employeeSchemaUpdate
from auth import verify_password, get_password_hash
from configs import conn

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

employeeRouter = APIRouter()

# here employee can login RU his data
# can also see leave and salary of him/hersel

def query_employee(username: str):
    cursor = conn.cursor()
    query = "SELECT * FROM employee WHERE username = %s"
    cursor.execute(query, (username,))
    employee = cursor.fetchone()
    cursor.close()
    return employee
    # for some reason thr following try/except is returing error - underling on cursor.close()
    # try:
    #     cursor.execute(query, (username,))
    #     employee = cursor.fetchone
    #     if cursor.rowcount < 1:
    #         return {"err_msg":"employee not found"}
    #     return employee
    # except mysql.connector.Error as error:
    #     return {"err_msg":error}
    # finally:
    #     cursor.close()

def authenticate_employee(username: str, password: str):
        employee: employeeScehmaRead = query_employee(username)
        print("[INFO]: ", employee)
        if verify_password(password, employee[4]):
             return employee
        return None

def create_access_token(data: dict, expires_delta: timedelta):
     to_encode = data.copy()
     expire = datetime.utcnow() + expires_delta
     to_encode.update({"exp": expire})
     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
     return encoded_jwt

def decode_access_token(token: str):
     try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username = payload.get("sub")
        if username is None:
             raise JWTError
        return username
     except JWTError:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
     
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/login")

@employeeRouter.post("/login/")
async def login(form_data: OAuth2PasswordRequestForm=Depends()):
     """
     Employee access
     employee login
     """
     employee = authenticate_employee(form_data.username, form_data.password)
     if not employee:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorect username or password")
     print("[DEBU_INFO]", ACCESS_TOKEN_EXPIRE_MINUTES)
     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
     access_token = create_access_token(
          data={"sub":employee[2]},
          expires_delta=access_token_expires
     )
     return {"access_token":access_token, "token_type": "bearer"}

@employeeRouter.get("/profile/")
async def get_profile(username: str = Depends(decode_access_token)):
     """
     Employee access
     employee profile get
     """
     cursor = conn.cursor()
     query = "SELECT * FROM employee WHERE username = %s"
     try:
        cursor.execute(query, (username,))
        employee = cursor.fetchone()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return employee
     except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
     finally:
        cursor.close()

@employeeRouter.put("/profile/")
async def update_profile(
     employee: employeeSchemaUpdate,
     username: str = Depends(decode_access_token)):
     """
     Employee access
     employee profile update
     """
     employee_id = query_employee(username)[0]
     cursor = conn.cursor()
     query = """UPDATE employee SET 
                manager_id = %s, username = %s, 
                email = %s, first_name = %s,
                last_name = %s, date_of_birth = %s, gender = %s,
                address = %s, contact_number = %s, hire_date = %s,
                dept = %s, role = %s, updated_at = %s WHERE employee_id =%s
            """
     try:
        cursor.execute(query, (
            employee.manager_id, employee.username, employee.email,
            employee.first_name, employee.last_name, employee.date_of_birth,
            employee.gender, employee.address, employee.contact_number,
            employee.hire_date, employee.dept, employee.role, employee.updated_at, employee_id,))
        conn.commit()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message":"Item updated sccessfully"}
     except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
     finally:
        cursor.close()

@employeeRouter.get("/my_leaves/")
async def get_my_leaves(username: str = Depends(decode_access_token)):
     """
     Employee access
     returns my_leaves
     """
     employee_id = query_employee(username)[0]
     cursor = conn.cursor()
     query = "SELECT * FROM leave_tbl WHERE employee_id = %s"
     try:
         cursor.execute(query, (employee_id, ))
         my_leaves = cursor.fetchall()
         if cursor.rowcount < 1:
             raise HTTPException(status_code=404, detail="Item not found")
         return my_leaves
     except mysql.connector.Error as error:
         raise HTTPException(status_code=500, detail=str(error))
     finally:
         cursor.close()

@employeeRouter.get("/my_salaries/")
async def get_my_salaries(username: str = Depends(decode_access_token)):
     """
     Employee access
     returns my_salary datat
     """
     employee_id = query_employee(username)[0]
     cursor = conn.cursor()
     query = "SELECT * FROM salary WHERE employee_id = %s"
     try:
         cursor.execute(query, (employee_id, ))
         my_salaries = cursor.fetchall()
         if cursor.rowcount < 1:
             raise HTTPException(status_code=404, detail="Item not found")
         return my_salaries
     except mysql.connector.Error as error:
         raise HTTPException(status_code=500, detail=str(error))
     finally:
         cursor.close()
