from pydantic import BaseModel

class NurseryView(BaseModel):
    nursery_id: str
    nursery_name: str
