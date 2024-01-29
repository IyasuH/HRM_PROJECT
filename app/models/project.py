from datetime import datetime, date


from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Union

class projectSchemaUpdate(BaseModel):
    manager_id: int = Field(title="Manager ID item")
    project_name: str = Field(title="Project Name Item")
    start_date: date = Field(title="Start Date")
    end_date: date = Field(title="End Date")
    updated_at: datetime = Field(default=datetime.now(), title="Updated At item")

class projectSchemaWrite(projectSchemaUpdate):
    created_at: datetime = Field(default=datetime.now(), title="Created At item")

class projectSchemaRead(projectSchemaWrite):
    project_id: int = Field(title="Project ID item")
