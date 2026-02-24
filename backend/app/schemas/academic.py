"""
Academic Schemas - Degrees, Departments, Semesters, Subjects
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ==========================================
# Degree Schemas
# ==========================================

class DegreeBase(BaseModel):
    """Base degree schema."""
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    duration_years: int = Field(..., ge=1, le=6)


class DegreeCreate(DegreeBase):
    """Degree creation schema."""
    pass


class DegreeUpdate(BaseModel):
    """Degree update schema."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    duration_years: Optional[int] = Field(None, ge=1, le=6)
    is_active: Optional[bool] = None


class DegreeResponse(DegreeBase):
    """Degree response schema."""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# Department Schemas
# ==========================================

class DepartmentBase(BaseModel):
    """Base department schema."""
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)


class DepartmentCreate(DepartmentBase):
    """Department creation schema."""
    pass


class DepartmentUpdate(BaseModel):
    """Department update schema."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    is_active: Optional[bool] = None


class DepartmentResponse(DepartmentBase):
    """Department response schema."""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# Semester Schemas
# ==========================================

class SemesterBase(BaseModel):
    """Base semester schema."""
    number: int = Field(..., ge=1, le=12)
    degree_id: int


class SemesterCreate(SemesterBase):
    """Semester creation schema."""
    pass


class SemesterUpdate(BaseModel):
    """Semester update schema."""
    is_active: Optional[bool] = None


class SemesterResponse(SemesterBase):
    """Semester response schema."""
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class SemesterWithDegree(SemesterResponse):
    """Semester with degree details."""
    degree: DegreeResponse


# ==========================================
# Subject Schemas
# ==========================================

class SubjectBase(BaseModel):
    """Base subject schema."""
    name: str = Field(..., min_length=2, max_length=150)
    code: str = Field(..., min_length=1, max_length=20)
    credits: int = Field(3, ge=1, le=10)
    degree_id: int
    department_id: int
    semester_id: int


class SubjectCreate(SubjectBase):
    """Subject creation schema."""
    pass


class SubjectUpdate(BaseModel):
    """Subject update schema."""
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    credits: Optional[int] = Field(None, ge=1, le=10)
    is_active: Optional[bool] = None


class SubjectResponse(SubjectBase):
    """Subject response schema."""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SubjectWithDetails(SubjectResponse):
    """Subject with related entities."""
    degree: DegreeResponse
    department: DepartmentResponse
    semester: SemesterResponse


# ==========================================
# Class Allocation Schemas
# ==========================================

class ClassAllocationBase(BaseModel):
    """Base class allocation schema."""
    teacher_id: int
    degree_id: int
    department_id: int
    semester_id: int
    subject_id: int
    academic_year: str = Field(..., pattern=r"^\d{4}-\d{4}$")  # e.g., "2024-2025"


class ClassAllocationCreate(ClassAllocationBase):
    """Class allocation creation schema."""
    pass


class ClassAllocationResponse(ClassAllocationBase):
    """Class allocation response schema."""
    id: int
    is_active: bool

    class Config:
        from_attributes = True


# ==========================================
# Teacher Subject Assignment
# ==========================================

class TeacherSubjectAssign(BaseModel):
    """Assign subject to teacher."""
    teacher_id: int
    subject_id: int
    academic_year: str = Field(..., pattern=r"^\d{4}-\d{4}$")


class TeacherSubjectResponse(BaseModel):
    """Teacher subject assignment response."""
    id: int
    teacher_id: int
    subject_id: int
    academic_year: str
    is_active: bool

    class Config:
        from_attributes = True


# ==========================================
# Semester Progression
# ==========================================

class SemesterProgressionRequest(BaseModel):
    """Request to advance semester for students."""
    degree_id: int
    department_id: int
    from_semester_id: int
    to_semester_id: int
