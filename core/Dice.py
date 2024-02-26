from pydantic import BaseModel, Field
from typing import Optional

class Dice(BaseModel):
    amount: int | None
    type: int | None