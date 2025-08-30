# DariusAI - Advanced Web Assistant AI 🤖

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.0+-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**DariusAI** is an advanced, web-based AI assistant inspired by J.A.R.V.I.S. from Iron Man. This modern application combines cutting-edge AI technologies with a sleek web interface to provide intelligent assistance across multiple domains including document analysis, web research, voice interaction, and task automation.

## ✨ Features

### 🧠 **Advanced AI Capabilities**
- **Large Language Model Integration**: OpenAI GPT-4, local models via Hugging Face
- **Retrieval-Augmented Generation (RAG)**: Context-aware responses using your documents
- **Conversation Memory**: Maintains context across sessions
- **Multi-modal Processing**: Text, voice, images, and documents

### 🎤 **Voice Interaction**
- **Speech-to-Text**: Real-time voice recognition
- **Text-to-Speech**: Natural voice responses with multiple voice options
- **Voice Commands**: Hands-free operation
- **Audio File Processing**: Upload and transcribe audio files

### 📄 **Document Intelligence**
- **Multi-format Support**: PDF, DOCX, TXT, MD files
- **Smart Summarization**: Extract key insights from documents
- **Knowledge Base**: Persistent learning from your files
- **Semantic Search**: Find relevant information across all documents

### 🌐 **Web Research & Scraping**
- **Intelligent Web Search**: Real-time web search with AI analysis
- **Content Extraction**: Clean, structured data from websites
- **Batch Processing**: Handle multiple URLs simultaneously
- **Search Result Analysis**: AI-powered summaries of web content

### 🔧 **Task Automation**
- **Mathematical Calculations**: Advanced computation capabilities
- **Workflow Automation**: Create custom automation sequences
- **Scheduled Tasks**: Set up recurring operations
- **API Integrations**: Connect with external services

### 💻 **Modern Web Interface**
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Chat**: WebSocket-powered instant messaging
- **Dark Theme**: Professional, eye-friendly interface
- **Drag & Drop**: Easy file uploads
- **Progressive Web App**: Install as a desktop application

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend      │    │   Services      │
│   (React.js)    │◄──►│   (FastAPI)      │◄──►│   (AI/ML)       │
│                 │    │                  │    │                 │
│ • Modern UI     │    │ • REST API       │    │ • OpenAI        │
│ • WebSocket     │    │ • WebSocket      │    │ • LangChain     │
│ • Voice UI      │    │ • File Upload    │    │ • Transformers  │
│ • Real-time     │    │ • Authentication │    │ • Web Scraping  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### **Technology Stack**

**Backend (Python)**
- **FastAPI**: Modern, fast web framework
- **LangChain**: AI/LLM orchestration framework
- **OpenAI API**: GPT models for advanced reasoning
- **Transformers**: Local AI models
- **SQLAlchemy**: Database ORM
- **WebSockets**: Real-time communication

**Frontend (JavaScript)**
- **React.js**: Modern UI framework
- **Material-UI**: Professional component library
- **Socket.IO**: Real-time client communication
- **Web Speech API**: Browser-native voice features
- **Axios**: HTTP client for API calls

**AI/ML Services**
- **OpenAI GPT-4/3.5**: Advanced language understanding
- **Sentence Transformers**: Semantic similarity
- **FAISS**: Vector similarity search
- **NLTK**: Natural language processing
- **BeautifulSoup**: Web scraping

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key (optional but recommended)

### **Option 1: Automated Setup (Recommended)**

**Windows:**
```bash
# Clone the repository
git clone https://github.com/Jinish2170/Web-Assistant-AI.git
cd Web-Assistant-AI

# Run automated setup
setup.bat
```

**Linux/Mac:**
```bash
# Clone the repository
git clone https://github.com/Jinish2170/Web-Assistant-AI.git
cd Web-Assistant-AI

# Make setup script executable and run
chmod +x setup.sh
./setup.sh
```

### **Option 2: Manual Setup**

1. **Backend Setup:**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   cp .env.example .env
   ```

3. **Start Development Servers:**
   ```bash
   # Terminal 1 - Backend
   cd backend
   python -m uvicorn main:app --reload --port 8000
   
   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

## 🔧 Configuration

### Backend Configuration (`backend/.env`)
```env
# AI/ML APIs
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Database
DATABASE_URL=sqlite:///./darius_ai.db

# Security
SECRET_KEY=your-secret-key-here

# AI Settings
DEFAULT_MODEL=gpt-3.5-turbo
MAX_TOKENS=2000
TEMPERATURE=0.7
```

### Frontend Configuration (`frontend/.env`)
```env
# API Endpoints
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_WS_BASE_URL=ws://localhost:8000/ws

# Feature Flags
REACT_APP_ENABLE_VOICE=true
REACT_APP_ENABLE_FILE_UPLOAD=true
REACT_APP_ENABLE_WEB_SEARCH=true
```

## 📱 Usage

### **Web Interface**
1. Open http://localhost:3000 in your browser
2. Start chatting with DariusAI
3. Upload files by dragging them into the chat
4. Use voice input by clicking the microphone button
5. Access web search and other tools from the sidebar

### **API Usage**
```python
import requests

# Send a chat message
response = requests.post('http://localhost:8000/api/v1/chat', json={
    'message': 'What can you help me with?',
    'session_id': 'my_session'
})

# Upload a file for analysis
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/upload',
        files={'file': f}
    )
```

### **WebSocket Connection**
```javascript
const socket = io('ws://localhost:8000/ws/my_session');

socket.on('connect', () => {
    console.log('Connected to DariusAI');
});

socket.emit('message', {
    type: 'chat',
    content: 'Hello DariusAI!'
});
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/api/v1/chat` | POST | Send chat messages |
| `/api/v1/upload` | POST | Upload files for processing |
| `/api/v1/web/search` | POST | Search and analyze web content |
| `/api/v1/voice/tts` | POST | Text-to-speech conversion |
| `/api/v1/voice/stt` | POST | Speech-to-text conversion |
| `/api/v1/task/calculate` | POST | Perform calculations |
| `/ws/{session_id}` | WebSocket | Real-time chat connection |

Full API documentation: http://localhost:8000/api/docs

## 🐳 Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🧪 Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality
```bash
# Python formatting
black backend/
isort backend/

# JavaScript formatting
cd frontend
npm run lint
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Documentation**: [Wiki](https://github.com/Jinish2170/Web-Assistant-AI/wiki)
- **Issues**: [GitHub Issues](https://github.com/Jinish2170/Web-Assistant-AI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Jinish2170/Web-Assistant-AI/discussions)

## 🚧 Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced workflow automation
- [ ] Multi-user support with authentication
- [ ] Plugin system for custom integrations
- [ ] Voice cloning and personalization
- [ ] Advanced document analysis (OCR, handwriting)
- [ ] Integration with productivity tools (Calendar, Email, CRM)
- [ ] Multi-language support

---

**Made with ❤️ by the DariusAI Team**

*Transform your digital experience with the power of advanced AI assistance.*
- `scikit-learn`
- `speech_recognition`
- `transformers`
- `sentence_transformers`
- `win32com`

## Contributing

Contributions to DariusAI are welcome! If you'd like to contribute, please fork the repository, make your changes, and submit a pull request.


## Contact

For any inquiries or feedback, please contact [Jinish Kathiriya] at [jinishkathiriya@gmail.com].

---

This README provides a detailed overview of DariusAI, its features, installation instructions, usage guidelines, dependencies, and information on contributing to the project.
