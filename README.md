# Ableton Buddy

Your AI-powered command center for Ableton Live.

## Description

Ableton Buddy is a Python-based tool that allows you to interact with Ableton Live using natural language. It uses a large language model to understand your commands and translate them into actions in Ableton Live.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/ableton-buddy.git
   cd ableton-buddy
   ```

2. **Create a virtual environment:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   The dependencies are:

   - `marvin` - AI orchestration framework
   - `python-osc` - OSC communication with Ableton Live
   - `pydantic` - Data validation
   - `fastapi` - API server (optional, for web UI)
   - `uvicorn` - ASGI server (optional, for web UI)
   - `sse-starlette` - Server-sent events for streaming (optional, for web UI)

4. **Set up your environment variables:**
   - Create a `.env` file by copying the `.env.example` file:
     ```bash
     cp .env.example .env
     ```
   - Open the `.env` file and add your OpenAI API key. You can also specify a different model for Marvin to use:
     ```
     OPENAI_API_KEY=...
     MARVIN_AGENT_MODEL=anthropic:claude-3-7-sonnet-latest
     ```

## Usage

### CLI Interface

To start Ableton Buddy in CLI mode, run:

```bash
python3 src/main.py
```

You'll be prompted to either start a new conversation or resume an existing one. If resuming, you'll need the thread ID from a previous session.

The CLI now displays only clean, user-friendly messages (your input and the assistant's responses) while all processing happens in the background.

### API Server (for Web UI)

To run the API server for future React frontend integration:

```bash
python3 run_api.py
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

**API Endpoints:**

- `GET /threads` - List all conversation threads
- `POST /threads` - Create a new thread
- `GET /threads/{thread_id}` - Get thread with messages
- `POST /threads/{thread_id}/messages` - Add message and get response
- `POST /threads/{thread_id}/stream` - Stream response in real-time (SSE)

## Features

- **Natural language interaction:** Control Ableton Live with simple, natural language commands.
- **Conversation persistence:** All conversations are automatically saved to a SQLite database.
- **Resume conversations:** Continue previous sessions by providing a thread ID.
- **Clean UI:** See only what matters - your input and assistant responses.
- **Real-time streaming:** Watch the assistant work in real-time (via API).
- **REST API:** Ready for React frontend integration with SSE streaming support.
- **Real-time control:** See your changes reflected in Ableton Live in real-time.
- **Extensible:** Easily add new tools and features to expand Ableton Buddy's capabilities.
- **Comprehensive Song Control:**
  - Play, stop, and continue playback.
  - Set tempo, and tap tempo.
  - Control the metronome.
  - Create, delete, and duplicate tracks and scenes.
  - And much more!
- **Query Ableton Live's State:**
  - Get the current tempo, playback state, and song time.
  - Get the names of tracks and the number of tracks and scenes.
  - And much more!

## Architecture

### Thread Persistence

Ableton Buddy uses Marvin's built-in SQLite database to automatically persist all conversations. Each conversation is stored as a thread with a unique ID that can be used to resume the conversation later.

The database file `ableton_buddy.db` is created automatically in the project root directory.

### Message Filtering

To provide a clean user experience, the system filters messages to show only:

- User input messages
- Final assistant responses (summaries)

Internal processing messages (classification, extraction, task execution) are stored in the database but hidden from the CLI and API responses by default.
