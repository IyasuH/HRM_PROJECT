from datetime import datetime, date


from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Union

class adminSchemaUpdate(BaseModel):
    username: str = Field(title="Username Item")
    email: EmailStr = Field(title="Email Item")
    updated_at: datetime = Field(default=datetime.now(), title="Updated At item")

class adminScehmaWrite(adminSchemaUpdate):
    password: str = Field(title="Hased Password Item")
    created_at: datetime = Field(default=datetime.now(), title="Created At item")

class adminScehmaRead(adminScehmaWrite):
    admin_id: int = Field(title="Manager Id Item")