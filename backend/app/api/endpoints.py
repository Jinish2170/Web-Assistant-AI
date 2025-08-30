from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse
import asyncio
from typing import List, Dict, Any, Optional
import io
import os
import tempfile
from ..models.schemas import (
    ChatRequest, ChatResponse, WebScrapeRequest, WebScrapeResponse,
    VoiceRequest, VoiceResponse, TaskRequest, TaskResponse
)
from ..services.ai_service import AdvancedAIService
from ..services.web_scraping import WebScrapingService
from ..services.voice_service import VoiceService
import logging

logger = logging.getLogger(__name__)

# Initialize services
ai_service = AdvancedAIService()
voice_service = VoiceService()

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "ai": "available",
            "voice": voice_service.get_status(),
            "web_scraping": "available"
        }
    }

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with enhanced AI capabilities"""
    try:
        result = await ai_service.chat(
            message=request.message,
            session_id=request.session_id or "default",
            context=request.context
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/voice")
async def voice_chat(audio_file: UploadFile = File(...)):
    """Voice chat endpoint - speech to text, process, text to speech"""
    try:
        # Read audio data
        audio_data = await audio_file.read()
        
        # Convert speech to text
        stt_result = await voice_service.speech_to_text(audio_data)
        if not stt_result.get("success"):
            raise HTTPException(status_code=400, detail=stt_result.get("error"))
        
        user_message = stt_result["text"]
        
        # Process with AI
        ai_result = await ai_service.chat(
            message=user_message,
            session_id="voice_session",
            context={"input_type": "voice"}
        )
        
        # Convert response to speech
        tts_result = await voice_service.text_to_speech(ai_result["response"])
        if not tts_result.get("success"):
            raise HTTPException(status_code=500, detail=tts_result.get("error"))
        
        # Return audio response
        audio_stream = io.BytesIO(tts_result["audio_data"])
        
        return StreamingResponse(
            audio_stream,
            media_type="audio/wav",
            headers={
                "X-User-Message": user_message,
                "X-AI-Response": ai_result["response"][:100] + "..." if len(ai_result["response"]) > 100 else ai_result["response"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process files (PDF, text, etc.)"""
    try:
        # Check file type
        file_extension = file.filename.split('.')[-1].lower()
        allowed_extensions = ['pdf', 'txt', 'md', 'docx']
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not supported. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process file with AI service
            result = await ai_service.process_file(temp_file_path, file_extension)
            
            return {
                "filename": file.filename,
                "file_type": file_extension,
                "file_size": len(content),
                "processed": result["success"],
                "summary": result["summary"],
                "details": result
            }
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/web/scrape", response_model=List[WebScrapeResponse])
async def scrape_web(request: WebScrapeRequest):
    """Scrape web content from URLs"""
    try:
        async with WebScrapingService() as scraper:
            if isinstance(request.url, str):
                # Single URL
                result = await scraper.scrape_url(
                    request.url,
                    extract_links=request.extract_links,
                    extract_images=request.extract_images
                )
                return [WebScrapeResponse(**result)]
            else:
                # Multiple URLs
                urls = request.url if isinstance(request.url, list) else [request.url]
                results = await scraper.scrape_multiple(
                    urls[:request.max_pages],
                    extract_links=request.extract_links,
                    extract_images=request.extract_images
                )
                return [WebScrapeResponse(**result) for result in results]
                
    except Exception as e:
        logger.error(f"Web scraping error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/web/search")
async def search_web(query: str, num_results: int = 3):
    """Search the web and scrape results"""
    try:
        async with WebScrapingService() as scraper:
            results = await scraper.search_and_scrape(query, num_results)
            
            # Process results with AI for better summaries
            processed_results = []
            for result in results:
                if result.get("content"):
                    # Create a summary using AI
                    summary_request = f"Summarize this web content in 2-3 sentences: {result['content'][:1000]}"
                    ai_summary = await ai_service.chat(
                        message=summary_request,
                        session_id="web_search",
                        context={"task": "summarization"}
                    )
                    
                    processed_results.append({
                        **result,
                        "ai_summary": ai_summary["response"],
                        "relevance_score": 0.8  # Simple scoring
                    })
                else:
                    processed_results.append(result)
            
            return {
                "query": query,
                "results": processed_results,
                "total_found": len(processed_results)
            }
            
    except Exception as e:
        logger.error(f"Web search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice/tts")
async def text_to_speech(request: VoiceRequest):
    """Convert text to speech"""
    try:
        result = await voice_service.text_to_speech(
            text=request.text,
            voice=request.voice,
            speed=request.speed
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        audio_stream = io.BytesIO(result["audio_data"])
        
        return StreamingResponse(
            audio_stream,
            media_type=f"audio/{result['format']}",
            headers={
                "Content-Disposition": "attachment; filename=speech.wav",
                "X-Duration": str(result.get("duration", 0))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice/stt")
async def speech_to_text(audio_file: UploadFile = File(...)):
    """Convert speech to text"""
    try:
        audio_data = await audio_file.read()
        result = await voice_service.speech_to_text(audio_data)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return {
            "text": result["text"],
            "confidence": result.get("confidence", 0.0),
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"STT error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voice/voices")
async def get_voices():
    """Get available TTS voices"""
    return voice_service.get_available_voices()

@router.post("/task/calculate")
async def calculate(expression: str):
    """Perform mathematical calculations"""
    try:
        # Simple evaluation with safety checks
        allowed_names = {
            k: v for k, v in __builtins__.items() 
            if k in ['abs', 'round', 'min', 'max', 'sum', 'pow']
        }
        allowed_names.update({
            'pi': 3.141592653589793,
            'e': 2.718281828459045,
            'sqrt': lambda x: x ** 0.5,
            'sin': lambda x: __import__('math').sin(x),
            'cos': lambda x: __import__('math').cos(x),
            'tan': lambda x: __import__('math').tan(x),
            'log': lambda x: __import__('math').log(x),
            'log10': lambda x: __import__('math').log10(x),
        })
        
        # Evaluate expression safely
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        
        return {
            "expression": expression,
            "result": result,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        return {
            "expression": expression,
            "error": str(e),
            "success": False
        }

@router.get("/knowledge/summary")
async def get_knowledge_summary():
    """Get summary of current knowledge base"""
    try:
        summary = await ai_service.get_knowledge_summary()
        return summary
    except Exception as e:
        logger.error(f"Knowledge summary error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/automate")
async def create_automation_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """Create automated tasks"""
    try:
        # This is a placeholder for task automation
        # In a full implementation, you'd have a task queue system like Celery
        
        task_id = f"task_{hash(str(request.parameters))}"
        
        if request.task_type == "web_monitoring":
            # Monitor a website for changes
            background_tasks.add_task(
                _monitor_website,
                request.parameters.get("url"),
                request.parameters.get("interval", 3600)
            )
        elif request.task_type == "scheduled_search":
            # Perform scheduled web searches
            background_tasks.add_task(
                _scheduled_search,
                request.parameters.get("query"),
                request.parameters.get("frequency", "daily")
            )
        
        return TaskResponse(
            task_id=task_id,
            status="created",
            result={"message": f"Task {request.task_type} created successfully"}
        )
        
    except Exception as e:
        logger.error(f"Task automation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task functions
async def _monitor_website(url: str, interval: int):
    """Background task to monitor website changes"""
    # Implementation would go here
    logger.info(f"Monitoring {url} every {interval} seconds")

async def _scheduled_search(query: str, frequency: str):
    """Background task for scheduled searches"""
    # Implementation would go here
    logger.info(f"Scheduled search for '{query}' with frequency {frequency}")

@router.get("/stats")
async def get_stats():
    """Get service statistics"""
    return {
        "total_conversations": 0,  # Would track in database
        "files_processed": 0,     # Would track in database
        "web_pages_scraped": 0,   # Would track in database
        "voice_interactions": 0,  # Would track in database
        "uptime": "0 days",       # Would calculate actual uptime
        "version": "2.0.0"
    }
