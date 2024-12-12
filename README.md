# API Sniper

A lightweight Python tool for reliably mimicking browser-initiated API calls.

## Features

- Mimics browser API calls with correct headers, cookies, tokens, and user agents
- Handles various authentication schemes (Bearer tokens, OAuth2, Basic Auth, API keys)
- Session state management and persistence
- Automatic response parsing and validation
- Configurable retry logic and error handling
- Request pattern recording and replay

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from api_sniper import APISniper, SniperConfig

# Initialize with basic configuration
config = SniperConfig(base_url="https://api.example.com", timeout=10)
sniper = APISniper(config)

# Make a simple GET request
response_data = sniper.get("/api/data")
print(response_data)  # Parsed JSON response

# Authenticated request
sniper.login(username="user", password="secret")
user_data = sniper.get("/api/user/profile")
print(user_data)
```

## License

MIT License