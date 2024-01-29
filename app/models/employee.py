from datetime import datetime, date


from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Union
from enum import Enum

class Gender(str, Enum):
    Male = "M"
    Female = "F"

class employeeSchemaUpdate(BaseModel):
    manager_id: int = Field(title="Manager ID item")
    username: str = Field(title="Username Item")
    email: EmailStr = Field(title="Email item")
    first_name: str = Field(title="First Name item")
    last_name: str = Field(title="Last Name item")
    date_of_birth: date = Field(title="Date Of Birth item")
    gender: Gender = Field(title="Gender item")
    address: Union[str, None] = Field(default=None, title="Adreess item")
    contact_number: Union[str, None] = Field(default=None, title="Contact item")
    hire_date: date = Field(title="Hire Date item")
    dept: str = Field(title="Department item")
    role: str = Field(title="Role item")
    updated_at: datetime = Field(default=datetime.now(), title="Updated At item")

class employeeScehmaWrite(employeeSchemaUpdate):
    password: str = Field(title="Password item")
    created_at: datetime = Field(default=datetime.now(), title="Created At item")

class employeeScehmaRead(employeeScehmaWrite):
    employee_id: int = Field(title="Employee ID item")