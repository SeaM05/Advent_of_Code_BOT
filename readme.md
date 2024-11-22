# Advent of Code Discord Leaderboard Bot

## Overview
This Discord bot provides real-time tracking and interaction for Advent of Code leaderboards using slash commands.

## Features
- `/leaderboard`: Display current Advent of Code leaderboard
- `/rank [player]`: Check a specific player's ranking
- `/keen`: Find today's top performer
- `/daily`: View daily challenge leaderboard
- `/remind`: Get time until next challenge
- `/join`: Retrieve login and leaderboard information

## Prerequisites
- Python 3.8+
- Discord account
- Discord Developer Portal application
- Advent of Code account

## Setup Instructions

### 1. Discord Configuration
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and name your bot
3. Navigate to "Bot" section
   - Click "Add Bot"
   - Generate and copy bot token (DISCORD_TOKEN)
   - Enable "Message Content Intent" and "Slash Commands"
4. Navigate to "OAuth2 > General" 
   - Copy Client ID (DISCORD_CLIENT_ID)
5. Use OAuth2 URL Generator to invite bot to server

### 2. Advent of Code Leaderboard Setup
1. Log into [Advent of Code](https://adventofcode.com/)
2. Open browser developer tools (F12)
3. Go to Cookies section
4. Find `session` cookie value (AOC_COOKIE)
5. Navigate to your private leaderboard
6. Copy leaderboard code from URL (AOC_LEADERBOARD_CODE)
7. Get leaderboard JSON URL (AOC_URL):
   ```
   https://adventofcode.com/YEAR/leaderboard/private/view/YOUR_LEADERBOARD_ID.json
   ```

### 3. Environment Variables
Create a `.env` file in project root:
```
DISCORD_TOKEN=your_discord_bot_token
DISCORD_CLIENT_ID=your_discord_client_id
AOC_URL=https://adventofcode.com/YEAR/leaderboard/private/view/YOUR_LEADERBOARD_ID.json
AOC_COOKIE=your_session_cookie_value
AOC_LEADERBOARD_CODE=your_private_leaderboard_code
```

### 4. Dependencies
```bash
pip install -U discord.py python-dotenv
```

### 5. Running the Bot
```bash
python main.py
```

## Security Notes
- Never share your `.env` file
- Keep `AOC_COOKIE` and `DISCORD_TOKEN` confidential
- Use `.gitignore` to prevent accidental commits

## Contributing
1. Fork repository
2. Create feature branch
3. Commit changes
4. Push and submit pull request

## Disclaimer
Complies with Advent of Code's API usage guidelines