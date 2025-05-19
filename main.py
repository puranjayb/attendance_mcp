from mcp.server.fastmcp import FastMCP
from pymongo.collection import Collection
from schema import ClassGroup, Student
from typing import Dict
from dbConfig import myDB

mcp = FastMCP(name="attendance_mcp")
class_collection: Collection = myDB["Classes"]

def get_class_id(class_name: str):
    """Get class ID from class name."""
    class_ = class_collection.find_one({"className": class_name}, {"_id": 1})
    if not class_:
        return {"error": "Class not found"}, 404
    else:
        return {"_id": class_["_id"]}

# ---------- Resource Endpoints (Read Operations) ----------

@mcp.resource("class://getClassByName/{class_name}")
def get_class_by_name(class_name: str):
    """Get class details by class name."""
    try:
        class_ = class_collection.find_one(
            {"className": class_name},
            {"_id": 1, "className": 1, "branch": 1, "students": 1}
        )

        if class_:
            class_["_id"] = str(class_["_id"])
            return {"class": class_}
        else:
            return{"error": "Class not found"}, 404
        
    except Exception as e:
        return {"error": str(e)}, 500

@mcp.resource("class://getAll")
def get_all_classes():
    """Get all classes."""
    try:
        classes = list(class_collection.find(
            {},
            {"_id": 1, "className": 1, "branch": 1}
        ))

        if classes:
            for class_ in classes:
                class_["_id"] = str(class_["_id"])
            return {"classes": classes}
        else:
            return {"error": "No classes found"}, 404
        
    except Exception as e:
        return {"error": str(e)}, 500

@mcp.resource("class://getStudents/{class_name}")
def get_students(class_name: str):
    """Get all students in a class."""
    try:
        class_ = get_class_id(class_name)

        if isinstance(class_, tuple):
            return class_

        students = class_collection.find_one(
            {"_id": class_["_id"]},
            {"students": 1, "_id": 0}
        )

        if students and "students" in students:
            return {"students": students["students"]}
        else:
            return {"error": "No students found"}, 404

    except Exception as e:
        return {"error": str(e)}, 500


@mcp.resource("class://getStudentByRoll/{class_name}/{registration_number}")
def get_student_by_roll(class_name:str, registration_number: str):
    """Get student details by roll number."""
    try:
        class_ = get_class_id(class_name)

        if isinstance(class_, tuple):
            return class_
         
        student = class_collection.find_one(
            {"_id": class_["_id"], "students.rollNumber": registration_number},
            {"students.$": 1}
        )

        if student and "students" in student:
            student = student["students"][0]
            return {"student": student}
        
        else:
            return {"error": "Student not found"}, 404
        
    except Exception as e:
        return {"error": str(e)}, 500    

# ---------- Tool Endpoints (Write Operations) ----------

@mcp.tool("createClass")
def create_class(data: ClassGroup):
    """Create a new class."""
    try:
        if class_collection.find_one({"className": data.className}):
            return {"error": "Class already exists"}, 400

        class_ = dict(data)
        class_["_id"] = f"{data.className}-{data.branch}"
        class_["students"] = [s.dict() for s in data.students]

        result = class_collection.insert_one(class_)

        if result.acknowledged:
            return {"message": "Class created", "class_id": str(result.inserted_id)}, 201
        else:
            return {"error": "Failed to create class"}, 500
        
    except Exception as e:
        return {"error": str(e)}, 500


@mcp.tool("updateClassWithClassName")
def update_class(class_name: str, data: ClassGroup):
    """Update class details by class name."""
    try:
        class_ = get_class_id(class_name)

        if isinstance(class_, tuple):
            return class_

        updated_class = dict(data)
        updated_class["students"] = [s.dict() for s in data.students]

        result = class_collection.update_one({"_id": class_["_id"]}, {"$set": updated_class})
        
        if result.modified_count > 0:
            return {"message": "Class updated"}
        else: 
            return {"error": "No changes made"}, 404
        
    except Exception as e:
        return {"error": str(e)}, 500


@mcp.tool("deleteClassWithClassName")
def delete_class(class_name: str):
    """Delete a class by class name."""
    try:
        class_ = get_class_id(class_name)

        if isinstance(class_, tuple):
            return class_

        result = class_collection.delete_one({"_id": class_["_id"]})

        if result.deleted_count > 0:
            return {"message": "Class deleted"}
        else:
            return {"error": "Class not found"}, 404
        
    except Exception as e:
        return {"error": str(e)}, 500

@mcp.tool("addNewStudentByClassName")
def add_student(class_name: str, student: Student):
    """Add a new student to a class by class name."""
    try:
        class_ = get_class_id(class_name)

        if isinstance(class_, tuple):
            return class_

        if class_collection.find_one({"_id": class_["_id"], "students.rollNumber": student.rollNumber}):
            return {"error": "Student exists"}, 400

        res = class_collection.update_one(
            {"_id": class_["_id"]},
            {"$push": {"students": dict(student)}}
        )
        
        if res.modified_count > 0:
            return {"message": "Student added"}
        else:
            return {"error": "Failed to add student"}, 500
        
    except Exception as e:
        return {"error": str(e)}, 500

@mcp.tool("removeStudentByClassName")
def remove_student(class_name: str, name: str):
    """Remove a student from a class by class name."""
    try:
        class_ = get_class_id(class_name)

        if isinstance(class_, tuple):
            return class_
        
        if not class_collection.find_one({"_id": class_["_id"], "students.name": name}):
            return {"error": "Student not found"}, 404
        
        res = class_collection.update_one(
            {"_id": class_["_id"]},
            {"$pull": {"students": {"name": name}}}
        )
        
        if res.modified_count > 0:
            return {"message": "Student removed"}
        else:
            return {"error": "Failed to remove student"}, 500
        
    except Exception as e:
        return {"error": str(e)}, 500

@mcp.tool("updateStudentByClassName")
def update_student(class_name: str, name: str, data: Student):
    """Update a student's details in a class by class name."""
    try:
        class_ = get_class_id(class_name)

        if isinstance(class_, tuple):
            return class_

        if not class_collection.find_one({"_id": class_["_id"], "students.name": name}):
            return {"error": "Student not found"}, 404
        
        res = class_collection.update_one(
            {"_id": class_["_id"], "students.name": name},
            {"$set": {"students.$": dict(data)}}
        )
        
        if res.modified_count > 0:
            return {"message": "Student updated"}
        else:
            return {"error": "No changes made"}, 404
        
    except Exception as e:
        return {"error": str(e)}, 500


@mcp.tool("getAttendanceByClassName")
def class_attendance(class_name: str):
    """Get attendance for all students in a class by class name."""
    try:
        class_ = get_class_id(class_name)

        if isinstance(class_, tuple):
            return class_

        students = class_collection.find_one({"_id": class_["_id"]}, {"students": 1})
        if not students:
            return {"error": "No students found"}, 404

        students = students.get("students", [])
        result = []
        for s in students:
            total = len(s.get("attendance", {}))
            attended = sum(1 for v in s.get("attendance", {}).values() if v)
            percent = (attended / total * 100) if total else 0
            result.append({"name": s["name"], "rollNumber": s["rollNumber"], "attendancePercentage": percent})

        return {"attendance": result}
    except Exception as e:
        return {"error": str(e)}, 500

@mcp.tool("getAttendanceByClassNameAndRollNumber")
def student_attendance(class_name: str, registration_number: str):
    """Get attendance for a specific student in a class by class name and roll number."""
    try:
        class_ = get_class_id(class_name)

        if isinstance(class_, tuple):
            return class_

        student = class_collection.find_one(
            {"_id": class_["_id"], "students.rollNumber": registration_number},
            {"students.$": 1}
        )
        if not student:
            return {"error": "Student not found"}, 404

        student = student["students"][0]
        total = len(student.get("attendance", {}))
        attended = sum(1 for v in student.get("attendance", {}).values() if v)
        percent = (attended / total * 100) if total else 0
        return {"name": student["name"], "rollNumber": student["rollNumber"], "attendancePercentage": percent}
    except Exception as e:
        return {"error": str(e)}, 500

@mcp.tool("updateAttendanceByClassNameAndRollNumber")
def update_attendance(class_name: str, registration_number: str, attendance: Dict[str, bool]):
    """Update attendance for a specific student in a class by class name and roll number."""
    try:
        class_ = get_class_id(class_name)

        if isinstance(class_, tuple):
            return class_

        update_student_attendance = {f"students.$.attendance.{k}": v for k, v in attendance.items()}
        result = class_collection.update_one(
            {"_id": class_["_id"], "students.rollNumber": registration_number},
            {"$set": update_student_attendance}
        )
        
        if result.modified_count > 0:
            return {"message": "Attendance updated"}
        else:
            return {"error": "No changes made"}, 404
        
    except Exception as e:
        return {"error": str(e)}, 500