# Twilio Automation Hub

An AI-powered platform that builds comprehensive customer service systems using Twilio, SendGrid, and Zendesk, with natural language workflow creation and visual editing capabilities.

## Features

- Natural language input for workflow creation
- Visual workflow editor using React Flow
- Multi-channel support (SMS, Voice, Email, Web Chat)
- AI-powered automation configuration
- Secure client API key management
- Cost tracking and analytics
- One-click cloud deployment

## Tech Stack

- **Frontend**: React.js, TypeScript, Tailwind CSS, React Flow
- **Backend**: Node.js, Express
- **Database**: MongoDB
- **AI**: OpenAI API
- **APIs**: 
  - Twilio (Messaging, Voice, Autopilot, Flex)
  - SendGrid Email API
  - Zendesk Core API

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   # Backend
   cd backend
   npm install
   cp .env.example .env  # Configure your environment variables

   # Frontend
   cd ../frontend
   npm install
   ```

3. Start the development servers:
   ```bash
   # Backend
   cd backend
   npm run dev

   # Frontend
   cd ../frontend
   npm run dev
   ```

4. Visit http://localhost:5173 to access the application

## Environment Variables

Configure the following in your `.env` file:

- `MONGODB_URI`: MongoDB connection string
- `JWT_SECRET`: Secret for JWT authentication
- `OPENAI_API_KEY`: OpenAI API key
- `TWILIO_ACCOUNT_SID`: Twilio Account SID
- `TWILIO_AUTH_TOKEN`: Twilio Auth Token
- `SENDGRID_API_KEY`: SendGrid API key
- `ZENDESK_*`: Zendesk credentials

## License

MIT
