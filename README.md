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
    - `marvin`
    - `python-osc`
    - `pydantic`

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

To start Ableton Buddy, run the following command:

```bash
python3 src/main.py
```

## Features

*   **Natural language interaction:** Control Ableton Live with simple, natural language commands.
*   **Real-time control:** See your changes reflected in Ableton Live in real-time.
*   **Extensible:** Easily add new tools and features to expand Ableton Buddy's capabilities.
*   **Comprehensive Song Control:**
    - Play, stop, and continue playback.
    - Set tempo, and tap tempo.
    - Control the metronome.
    - Create, delete, and duplicate tracks and scenes.
    - And much more!
*   **Query Ableton Live's State:**
    - Get the current tempo, playback state, and song time.
    - Get the names of tracks and the number of tracks and scenes.
    - And much more!