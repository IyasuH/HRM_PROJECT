from models.salary import salarySchemaRead, salarySchemaUpdate, salarySchemaWrite
from models.leave_tbl import leaveSchemaRead, leaveSchemaUpdate, leaveSchemaWrite
from models.admin import adminScehmaRead, adminScehmaWrite, adminSchemaUpdate
from models.project import projectSchemaRead, projectSchemaUpdate, projectSchemaWrite
from models.employee import employeeScehmaWrite, employeeScehmaRead, employeeSchemaUpdate
from models.manager import managerScehmaRead, managerScehmaWriter
from configs import conn
from auth import verify_password, get_password_hash
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt


from fastapi import APIRouter, HTTPException, Depends, Path, status
from typing import Annotated, Union
import bcrypt
import mysql.connector

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

adminRouter = APIRouter()

def query_admin(username: str):
    # for authetication and authorization purposes 
    cursor = conn.cursor()
    query = "SELECT * FROM admin WHERE username = %s"
    cursor.execute(query, (username,))
    admin = cursor.fetchone()
    cursor.close()
    return admin

def authenticate_manager(username: str, password: str):
        admin: adminScehmaRead = query_admin(username)
        if verify_password(password, admin[3]):
             return admin
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

@adminRouter.post("/login/")
async def login(form_data: OAuth2PasswordRequestForm=Depends()):
     """
     Admin access
     admin login
     """
     admin = authenticate_manager(form_data.username, form_data.password)
     if not admin:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorect username or password")
     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
     access_token = create_access_token(
          data={"sub":admin[1]},
          expires_delta=access_token_expires
     )
     return {'access_token':access_token, "token_type": "bearer"}


####EMPLOYEE-LCRUD#######

@adminRouter.get("/")
async def get_emplyees(response_model=employeeScehmaRead):
    """
    Admin access only
    list all employees
    """
    cursor = conn.cursor()
    query = "SELECT * FROM employee"
    cursor.execute(query)
    employees = cursor.fetchall()
    cursor.close()
    return employees

@adminRouter.post("/new_employee/")
async def create_employee(employee: employeeScehmaWrite):
    """
    Admin access only
    Create new employee
    """
    cursor = conn.cursor()
    hashed_password = get_password_hash(employee.password)
    query = """INSERT INTO employee
    (
        manager_id, username, email, password, first_name, last_name, date_of_birth,
        gender, address, contact_number, hire_date, dept, role, created_at, updated_at
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, 
                   (employee.manager_id, employee.username, employee.email, hashed_password, employee.first_name, employee.last_name, employee.date_of_birth, employee.gender, employee.address, employee.contact_number, employee.hire_date, employee.dept, employee.role, employee.created_at, employee.updated_at)
                   )
    conn.commit()
    cursor.close()
    return {'message':'data created'}

@adminRouter.get("/employee/{employee_id}")
async def get_emplyee(employee_id: Annotated[int, Path(title="Book ID", ge=1)]):
    """
    Admin access only
    read one employee
    """
    cursor = conn.cursor()
    query = "SELECT * FROM employee WHERE employee_id = %s"
    try:
        cursor.execute(query, (employee_id,))
        employee = cursor.fetchone()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return employee
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()

@adminRouter.put("/employee/{employee_id}")
async def update_emplyee(
    employee_id: Annotated[int, Path(title="Employee ID", ge=1)],
    employee: employeeSchemaUpdate):
    """
    Admin access only
    update employee
    """
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

@adminRouter.delete("/employee/{employee_id}")
async def delete_emplyee(employee_id: int):
    """
    Admin access only
    delete one employee
    """
    cursor = conn.cursor()
    query = "DELETE FROM employee WHERE employee_id = %s"
    try:
        cursor.execute(query, (employee_id,))
        conn.commit()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message":"Item is deleted"}
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()


####MANGER-LCRUD#######

@adminRouter.get("/managers/")
async def get_managers(response_model=managerScehmaRead):
    """
    Admin access only
    list all managers
    """
    cursor = conn.cursor()
    query = "SELECT * FROM manager"
    cursor.execute(query)
    managers = cursor.fetchall()
    cursor.close()
    return managers

@adminRouter.post("/new_manager/")
async def create_manger(manager: managerScehmaWriter):
    """
    Admin access only
    Create new manager
    """
    cursor = conn.cursor()
    hashed_password = get_password_hash(manager.password)
    print("[INFO]: ", manager.created_at)
    query = """INSERT INTO manager
    (username, email, password, created_at, updated_at)
    VALUES(%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (manager.username, manager.email, hashed_password, manager.created_at, manager.updated_at))
    conn.commit()
    cursor.close()
    return {'message':'data created'}

@adminRouter.get("/manager/{manger_id}")
async def get_manager(manager_id: int):
    """
    Admin access only
    read one manager
    """
    cursor = conn.cursor()
    query = "SELECT * FROM manager WHERE manager_id = %s"
    try:
        cursor.execute(query, (manager_id,))
        manager = cursor.fetchone()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return manager
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()

@adminRouter.put("/manager/{manger_id}")
async def update_manager(
    manager_id: Annotated[int, Path(title="Manager ID", ge=1)],
    manager: managerScehmaWriter
    ):
    """
    Admin access only
    update manager
    """
    cursor = conn.cursor()
    query = """UPDATE manager SET
            username = %s, email = %s, updated_at = %s,
            WHERE manager_id = %s
    """
    try:
        cursor.execute(query, (manager.username, manager.email, manager.updated_at, manager_id))
        conn.commit()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return manager
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()


@adminRouter.delete("/manager/{manger_id}")
async def delete_manager(manager_id: int):
    """
    Admin access only
    delete one manager
    """
    cursor = conn.cursor()
    query = "DELETE FROM manager WHERE manager_id = %s"
    try:
        cursor.execute(query, (manager_id,))
        conn.commit()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message":"Item is deleted"}
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()


####ADMIN-LCRUD#######

@adminRouter.get("/admins")
async def get_admins(response_model=adminScehmaRead):
    """
    Admin access only
    list all admins
    """
    cursor = conn.cursor()
    query = "SELECT * FROM admin"
    cursor.execute(query)
    admins = cursor.fetchall()
    cursor.close()
    return admins

@adminRouter.post("/new_admin/")
async def create_admin(admin: adminScehmaWrite):
    """
    Admin access only
    Create new amdin
    """
    cursor = conn.cursor()
    hashed_password = get_password_hash(admin.password)
    query = """INSERT INTO admin
    (username, email, password, created_at, updated_at)
    VALUES(%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (admin.username, admin.email, hashed_password, admin.created_at, admin.updated_at))
    conn.commit()
    cursor.close()
    return {'message':'data created'}

# AMDIN SHOULD BE FORBIDEN FROM EDITING OTHER ADMIN ACCOUNT (THAT SHOULD BE IMPLMENTED)
@adminRouter.put("/admin/{admin_id}")
async def update_admins(
    admin_id: Annotated[int, Path(title="Employee ID", ge=1)],
    admin: adminSchemaUpdate
    ):
    """
    Admin access only
    update admn personal account only 
    """
    cursor = conn.cursor()
    query = "UPDATE admin SET username = %s, email = %s, updated_at = %s WHERE admin_id = %s"
    try:
        cursor.execute(query, (admin.username, admin.email, admin.updated_at, admin_id))
        conn.commit()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message":"Item updated sccessfully"}
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()

####PROJECT-LCRUD#######

@adminRouter.get('/projects/')
async def get_progects(response_model=projectSchemaRead):
    """
    Admin access only
    List all projects
    """
    cursor = conn.cursor()
    query = "SELECT * FROM project"
    cursor.execute(query)
    projects = cursor.fetchall()
    cursor.close()
    return projects

@adminRouter.post("/new_project/")
async def create_project(project: projectSchemaWrite):
    """
    Admin access only
    Create new project
    """
    cursor = conn.cursor()
    query = """INSERT INTO project
    (manager_id, project_name, start_date, end_date, created_at, updated_at)
    VALUES(%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (project.manager_id, project.project_name, project.start_date, project.end_date, project.created_at, project.updated_at))
    conn.commit()
    cursor.close()
    return {'message':'data created'}

@adminRouter.get('/project/{project_id}')
async def get_progect(project_id: int):
    """
    Admin access only
    to get one project
    """
    cursor = conn.cursor()
    query = "SELECT * FROM project WHERE project_id = %s"
    try:
        cursor.execute(query, (project_id,))
        project = cursor.fetchone()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return project
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()

@adminRouter.put('/project/{project_id}')
async def update_progect(
    project_id: Annotated[int, Path(title="Project ID", ge=1)],
    project: projectSchemaUpdate):
    """
    Admin access only
    to update project
    """
    cursor = conn.cursor()
    query = "UPDATE project SET manager_id = %s, project_name = %s, start_date = %s, end_date = %s, updated_at = %s WHERE project_id = %s"
    try:
        cursor.execute(query, (project.manager_id, project.project_name, project.start_date, project.end_date, project.updated_at, project_id))
        conn.commit()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message":"Item updated sccessfully"}
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()


@adminRouter.delete('/project/{project_id}')
async def delete_progect(project_id: Annotated[int, Path(title="Project ID", ge=1)]):
    """
    Admin access only
    to delete one project
    """
    cursor = conn.cursor()
    query = "DELETE FROM project WHERE project_id = %s"
    try:
        cursor.execute(query, (project_id,))
        conn.commit()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message": "Item is deleted"}
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()


####LEAVE-LCRUD#######

@adminRouter.get('/leaves/')
async def get_leaves(response_model=leaveSchemaRead):
    """
    Admin access only
    List all leaves
    """
    cursor = conn.cursor()
    query = "SELECT * FROM leave_tbl"
    cursor.execute(query)
    leaves = cursor.fetchall()
    cursor.close()
    return leaves

@adminRouter.post("/new_leave/")
async def create_leave(leave: leaveSchemaWrite):
    """
    Admin access only
    Create new leave
    """
    cursor = conn.cursor()
    query = """INSERT INTO leave_tbl
    (employee_id, start_date, end_date, leave_type, status, created_at, updated_at)
    VALUES(%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (leave.employee_id, leave.start_date, leave.end_date, leave.leave_type, leave.status, leave.created_at, leave.updated_at))
    conn.commit()
    cursor.close()
    return {'message':'data created'}

@adminRouter.get('/leave/{leave_id}')
async def get_leave(leave_id: int):
    """
    Admin access only
    get one leave
    """
    cursor = conn.cursor()
    query = "SELECT * FROM leave_tbl WHERE leave_id = %s"
    try:
        cursor.execute(query, (leave_id,))
        leave = cursor.fetchone()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return leave
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()

@adminRouter.put('/leave/{leave_id}')
async def update_leave(leave_id: Annotated[int, Path(title="Project ID", ge=1)], leave: leaveSchemaUpdate):
    """
    Admin access only
    update leave data
    """
    cursor = conn.cursor()
    query = "UPDATE leave_tbl SET employee_id = %s, start_date = %s, end_date = %s, leave_type = %s, status = %s, updated_at = %s WHERE leave_id=%s"
    try:
        cursor.execute(query, (leave.employee_id, leave.start_date, leave.end_date, leave.leave_type, leave.status, leave.updated_at, leave_id))
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message":"Item updated sccessfully"}
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()


@adminRouter.delete('/leave/{leave_id}')
async def delete_leave(leave_id: int):
    """
    Admin access only
    delete one leave
    """
    cursor = conn.cursor()
    query = "DELETE FROM leave_tbl WHERE leave_id = %s"
    try:
        cursor.execute(query, (leave_id,))
        conn.commit()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message":"Item is deleted"}
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()


####SALARY-LCRUD#######

@adminRouter.get('/salaries/')
async def get_salaries(response_model=salarySchemaRead):
    """
    Admin access only
    List all salaries
    """
    cursor = conn.cursor()
    query = "SELECT * FROM salary"
    cursor.execute(query)
    salaries = cursor.fetchall()
    cursor.close()
    return salaries

@adminRouter.post("/new_salary/")
async def create_salary(salary: salarySchemaWrite):
    """
    Admin access only
    Create new salary
    """
    cursor = conn.cursor()
    query = """INSERT INTO salary
    (employee_id, salary_date, amount, created_at, updated_at)
    VALUES(%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (salary.employee_id, salary.salary_date, salary.amount, salary.created_at, salary.updated_at))
    conn.commit()
    cursor.close()
    return {'message':'data created'}

@adminRouter.get('/salary/{salary_id}')
async def get_salary(salary_id: int):
    """
    Admin access only
    get one salary
    """
    cursor = conn.cursor()
    query = "SELECT * FROM salary WHERE salary_id = %s"
    try:
        cursor.execute(query, (salary_id,))
        salary = cursor.fetchone()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return salary
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()

@adminRouter.put('/salary/{salary_id}')
async def update_salary(salary_id: int, salary: salarySchemaUpdate):
    """
    Admin access only
    update salary
    """
    cursor = conn.cursor()
    query = "UPDATE salary SET employee_id = %s, salary_date = %s, amount = %s, updated_at = %s WHERE salary_id = %s"
    try:
        cursor.execute(query, (salary.employee_id, salary.salary_date, salary.amount, salary.updated_at, salary_id,))
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message":"Item updated sccessfully"}
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()


@adminRouter.delete('/salary/{salary_id}')
async def delete_salary(salary_id: int):
    """
    Admin access only
    delete one salary
    """
    cursor = conn.cursor()
    query = "DELETE FROM salary WHERE salary_id = %s"
    try:
        cursor.execute(query, (salary_id,))
        conn.commit()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message":"Item is deleted"}
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()
