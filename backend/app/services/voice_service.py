import pyttsx3
import speech_recognition as sr
import asyncio
import io
import wave
import threading
from typing import Optional, Dict, Any
import logging
import tempfile
import os

logger = logging.getLogger(__name__)

class VoiceService:
    def __init__(self):
        # Initialize TTS engine
        try:
            self.tts_engine = pyttsx3.init()
            voices = self.tts_engine.getProperty('voices')
            
            # Set female voice if available
            if voices and len(voices) > 1:
                self.tts_engine.setProperty('voice', voices[1].id)
            
            # Set default properties
            self.tts_engine.setProperty('rate', 150)  # Speed
            self.tts_engine.setProperty('volume', 0.8)  # Volume (0.0 to 1.0)
            
            self.tts_available = True
            logger.info("TTS engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {str(e)}")
            self.tts_engine = None
            self.tts_available = False
        
        # Initialize Speech Recognition
        try:
            self.sr_recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self.microphone as source:
                self.sr_recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self.sr_available = True
            logger.info("Speech recognition initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize speech recognition: {str(e)}")
            self.sr_recognizer = None
            self.microphone = None
            self.sr_available = False
    
    async def text_to_speech(self, text: str, voice: Optional[str] = None, speed: int = 150) -> Dict[str, Any]:
        """Convert text to speech and return audio data"""
        if not self.tts_available:
            return {"error": "TTS not available", "success": False}
        
        try:
            # Set voice properties
            self.tts_engine.setProperty('rate', speed)
            
            # Create temporary file for audio output
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Save speech to file
            self.tts_engine.save_to_file(text, temp_path)
            self.tts_engine.runAndWait()
            
            # Read the audio file
            with open(temp_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Clean up
            os.unlink(temp_path)
            
            return {
                "success": True,
                "audio_data": audio_data,
                "format": "wav",
                "text": text,
                "duration": len(text) * 0.1  # Rough estimation
            }
            
        except Exception as e:
            logger.error(f"TTS error: {str(e)}")
            return {"error": str(e), "success": False}
    
    async def speech_to_text(self, audio_data: bytes = None, timeout: int = 10) -> Dict[str, Any]:
        """Convert speech to text from microphone or audio data"""
        if not self.sr_available:
            return {"error": "Speech recognition not available", "success": False}
        
        try:
            if audio_data:
                # Process provided audio data
                audio_file = io.BytesIO(audio_data)
                with sr.AudioFile(audio_file) as source:
                    audio = self.sr_recognizer.record(source)
            else:
                # Listen from microphone
                with self.microphone as source:
                    logger.info("Listening for speech...")
                    audio = self.sr_recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            # Recognize speech using Google Speech Recognition
            text = self.sr_recognizer.recognize_google(audio)
            
            return {
                "success": True,
                "text": text,
                "confidence": 1.0  # Google API doesn't return confidence
            }
            
        except sr.WaitTimeoutError:
            return {"error": "No speech detected within timeout", "success": False}
        except sr.UnknownValueError:
            return {"error": "Could not understand audio", "success": False}
        except sr.RequestError as e:
            return {"error": f"Recognition service error: {str(e)}", "success": False}
        except Exception as e:
            logger.error(f"Speech recognition error: {str(e)}")
            return {"error": str(e), "success": False}
    
    def speak_sync(self, text: str):
        """Synchronous speech - blocks until finished"""
        if self.tts_available:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                return True
            except Exception as e:
                logger.error(f"Sync speech error: {str(e)}")
                return False
        return False
    
    async def speak_async(self, text: str):
        """Asynchronous speech - non-blocking"""
        def _speak():
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                logger.error(f"Async speech error: {str(e)}")
        
        if self.tts_available:
            thread = threading.Thread(target=_speak)
            thread.daemon = True
            thread.start()
            return True
        return False
    
    def get_available_voices(self) -> Dict[str, Any]:
        """Get list of available TTS voices"""
        if not self.tts_available:
            return {"voices": [], "error": "TTS not available"}
        
        try:
            voices = self.tts_engine.getProperty('voices')
            voice_list = []
            
            for i, voice in enumerate(voices):
                voice_info = {
                    "id": voice.id,
                    "name": voice.name,
                    "gender": "female" if "female" in voice.name.lower() else "male",
                    "language": getattr(voice, 'languages', ['en'])[0] if hasattr(voice, 'languages') else 'en'
                }
                voice_list.append(voice_info)
            
            return {"voices": voice_list, "current_voice": self.tts_engine.getProperty('voice')}
            
        except Exception as e:
            logger.error(f"Error getting voices: {str(e)}")
            return {"voices": [], "error": str(e)}
    
    def set_voice(self, voice_id: str) -> bool:
        """Set the TTS voice"""
        if not self.tts_available:
            return False
        
        try:
            self.tts_engine.setProperty('voice', voice_id)
            return True
        except Exception as e:
            logger.error(f"Error setting voice: {str(e)}")
            return False
    
    def set_speech_rate(self, rate: int) -> bool:
        """Set the speech rate (words per minute)"""
        if not self.tts_available:
            return False
        
        try:
            # Clamp rate between reasonable limits
            rate = max(50, min(300, rate))
            self.tts_engine.setProperty('rate', rate)
            return True
        except Exception as e:
            logger.error(f"Error setting speech rate: {str(e)}")
            return False
    
    def get_microphone_list(self) -> Dict[str, Any]:
        """Get list of available microphones"""
        if not self.sr_available:
            return {"microphones": [], "error": "Speech recognition not available"}
        
        try:
            microphones = []
            for i, name in enumerate(sr.Microphone.list_microphone_names()):
                microphones.append({
                    "index": i,
                    "name": name
                })
            
            return {"microphones": microphones}
            
        except Exception as e:
            logger.error(f"Error getting microphones: {str(e)}")
            return {"microphones": [], "error": str(e)}
    
    def test_microphone(self, device_index: Optional[int] = None) -> Dict[str, Any]:
        """Test microphone functionality"""
        if not self.sr_available:
            return {"success": False, "error": "Speech recognition not available"}
        
        try:
            # Test with specific microphone if provided
            if device_index is not None:
                test_mic = sr.Microphone(device_index=device_index)
            else:
                test_mic = self.microphone
            
            with test_mic as source:
                # Quick ambient noise adjustment
                self.sr_recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Test recording
                audio = self.sr_recognizer.listen(source, timeout=1, phrase_time_limit=2)
                
            return {
                "success": True, 
                "message": "Microphone test successful",
                "energy_threshold": self.sr_recognizer.energy_threshold
            }
            
        except sr.WaitTimeoutError:
            return {"success": True, "message": "Microphone working (no speech detected)"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "tts_available": self.tts_available,
            "speech_recognition_available": self.sr_available,
            "current_voice": self.tts_engine.getProperty('voice') if self.tts_available else None,
            "current_rate": self.tts_engine.getProperty('rate') if self.tts_available else None,
            "energy_threshold": self.sr_recognizer.energy_threshold if self.sr_available else None
        }
