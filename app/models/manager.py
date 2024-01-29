from datetime import datetime, date
# from datetime.datetime import date

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Union

class managerSchemaUpdate(BaseModel):
    username: str = Field(title="Username Item")
    email: EmailStr = Field(title="Email Item")
    updated_at: datetime = Field(default=datetime.now(), title="Updated At item")

class managerScehmaWriter(managerSchemaUpdate):
    password: str = Field(title="Hased Password Item")
    created_at: datetime = Field(default=datetime.now(), title="Created At item")

class managerScehmaRead(managerScehmaWriter):
    manager_id: int = Field(title="Manager Id Item")