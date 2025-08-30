@echo off
echo 🤖 DariusAI - Advanced Web Assistant
echo ====================================
echo.

:: Colors (limited in batch)
set "info=[INFO]"
set "success=[SUCCESS]"
set "warning=[WARNING]"
set "error=[ERROR]"

:: Check if Python is installed
echo %info% Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo %error% Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)
echo %success% Python found

:: Check if Node.js is installed
echo %info% Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo %error% Node.js is not installed or not in PATH
    echo Please install Node.js 16 or higher from nodejs.org
    pause
    exit /b 1
)
echo %success% Node.js found

:: Setup Backend
echo.
echo %info% Setting up backend...
cd backend

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo %info% Creating Python virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Upgrade pip
python -m pip install --upgrade pip

:: Install requirements
echo %info% Installing Python dependencies...
pip install -r requirements.txt

:: Copy environment file
if not exist ".env" (
    echo %info% Creating environment file...
    copy .env.example .env
    echo %warning% Please edit backend/.env with your API keys and configuration
)

cd ..
echo %success% Backend setup complete!

:: Setup Frontend
echo.
echo %info% Setting up frontend...
cd frontend

:: Install npm dependencies
echo %info% Installing Node.js dependencies...
npm install

:: Copy environment file
if not exist ".env" (
    echo %info% Creating environment file...
    copy .env.example .env
)

cd ..
echo %success% Frontend setup complete!

echo.
echo %success% 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Edit backend\.env with your OpenAI API key and other settings
echo 2. Edit frontend\.env if needed
echo 3. Run 'start-dev.bat' to start both servers
echo.

:: Ask if user wants to start now
set /p start="Do you want to start the development servers now? (y/n): "
if /i "%start%"=="y" (
    call start-dev.bat
) else (
    echo %info% You can start the servers later by running 'start-dev.bat'
)

pause
