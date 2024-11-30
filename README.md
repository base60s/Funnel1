# Funnel1

An AI agent chatbot for blockchain interactions and Twitter integration using Claude.

## Features

- Blockchain interaction capabilities
- Twitter integration for posting tweets
- Claude AI integration for natural language processing
- RESTful API interface

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your credentials:
```
CLAUDE_API_KEY=your_claude_api_key
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_SECRET=your_twitter_access_secret
WEB3_PROVIDER_URL=your_web3_provider_url
```

4. Run the server: `python main.py`

## Usage

The agent can be interacted with through the REST API:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Post a tweet about Ethereum price"}'
```

## Architecture

The project follows a modular architecture:
- `main.py`: Application entry point
- `agent/`: Core agent implementation
- `services/`: External service integrations
- `utils/`: Utility functions