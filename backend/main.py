from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import json
from typing import Dict, List
import logging

from app.core.config import settings
from app.api.endpoints import router
from app.services.ai_service import AdvancedAIService
from app.services.voice_service import VoiceService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Advanced Web-Based AI Assistant with Voice, Web Scraping, and Automation Capabilities",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix=settings.API_V1_STR)

# WebSocket connection manager for real-time chat
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.ai_service = AdvancedAIService()
        self.voice_service = VoiceService()

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connection established: {session_id}")

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket connection closed: {session_id}")

    async def send_personal_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_text(json.dumps(message))

    async def handle_message(self, message: dict, session_id: str):
        """Handle incoming WebSocket messages"""
        try:
            message_type = message.get("type", "chat")
            content = message.get("content", "")
            
            if message_type == "chat":
                # Regular chat message
                response = await self.ai_service.chat(
                    message=content,
                    session_id=session_id,
                    context=message.get("context")
                )
                
                await self.send_personal_message({
                    "type": "chat_response",
                    "content": response["response"],
                    "metadata": response.get("metadata", {}),
                    "suggestions": response.get("suggestions", [])
                }, session_id)
                
            elif message_type == "voice":
                # Voice message (base64 encoded audio)
                # This would be implemented to handle voice data
                await self.send_personal_message({
                    "type": "voice_response",
                    "content": "Voice processing not fully implemented in WebSocket yet"
                }, session_id)
                
            elif message_type == "typing":
                # Handle typing indicators
                await self.send_personal_message({
                    "type": "typing_response",
                    "content": "I'm thinking..."
                }, session_id)
                
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}")
            await self.send_personal_message({
                "type": "error",
                "content": "Sorry, I encountered an error processing your message."
            }, session_id)

manager = ConnectionManager()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, session_id)
    
    # Send welcome message
    await manager.send_personal_message({
        "type": "system",
        "content": "Connected to DariusAI! Send me a message to get started.",
        "timestamp": asyncio.get_event_loop().time()
    }, session_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle the message
            await manager.handle_message(message, session_id)
            
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except json.JSONDecodeError:
        await manager.send_personal_message({
            "type": "error",
            "content": "Invalid message format. Please send valid JSON."
        }, session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await manager.send_personal_message({
            "type": "error",
            "content": "An unexpected error occurred."
        }, session_id)
        manager.disconnect(session_id)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to DariusAI - Advanced Web Assistant",
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "websocket": "/ws/{session_id}",
        "features": [
            "Advanced AI Chat with Context",
            "Voice Interaction (Speech-to-Text & Text-to-Speech)",
            "Web Scraping and Real-time Search",
            "Document Processing (PDF, DOCX, TXT)",
            "Task Automation",
            "Real-time WebSocket Communication",
            "RESTful API Endpoints"
        ],
        "status": "operational"
    }

@app.get("/api/status")
async def api_status():
    """Detailed API status"""
    return {
        "api_version": settings.APP_VERSION,
        "environment": "development" if settings.DEBUG else "production",
        "services": {
            "ai_service": "available",
            "voice_service": manager.voice_service.get_status(),
            "web_scraping": "available",
            "websocket": f"{len(manager.active_connections)} active connections"
        },
        "endpoints": {
            "chat": f"{settings.API_V1_STR}/chat",
            "voice_chat": f"{settings.API_V1_STR}/chat/voice",
            "file_upload": f"{settings.API_V1_STR}/upload",
            "web_scraping": f"{settings.API_V1_STR}/web/scrape",
            "web_search": f"{settings.API_V1_STR}/web/search",
            "text_to_speech": f"{settings.API_V1_STR}/voice/tts",
            "speech_to_text": f"{settings.API_V1_STR}/voice/stt",
            "calculations": f"{settings.API_V1_STR}/task/calculate"
        }
    }

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"API Documentation available at: /api/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down DariusAI...")
    # Close any open connections, save state, etc.
    for session_id in list(manager.active_connections.keys()):
        manager.disconnect(session_id)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
