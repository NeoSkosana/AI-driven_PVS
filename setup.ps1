$ErrorActionPreference = "Stop"

Write-Host "Setting up AI-Driven Problem Validation System..."

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..."
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
.\venv\Scripts\Activate

# Install Python dependencies
Write-Host "Installing Python dependencies..."
pip install -r requirements.txt

# Install frontend dependencies
Write-Host "Installing frontend dependencies..."
Set-Location frontend
npm install
Set-Location ..

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..."
    @"
MONGODB_URI=mongodb://localhost:27017/problem_validation
REDIS_HOST=localhost
REDIS_PORT=6379
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASS=guest
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=Problem-Validation-System/1.0
"@ | Out-File -FilePath ".env" -Encoding UTF8
}

Write-Host "Setup complete! To start the application:"
Write-Host "1. Start the services: docker-compose up -d"
Write-Host "2. Start the backend: uvicorn src.main:app --reload"
Write-Host "3. Start the frontend: cd frontend && npm run dev"
