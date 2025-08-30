from typing import Optional, List, Dict, Any
import openai
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, TextLoader
import pickle
import os
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

class AdvancedAIService:
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY
        self.model_name = settings.DEFAULT_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
        
        # Initialize embeddings
        if self.openai_api_key:
            self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
            self.llm = ChatOpenAI(
                openai_api_key=self.openai_api_key,
                model_name=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
        else:
            # Fallback to local models
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self.llm = None
            logger.warning("No OpenAI API key provided, using local embeddings only")
        
        # Initialize memory and vector store
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=10  # Remember last 10 exchanges
        )
        
        self.vector_store = None
        self.qa_chain = None
        self.knowledge_base_path = "knowledge_base"
        
        # Load existing knowledge base
        self.load_knowledge_base()
        
        # System prompt for enhanced capabilities
        self.system_prompt = """You are DariusAI, an advanced web-based personal assistant inspired by J.A.R.V.I.S. 
        You have the following capabilities:
        - Answer questions using your knowledge base and real-time web data
        - Help with calculations, research, and analysis
        - Process and summarize documents
        - Provide personalized recommendations
        - Assist with task automation and workflow optimization
        - Maintain context across conversations
        
        Always be helpful, accurate, and concise. When you don't know something, offer to search for the information or suggest alternatives.
        """
    
    async def chat(self, message: str, session_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Enhanced chat function with context awareness and multiple AI capabilities"""
        try:
            # Check if we have a knowledge base to query
            if self.qa_chain and self.vector_store:
                # Use retrieval-augmented generation
                response = await self._rag_response(message, session_id)
            elif self.llm:
                # Use direct LLM response with memory
                response = await self._direct_llm_response(message, session_id)
            else:
                # Fallback to rule-based responses
                response = await self._fallback_response(message, session_id)
            
            # Add metadata and suggestions
            response_data = {
                "response": response,
                "session_id": session_id,
                "metadata": {
                    "model_used": self.model_name if self.llm else "fallback",
                    "has_knowledge_base": self.vector_store is not None,
                    "context_used": context is not None
                },
                "suggestions": self._generate_suggestions(message, response)
            }
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "session_id": session_id,
                "metadata": {"error": str(e)},
                "suggestions": ["Try rephrasing your question", "Check your internet connection"]
            }
    
    async def _rag_response(self, message: str, session_id: str) -> str:
        """Retrieval-Augmented Generation response"""
        if not self.qa_chain:
            return await self._direct_llm_response(message, session_id)
        
        try:
            result = self.qa_chain({"question": message, "chat_history": []})
            return result["answer"]
        except Exception as e:
            logger.error(f"RAG response error: {str(e)}")
            return await self._direct_llm_response(message, session_id)
    
    async def _direct_llm_response(self, message: str, session_id: str) -> str:
        """Direct LLM response with conversation memory"""
        if not self.llm:
            return await self._fallback_response(message, session_id)
        
        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=message)
            ]
            
            response = self.llm(messages)
            return response.content
        except Exception as e:
            logger.error(f"LLM response error: {str(e)}")
            return await self._fallback_response(message, session_id)
    
    async def _fallback_response(self, message: str, session_id: str) -> str:
        """Fallback rule-based response system"""
        message_lower = message.lower()
        
        # Simple pattern matching for common queries
        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return "Hello! I'm DariusAI, your advanced web assistant. How can I help you today?"
        
        elif any(word in message_lower for word in ["calculate", "math", "compute"]):
            return "I can help with calculations! Please provide the mathematical expression you'd like me to solve."
        
        elif any(word in message_lower for word in ["search", "find", "look up"]):
            return "I can search the web for information. What would you like me to search for?"
        
        elif any(word in message_lower for word in ["weather", "temperature"]):
            return "I can help you get weather information. Please specify the location you're interested in."
        
        else:
            return "I understand you're asking about that topic. While I'm processing your request with my advanced capabilities, could you provide more details or rephrase your question?"
    
    def _generate_suggestions(self, message: str, response: str) -> List[str]:
        """Generate helpful suggestions based on the conversation"""
        suggestions = []
        message_lower = message.lower()
        
        if "calculate" in message_lower:
            suggestions.extend([
                "Try more complex mathematical expressions",
                "Ask about statistical analysis",
                "Request help with financial calculations"
            ])
        elif "search" in message_lower:
            suggestions.extend([
                "Ask me to summarize the search results",
                "Request specific information from websites",
                "Ask about recent news on this topic"
            ])
        else:
            suggestions.extend([
                "Ask me to explain something in more detail",
                "Request help with a specific task",
                "Upload a file for analysis"
            ])
        
        return suggestions[:3]  # Return top 3 suggestions
    
    async def process_file(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Process uploaded files and add to knowledge base"""
        try:
            # Load document based on type
            if file_type == "pdf":
                loader = PyPDFLoader(file_path)
            elif file_type in ["txt", "md"]:
                loader = TextLoader(file_path, encoding="utf-8")
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            # Load and split documents
            documents = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)
            
            # Add to vector store
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(splits, self.embeddings)
            else:
                self.vector_store.add_documents(splits)
            
            # Update QA chain
            self._update_qa_chain()
            
            # Save knowledge base
            self.save_knowledge_base()
            
            # Generate summary
            summary = f"Processed {len(splits)} chunks from {os.path.basename(file_path)}"
            
            return {
                "success": True,
                "summary": summary,
                "chunks_processed": len(splits),
                "file_name": os.path.basename(file_path)
            }
            
        except Exception as e:
            logger.error(f"File processing error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "summary": f"Failed to process {os.path.basename(file_path)}"
            }
    
    def _update_qa_chain(self):
        """Update the QA chain with current vector store"""
        if self.vector_store and self.llm:
            self.qa_chain = ConversationalRetrievalChain.from_llm(
                self.llm,
                self.vector_store.as_retriever(),
                memory=self.memory,
                return_source_documents=True
            )
    
    def save_knowledge_base(self):
        """Save the vector store to disk"""
        if self.vector_store:
            os.makedirs(self.knowledge_base_path, exist_ok=True)
            self.vector_store.save_local(self.knowledge_base_path)
    
    def load_knowledge_base(self):
        """Load existing vector store from disk"""
        try:
            if os.path.exists(self.knowledge_base_path):
                self.vector_store = FAISS.load_local(
                    self.knowledge_base_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                self._update_qa_chain()
                logger.info("Knowledge base loaded successfully")
        except Exception as e:
            logger.error(f"Error loading knowledge base: {str(e)}")
    
    async def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get summary of current knowledge base"""
        if not self.vector_store:
            return {"total_documents": 0, "status": "No knowledge base loaded"}
        
        try:
            # This is a simplified version - in a real implementation,
            # you'd want to store more metadata about the documents
            return {
                "total_documents": self.vector_store.index.ntotal if hasattr(self.vector_store.index, 'ntotal') else 0,
                "status": "Knowledge base active",
                "capabilities": [
                    "Document Q&A",
                    "Semantic search",
                    "Context-aware responses"
                ]
            }
        except Exception as e:
            return {"error": str(e), "status": "Error accessing knowledge base"}
