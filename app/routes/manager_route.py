from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, Path, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
import mysql.connector
from dotenv import load_dotenv

import os
from models.employee import employeeScehmaRead, employeeScehmaWrite
from models.project import projectSchemaRead, projectSchemaUpdate, projectSchemaWrite
from models.manager import managerScehmaRead, managerSchemaUpdate

from auth import verify_password, get_password_hash
from configs import conn

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

managerRouter = APIRouter()

# here manager can login RU his data
# also can CRUD project own projects
# can olny update employees role that worked upder him
# can CLU(only role) leave for employees under him - since manger can only edit one column from their employee which is their role need to create new schema

def query_manager(username: str):
    # for authetication and authorization purposes 
    cursor = conn.cursor()
    query = "SELECT * FROM manager WHERE username = %s"
    cursor.execute(query, (username,))
    manager = cursor.fetchone()
    cursor.close()
    return manager

def authenticate_manager(username: str, password: str):
        manager: managerScehmaRead = query_manager(username)
        if verify_password(password, manager[3]):
             return manager
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

@managerRouter.post("/login/")
async def login(form_data: OAuth2PasswordRequestForm=Depends()):
     """
     Manager access
     manager login
     """
     manager = authenticate_manager(form_data.username, form_data.password)
     if not manager:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorect username or password")
     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
     access_token = create_access_token(
          data={"sub":manager[1]},
          expires_delta=access_token_expires
     )
     return {'access_token':access_token, "token_type": "bearer"}

@managerRouter.get("/profile/")
async def get_profile(username: str = Depends(decode_access_token)):
     """
     Manager access
     Manager profile get
     """
     cursor = conn.cursor()
     query = "SELECT * FROM manager WHERE username = %s"
     try:
        cursor.execute(query, (username,))
        manager = cursor.fetchone()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return manager
     except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
     finally:
        cursor.close()

@managerRouter.put("/profile/")
async def update_profile(
     manager: managerSchemaUpdate,
     username: str = Depends(decode_access_token)):
     """
     Manager access
     manager profile update
     """
     manager_id = query_manager(username)[0]
     cursor = conn.cursor()
     query = """UPDATE manager SET username = %s,
            email = %s, updated_at = %s, WHERE manager_id = %s"""
     try:
        cursor.execute(query, (manager.username, manager.email, manager.updated_at, manager_id))
        conn.commit()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message":"Item updated sccessfully"}
     except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
     finally:
        cursor.close()
          
@managerRouter.get('/my_projects/')
async def get_my_projects(username: str = Depends(decode_access_token)):
    """
    Manager access
    List mangers project only
    """
    manager_id = query_manager(username)[0]
    cursor = conn.cursor()
    query = "SELECT * FROM project WHERE manager_id = %s"
    try:
        cursor.execute(query, (manager_id, ))
        my_projects = cursor.fetchall()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="No item found")
        return my_projects
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()

@managerRouter.post("/new_project/")
async def create_project(project: projectSchemaWrite, username: str = Depends(decode_access_token)):
    """
    Manager access
    create new project
    Don't give manager_id it is going to be your manger_id by default
    """
    manager_id = query_manager(username)[0]
    cursor = conn.cursor()
    query = """INSERT INTO project
    (manager_id, project_name, start_date, end_date, created_at, updated_at)
    VALUES(%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (manager_id, project.project_name, project.start_date, project.end_date, project.created_at, project.updated_at))
    conn.commit()
    cursor.close()
    return {'message':'data created'}
    
@managerRouter.get('/project/{project_id}')
async def get_progect(project_id: Annotated[int, Path(title="Project ID", ge=1)], username: str = Depends(decode_access_token)):
    """
    Manager access only
    to get one project
    """
    manager_id = query_manager(username)[0]
    cursor = conn.cursor()
    query = "SELECT * FROM project WHERE project_id = %s and manager_id = %s"
    try:
        cursor.execute(query, (project_id, manager_id, ))
        project = cursor.fetchone()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return project
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()

@managerRouter.put('/project/{project_id}')
async def update_progect(
    project_id: Annotated[int, Path(title="Project ID", ge=1)],
    project: projectSchemaUpdate,
    username: str = Depends(decode_access_token)):
    # here should only edit projects with this manger_id
    """
    Manager access only
    to update project
    Can only update project if you are the manager
    Can not change manager at this level (needs admin access) (so changing it does not matter, it just showed it on swager because i added it the scheam.)
    """
    cursor = conn.cursor()
    query_1 = "SELECT * FROM project WHERE project_id = %s"
    try:
        cursor.execute(query_1, (project_id,))
        project_ = cursor.fetchone()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    manager_id = query_manager(username)[0]
    if project_[1] != manager_id:
        return HTTPException(status_code=403, detail="Can not access project")
    
    query = "UPDATE project SET project_name = %s, start_date = %s, end_date = %s, updated_at = %s WHERE project_id = %s"
    try:
        cursor.execute(query, (project.project_name, project.start_date, project.end_date, project.updated_at, project_id))
        conn.commit()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message":"Item updated sccessfully"}
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()

@managerRouter.delete('/project/{project_id}')
async def delete_progect(project_id: Annotated[int, Path(title="Project ID", ge=1)], 
                         username: str = Depends(decode_access_token)):
    """
    Manager access only
    to delete one project
    Can only Delete project if you are the manager
    """
    cursor = conn.cursor()
    query_1 = "SELECT * FROM project WHERE project_id = %s"
    try:
        cursor.execute(query_1, (project_id,))
        project_ = cursor.fetchone()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    manager_id = query_manager(username)[0]
    if project_[1] != manager_id:
        return HTTPException(status_code=403, detail="Can not access project")

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

@managerRouter.get("/my_employees/")
async def get_my_employees(response_model=employeeScehmaRead, username: str = Depends(decode_access_token)):
    """
    Manager access only
    list employees under the manager
    """
    manager_id = query_manager(username)[0]
    cursor = conn.cursor()
    query = "SELECT * FROM employee WHERE manager_id = %s"
    try:
        cursor.execute(query, (manager_id,))
        employees = cursor.fetchall()
        if cursor.rowcount < 1:
            raise HTTPException(status_code=404, detail="Item not found")
        return employees
    except mysql.connector.Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        cursor.close()

@managerRouter.post("/new_employee/")
async def create_employee(employee: employeeScehmaWrite, username: str = Depends(decode_access_token)):
    """
    Admin access only
    Create new employee manager_id is going to be your manager_id, no need to edit
    """
    manager_id_ = query_manager(username)[0]
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
                   (manager_id_, employee.username, employee.email, hashed_password, employee.first_name, employee.last_name, employee.date_of_birth, employee.gender, employee.address, employee.contact_number, employee.hire_date, employee.dept, employee.role, employee.created_at, employee.updated_at)
                   )
    conn.commit()
    cursor.close()
    return {'message':'data created'}
