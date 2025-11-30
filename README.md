# Ableton Buddy

Your AI-powered command center for Ableton Live.

## Demo Video

Watch the demo video to see Ableton Buddy in action:

[![Demo Video](final-report/figures/demo_video.mp4)](final-report/figures/demo_video.mp4)

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

4. **Install AbletonOSC (for live mode only):**

   To use Ableton Buddy with Ableton Live, you'll need to install the AbletonOSC Max for Live device:

   - Download from: https://github.com/ideoforms/AbletonOSC
   - Follow the installation instructions in the AbletonOSC repository
   - Load the AbletonOSC device in Ableton Live
   - **Note:** You can skip this step if you want to use simulation mode only

5. **Set up your environment variables:**

   - Create a `.env` file by copying the `.env.example` file:
     ```bash
     cp .env.example .env
     ```
   - Open the `.env` file and add your OpenAI API key. You can also specify a different model for Marvin to use:
     ```
     OPENAI_API_KEY=...
     MARVIN_AGENT_MODEL=anthropic:claude-3-7-sonnet-latest
     ```

6. **Install frontend dependencies:**

   Navigate to the frontend directory and install the required packages:

   ```bash
   cd frontend
   npm install
   ```

   The frontend dependencies include:

   - `react` & `react-dom` - React framework
   - `@chatscope/chat-ui-kit-react` - Chat UI components
   - `react-router-dom` - Client-side routing
   - `react-markdown` - Markdown rendering
   - `tailwindcss` - Utility-first CSS framework
   - `vite` - Build tool and dev server

## Simulation Mode

Ableton Buddy includes a simulation mode that allows you to test and explore the tool's capabilities without having Ableton Live installed. This is perfect for:

- **Testing the interface** - Try out the web UI and CLI without Ableton Live
- **Learning the commands** - Understand what Ableton Buddy can do before purchasing Ableton Live
- **Development and debugging** - Work on the codebase without needing Ableton Live running
- **Demonstrations** - Show off the tool's capabilities to others

### Enabling Simulation Mode

To enable simulation mode, edit the OSC client configuration:

1. **Open the OSC client file:**

   ```bash
   nano src/tools/osc/client.py
   ```

2. **Change line 15 from:**

   ```python
   OSC_AVAILABLE = True # Set to False to run in simulation mode
   ```

   **to:**

   ```python
   OSC_AVAILABLE = False # Set to False to run in simulation mode
   ```

3. **Save the file and restart the application**


## Usage

### CLI Interface

To start Ableton Buddy in CLI mode, run:

```bash
python3 src/main.py
```

You'll be prompted to either start a new conversation or resume an existing one. If resuming, you'll need the thread ID from a previous session.

The CLI now displays only clean, user-friendly messages (your input and the assistant's responses) while all processing happens in the background.

### Web UI (React Frontend)

To run the React frontend:

1. **Start the API server** (in one terminal):

   ```bash
   python3 run_api.py
   ```

2. **Start the frontend development server** (in another terminal):
   ```bash
   cd frontend
   npm run dev
   ```

The frontend will be available at `http://localhost:5173` and will automatically connect to the API server running on `http://localhost:8000`.

**Frontend Development Commands:**

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint for code quality checks

### API Server

To run the API server for the web UI:

```bash
python3 run_api.py
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

**API Endpoints:**

- `GET /` - API health check
- `GET /threads` - List all conversation threads
- `POST /threads` - Create a new thread
- `DELETE /threads/{thread_id}` - Delete a thread and all its messages
- `GET /threads/{thread_id}` - Get thread with filtered messages (user-friendly)
- `GET /threads/{thread_id}/detailed` - Get thread with all messages including metadata
- `POST /threads/{thread_id}/messages` - Add message and get response
- `POST /threads/{thread_id}/stream` - Stream response in real-time (SSE)
- `DELETE /threads/{thread_id}/stream` - Cancel an active stream

## Example Prompts

Here are some example prompts you can try with Ableton Buddy to get started:

### Song Control Examples

**Playback Control:**

- "Play the song"
- "Stop playback"
- "Pause and then continue playing"
- "Stop all clips"

**Tempo and Time:**

- "What's the current tempo?"
- "Set the tempo to 120 BPM"
- "Tap tempo for me"
- "What's the current song time?"
- "Jump to 2 minutes and 30 seconds"

**Recording and Session:**

- "Start session recording"
- "Turn on the metronome"
- "What's the time signature?"
- "Set the time signature to 4/4"
- "Enable loop mode"

**Track and Scene Management:**

- "Create a new MIDI track"
- "Create a new audio track"
- "How many tracks are there?"
- "What are the track names?"
- "Create a new scene"
- "Duplicate the first track"

### Track Control Examples

**Basic Track Operations:**

- "Mute track 1"
- "Solo track 2"
- "What's the volume of track 3?"
- "Set track 1 volume to 80%"
- "Pan track 2 to the left"
- "Arm track 1 for recording"

**Track Information:**

- "What's the name of track 1?"
- "Rename track 2 to 'Bass'"
- "What color is track 3?"
- "Change track 1 color to red"
- "Is track 2 muted?"

**Advanced Track Control:**

- "What devices are on track 1?"
- "What clips are on track 2?"
- "Stop all clips on track 3"
- "What's the send level for track 1?"
- "Set track 1 send to 50%"

**Routing and Monitoring:**

- "What's the input routing for track 1?"
- "Set track 1 to monitor input"
- "What's the output level of track 2?"
- "Fold track 1"

### Complex Workflow Examples

**Setting Up a New Project:**

- "Create 4 MIDI tracks and name them Kick, Snare, Hi-Hat, and Bass"
- "Set the tempo to 128 BPM and enable the metronome"
- "Arm all tracks for recording"
- "Create 8 scenes for my song structure"

**Mixing and Arrangement:**

- "Mute tracks 2 and 4, solo track 1"
- "Set track 1 volume to 70%, track 2 to 60%, track 3 to 80%"
- "Pan track 1 left, track 2 right, track 3 center"
- "What's the current arrangement length?"

**Live Performance Setup:**

- "Stop all clips and set tempo to 100 BPM"
- "Create a new scene called 'Intro'"
- "Arm track 1 and set it to monitor input"
- "Enable session recording"

### Query Examples

**Get Information:**

- "What's the current state of the song?"
- "Show me all track information"
- "What's the loop status?"
- "Are we recording?"
- "What's the groove amount?"

**Check Capabilities:**

- "Can I undo the last action?"
- "What's the clip trigger quantization?"
- "Is the metronome on?"
- "What's the current monitoring state of track 1?"

