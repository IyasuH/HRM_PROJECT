from datetime import datetime, date


from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Union

class leaveSchemaUpdate(BaseModel):
    employee_id: int = Field(title="Employee ID item")
    start_date: date = Field(title="Start Date")
    end_date: date = Field(title="End Date")
    leave_type: str = Field(title="Leave type (should be a ENUM type)")
    status: str = Field(title="Status type (should be ENUM type)")
    updated_at: datetime = Field(default=datetime.now(), title="Updated At item")

class leaveSchemaWrite(leaveSchemaUpdate):
    created_at: datetime = Field(default=datetime.now(), title="Created At item")

class leaveSchemaRead(leaveSchemaWrite):
    leave_id: int = Field(title="Leave ID item")