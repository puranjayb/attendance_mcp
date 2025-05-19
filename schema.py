from pydantic import BaseModel
from typing import List, Dict

class Student(BaseModel):
    name: str
    rollNumber: str
    attendance: Dict[str, bool]  

class ClassGroup(BaseModel):
    className: str
    branch: str
    students: List[Student]
