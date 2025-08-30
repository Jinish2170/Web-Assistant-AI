from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    TEXT = "text"
    VOICE = "voice"
    FILE = "file"
    IMAGE = "image"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

# Chat models
class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    message_type: MessageType = MessageType.TEXT
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()

class ChatRequest(BaseModel):
    message: str
    message_type: MessageType = MessageType.TEXT
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    response_type: MessageType = MessageType.TEXT
    metadata: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None

# User models
class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True

# File upload models
class FileUploadResponse(BaseModel):
    filename: str
    file_id: str
    file_size: int
    file_type: str
    processed: bool = False
    summary: Optional[str] = None

# Web scraping models
class WebScrapeRequest(BaseModel):
    url: str
    max_pages: int = 1
    extract_links: bool = True
    extract_images: bool = False

class WebScrapeResponse(BaseModel):
    url: str
    title: Optional[str] = None
    content: str
    links: Optional[List[str]] = None
    images: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

# Task automation models
class TaskRequest(BaseModel):
    task_type: str
    parameters: Dict[str, Any]
    schedule: Optional[str] = None  # For scheduled tasks

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Voice models
class VoiceRequest(BaseModel):
    text: str
    voice: Optional[str] = "default"
    speed: Optional[int] = 150
    output_format: str = "mp3"

class VoiceResponse(BaseModel):
    audio_url: str
    duration: Optional[float] = None

# Knowledge base models
class KnowledgeEntry(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    source: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class SearchQuery(BaseModel):
    query: str
    limit: int = 10
    filters: Optional[Dict[str, Any]] = None

class SearchResult(BaseModel):
    entries: List[KnowledgeEntry]
    total: int
    query: str
