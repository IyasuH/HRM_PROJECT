from datetime import datetime, date


from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Union

class salarySchemaUpdate(BaseModel):
    employee_id: int = Field(title="Emplyee ID item")
    salary_date: date = Field(title="End Date")
    amount: float = Field(title="Amount item")
    updated_at: datetime = Field(default=datetime.now(), title="Updated At item")

class salarySchemaWrite(salarySchemaUpdate):
    created_at: datetime = Field(default=datetime.now(), title="Created At item")

class salarySchemaRead(salarySchemaWrite):
    salary_id: int = Field(title="Salary ID item")