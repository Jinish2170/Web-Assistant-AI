# 🚀 Getting Started with DariusAI

Welcome to DariusAI - your advanced web-based AI assistant! Follow these steps to get up and running quickly.

## 🎯 Prerequisites

Before you begin, make sure you have:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **OpenAI API Key** (recommended) - [Get API Key](https://platform.openai.com/api-keys)

## 🔧 Quick Setup

### Option 1: Automated Setup (Easiest)

**For Windows:**
```bash
setup.bat
```

**For Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

This will automatically:
- Set up Python virtual environment
- Install all dependencies
- Create configuration files
- Start both backend and frontend servers

### Option 2: Manual Setup

1. **Clone and navigate:**
   ```bash
   git clone https://github.com/Jinish2170/Web-Assistant-AI.git
   cd Web-Assistant-AI
   ```

2. **Setup Backend:**
   ```bash
   cd backend
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Setup Frontend:**
   ```bash
   cd frontend
   npm install
   ```

4. **Configure Environment:**
   - Copy `backend/.env.example` to `backend/.env`
   - Add your OpenAI API key to the `.env` file
   - Copy `frontend/.env.example` to `frontend/.env`

5. **Start Servers:**
   
   **Backend (Terminal 1):**
   ```bash
   cd backend
   venv\Scripts\activate  # Windows
   python -m uvicorn main:app --reload --port 8000
   ```
   
   **Frontend (Terminal 2):**
   ```bash
   cd frontend
   npm start
   ```

## 🎉 Access Your AI Assistant

Once both servers are running:

- **Web App**: http://localhost:3000
- **API Documentation**: http://localhost:8000/api/docs
- **Backend API**: http://localhost:8000

## 🔑 Important Configuration

### Add Your OpenAI API Key

Edit `backend/.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

Without an API key, the system will still work but with limited AI capabilities using local models.

## ✨ First Steps

1. **Chat Interface**: Start by typing a message like "Hello, what can you do?"
2. **Upload Files**: Drag and drop PDF or text files to teach DariusAI
3. **Voice Interaction**: Click the microphone to speak with DariusAI
4. **Web Search**: Use the web search feature to research topics in real-time
5. **Calculations**: Ask for mathematical calculations or data analysis

## 🆘 Troubleshooting

### Common Issues:

**"Module not found" errors:**
- Make sure you activated the Python virtual environment
- Reinstall requirements: `pip install -r requirements.txt`

**Frontend won't start:**
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

**API connection errors:**
- Make sure backend is running on port 8000
- Check firewall settings
- Verify CORS settings in backend configuration

**Voice features not working:**
- Make sure you're using HTTPS or localhost
- Check browser permissions for microphone access
- Modern browsers required (Chrome, Firefox, Edge)

### Getting Help:

- Check the console logs (F12 in browser)
- Review terminal output for error messages
- Create an issue on GitHub with error details

## 🚀 Next Steps

Once you're up and running:

1. **Explore Features**: Try all the different capabilities
2. **Customize Settings**: Modify configuration files for your needs
3. **Add Content**: Upload your documents to build a knowledge base
4. **Integrate**: Use the API endpoints to integrate with other applications
5. **Contribute**: Help improve DariusAI by contributing to the project

## 📚 Additional Resources

- **Full Documentation**: See README.md
- **API Reference**: Visit http://localhost:8000/api/docs when running
- **GitHub Issues**: Report bugs or request features
- **Discord Community**: Join our development discussions

---

**Happy AI Assisting! 🤖✨**
