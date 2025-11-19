"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Core user profile for the health app
class Profile(BaseModel):
    display_name: str = Field(..., description="Public display name")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    bio: Optional[str] = Field("", description="Short bio")

class Patient(BaseModel):
    email: str = Field(..., description="Email address")
    profile: Profile
    role: str = Field("patient", description="user role: patient/doctor/admin")

class Doctor(BaseModel):
    email: str
    name: str
    specialty: Optional[str] = None
    hospital: Optional[str] = None
    verified: bool = True

class CommunityPost(BaseModel):
    title: str
    content: str
    author: str = Field(..., description="Author display name or id")
    tags: List[str] = []
    likes: int = 0

class CommunityComment(BaseModel):
    post_id: str
    author: str
    content: str

# Example schemas retained for reference
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
