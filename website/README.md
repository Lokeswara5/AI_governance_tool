# AI Governance Tool Website

A real-time, dynamic website for AI policy compliance monitoring and analysis.

## Features

- **Real-time Updates**: Live compliance monitoring using WebSockets
- **Multi-tenant**: Support for multiple organizations
- **Interactive Dashboard**: Real-time visualization of compliance metrics
- **Responsive Design**: Works on desktop and mobile devices
- **API Access**: REST API for integration with other tools
- **Customizable**: Configurable compliance rules and thresholds

## Architecture

- **Frontend**: React with TypeScript
- **Backend**: FastAPI
- **Database**: PostgreSQL
- **Cache**: Redis
- **Real-time**: WebSocket
- **Containerization**: Docker

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/your-username/AI_governance_tool.git
cd AI_governance_tool/website
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Start the services:
```bash
docker-compose up -d
```

4. Access the website:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Admin: http://localhost:8000/admin

## Development

### Frontend

```bash
cd frontend
npm install
npm start
```

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn src.main:app --reload
```

## Configuration

The application can be configured through environment variables or `.env` file:

- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: Secret key for JWT tokens
- `DEBUG`: Enable debug mode (True/False)
- `CORS_ORIGINS`: Allowed origins for CORS
- `UPLOAD_DIR`: Directory for file uploads
- `MIN_COMPLIANCE_SCORE`: Minimum score for compliance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details