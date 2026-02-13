# User Guide: "Always-On" AI Assistant

A voice-controlled personal AI assistant that converts natural language into executable CLI commands, powered by DeepSeek V3, RealtimeSTT, and Typer.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
  - [API Keys](#api-keys)
  - [Assistant Configuration](#assistant-configuration)
- [Getting Started](#getting-started)
  - [Typer Assistant (Voice-to-Command)](#typer-assistant-voice-to-command)
  - [Base Assistant (Conversational Chat)](#base-assistant-conversational-chat)
- [How It Works](#how-it-works)
  - [Typer Assistant Workflow](#typer-assistant-workflow)
  - [Wake Word](#wake-word)
  - [Execution Modes](#execution-modes)
  - [The Scratchpad](#the-scratchpad)
- [Available CLI Commands](#available-cli-commands)
  - [User Management](#user-management)
  - [Task Management](#task-management)
  - [File Operations](#file-operations)
  - [Database Operations](#database-operations)
  - [Data Security](#data-security)
  - [Server and Monitoring](#server-and-monitoring)
- [Customization](#customization)
  - [Changing the LLM Backend](#changing-the-llm-backend)
  - [Changing the Voice Backend](#changing-the-voice-backend)
  - [Tuning Speech Recognition](#tuning-speech-recognition)
  - [Adding Custom Commands](#adding-custom-commands)
  - [Using Context Files](#using-context-files)
- [Example Interactions](#example-interactions)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Python 3.10 - 3.11** (3.11 recommended)
- **uv** package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
- **A microphone** for voice input
- **DeepSeek API key** (required for the Typer Assistant)
- **ElevenLabs API key** (optional, for cloud text-to-speech)
- **Ollama** (optional, for local LLM inference in the Base Assistant)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd always-on-ai-assistant
```

2. Copy the environment template and add your API keys:

```bash
cp .env.sample .env
```

3. Edit `.env` and fill in your keys:

```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
ELEVEN_API_KEY=your_elevenlabs_api_key_here
```

4. Install dependencies:

```bash
uv sync
```

5. (Optional) Install Python 3.11 if you don't have it:

```bash
uv python install 3.11
```

## Configuration

### API Keys

| Key | Required For | How to Obtain |
|-----|-------------|---------------|
| `DEEPSEEK_API_KEY` | Typer Assistant (command generation) | [DeepSeek Platform](https://platform.deepseek.com/) |
| `ELEVEN_API_KEY` | Cloud text-to-speech | [ElevenLabs](https://elevenlabs.io/) |

### Assistant Configuration

All assistant behavior is controlled by `assistant_config.yml`:

```yaml
typer_assistant:
  assistant_name: Ada          # Wake word / assistant name
  human_companion_name: Dan    # Your name (used in voice responses)
  ears: realtime-stt           # Speech-to-text engine
  brain: deepseek-v3           # LLM backend (only deepseek-v3 supported)
  voice: elevenlabs            # TTS backend: "local" or "elevenlabs"
  elevenlabs_voice: WejK3H1m7MI9CHnIjW9K  # ElevenLabs voice ID

base_assistant:
  assistant_name: Ada          # Wake word / assistant name
  human_companion_name: Dan    # Your name
  ears: realtime-stt           # Speech-to-text engine
  brain: ollama:phi4           # LLM backend: "deepseek-v3" or "ollama:<model>"
  voice: local                 # TTS backend: "local", "elevenlabs", or "realtime-tts"
  elevenlabs_voice: WejK3H1m7MI9CHnIjW9K
```

Edit these values to personalize the assistant's name, your name, and which backends to use.

## Getting Started

### Typer Assistant (Voice-to-Command)

The Typer Assistant listens for your voice, interprets natural-language requests, generates CLI commands, and optionally executes them.

**Quick start using the shell script:**

```bash
bash ada.sh
```

**Or run directly with options:**

```bash
uv run python main_typer_assistant.py awaken \
  --typer-file commands/template.py \
  --scratchpad scratchpad.md \
  --mode execute
```

**Options:**

| Flag | Short | Description |
|------|-------|-------------|
| `--typer-file` | `-f` | Path to the file containing Typer CLI commands |
| `--scratchpad` | `-s` | Path to the markdown scratchpad (active memory) |
| `--context` | `-c` | Additional context files (can be specified multiple times) |
| `--mode` | `-m` | Execution mode: `default`, `execute`, or `execute-no-scratch` |

**Health check:**

```bash
uv run python main_typer_assistant.py ping
```

### Base Assistant (Conversational Chat)

The Base Assistant provides a simple conversational chat interface with voice input and output. It maintains conversation history in memory for multi-turn dialogue.

```bash
uv run python main_base_assistant.py chat
```

Say "exit" or "quit" to end the session, or press `Ctrl+C`.

## How It Works

### Typer Assistant Workflow

```
You speak    -->  RealtimeSTT transcribes  -->  Wake word check
                                                    |
                                              (contains "Ada"?)
                                                    |
                                                   Yes
                                                    |
                                           Build prompt from:
                                           - Available CLI commands
                                           - Scratchpad context
                                           - Context files
                                           - Your request
                                                    |
                                           DeepSeek generates
                                           a CLI command
                                                    |
                                           Execute (if mode allows)
                                                    |
                                           Record to scratchpad
                                                    |
                                           Speak feedback via TTS
```

1. **Listen** - RealtimeSTT continuously listens and transcribes your speech.
2. **Filter** - Only processes input that contains the assistant's name (wake word).
3. **Generate** - Sends a prompt to DeepSeek V3 containing the available commands, scratchpad context, and your request. DeepSeek generates the correct CLI command.
4. **Execute** - Depending on the mode, runs the generated command in the shell.
5. **Record** - Appends the request, generated command, and output to the scratchpad.
6. **Respond** - Generates a short voice response and speaks it using the configured TTS engine.

### Wake Word

The assistant only processes speech that contains its name. By default, this is **"Ada"**. You must include the name in your speech for the assistant to act.

Examples:
- "Ada, ping the server" -- processed
- "Ada, list all users" -- processed
- "ping the server" -- ignored

Change the wake word by editing `assistant_name` in `assistant_config.yml`.

### Execution Modes

| Mode | Generates Command | Executes | Records to Scratchpad |
|------|:-:|:-:|:-:|
| `default` | Yes | No | Yes |
| `execute` | Yes | Yes | Yes |
| `execute-no-scratch` | Yes | Yes | No |

- **`default`** - Safe mode. Generates the command and writes it to the scratchpad, but does not execute it. Good for reviewing commands before running them.
- **`execute`** - Full automation. Generates, executes, and records everything to the scratchpad. This is the most common mode.
- **`execute-no-scratch`** - Generates and executes, but does not write anything to the scratchpad.

### The Scratchpad

The scratchpad (`scratchpad.md`) is a markdown file that acts as the assistant's active memory. Every interaction in `default` and `execute` mode is appended to it with timestamps.

**What gets recorded:**
- Your natural-language request
- The generated CLI command
- The command's output (in `execute` mode)

**Why it matters:**
- The scratchpad is included in every prompt sent to the LLM, so the assistant has context about past interactions.
- You can manually edit the scratchpad to add instructions, notes, or data that the assistant should reference.
- You can write structured blocks (like a list of users to create/delete) and ask the assistant to process them.

**Example scratchpad entry:**

```markdown
## Ada Executed Command (2025-01-11 13:31:51)

> Request: Ada, list users that are viewers.

**Ada's Command:**
​```bash
uv run python commands/template.py list-users --role viewer
​```

**Output:**
​```
Users:
- user_4 (Role: viewer, Created: 2025-01-11T10:14:21)
- user_9 (Role: viewer, Created: 2025-01-11T10:14:21)
​```
```

## Available CLI Commands

The default command set is defined in `commands/template.py`. These are the commands the assistant can generate and execute.

### User Management

| Command | Description | Key Options |
|---------|-------------|-------------|
| `list-users` | List all users | `--role <role>` filter by role, `--sort <field>` sort by username/role/created_at |
| `create-user <username>` | Create a new user | `--role <role>` (default: guest) |
| `delete-user <user_id>` | Delete a user by ID | `--confirm` required to actually delete |

### Task Management

| Command | Description | Key Options |
|---------|-------------|-------------|
| `list-tasks` | List tasks | `--all` include completed, `--sort-by <field>` |
| `queue-task <name>` | Queue a new task | `--priority <n>`, `--delay <seconds>` |
| `remove-task <id>` | Remove a task | `--force` skip confirmation |
| `inspect-task <id>` | View task details | `--json` for JSON output |

### File Operations

| Command | Description | Key Options |
|---------|-------------|-------------|
| `list-files <path>` | List directory contents | `--all` include hidden files |
| `compare-files <a> <b>` | Diff two files | `--diff-only` show only differences |
| `upload-file <path>` | Upload a file | `--destination <label>`, `--secure` |
| `download-file <url>` | Download a file | `--output <path>`, `--retry <n>` |

### Database Operations

| Command | Description | Key Options |
|---------|-------------|-------------|
| `generate-report <table>` | Generate a JSON report from a table | `--output <file>` |
| `filter-records <table>` | Search records in a table | `--query <text>`, `--limit <n>` |
| `backup-data <dir>` | Back up the database | `--full` for full backup |
| `restore-data <file>` | Restore from backup | `--overwrite` required |
| `migrate-database <old_db>` | Migrate to a new database | `--new-db <path>`, `--dry-run` |

### Data Security

| Command | Description | Key Options |
|---------|-------------|-------------|
| `encrypt-data <file>` | Encrypt a file | `--output <file>`, `--algorithm <alg>` |
| `decrypt-data <file>` | Decrypt a file | `--key <key>`, `--output <file>` |

### Server and Monitoring

| Command | Description | Key Options |
|---------|-------------|-------------|
| `ping-server` | Ping the server | `--wait` wait for response |
| `show-config` | Display current config | `--verbose` for detailed JSON |
| `summarize-logs <path>` | Summarize a log file | `--lines <n>` limit output |

## Customization

### Changing the LLM Backend

**Typer Assistant:** Only supports DeepSeek V3 (uses the prefix-constrained generation feature).

**Base Assistant:** Supports DeepSeek V3 or any Ollama model. Edit `assistant_config.yml`:

```yaml
base_assistant:
  brain: ollama:phi4          # Use local phi4 model
  # brain: ollama:llama3      # Or any other Ollama model
  # brain: deepseek-v3        # Or cloud DeepSeek
```

To use Ollama, install it first and pull your desired model:

```bash
ollama pull phi4
```

### Changing the Voice Backend

Three TTS options are available:

| Backend | Config Value | Description |
|---------|-------------|-------------|
| Local pyttsx3 | `local` | Free, offline, lower quality |
| ElevenLabs | `elevenlabs` | High quality cloud TTS (requires API key) |
| RealtimeTTS | `realtime-tts` | Streaming local TTS (Base Assistant only) |

Edit `assistant_config.yml`:

```yaml
typer_assistant:
  voice: local          # Switch to local TTS
  # voice: elevenlabs   # Or use ElevenLabs
```

To change the ElevenLabs voice, update the `elevenlabs_voice` field with a different voice ID from your ElevenLabs account.

### Tuning Speech Recognition

Speech recognition parameters are configured in `main_typer_assistant.py` inside the `AudioToTextRecorder` constructor:

```python
recorder = AudioToTextRecorder(
    model="tiny.en",                    # Whisper model size
    post_speech_silence_duration=1.5,   # Seconds of silence before processing
    beam_size=8,                        # Higher = more accurate, slower
    batch_size=25,                      # Higher = faster, more memory
    language="en",
)
```

**Model options** (speed vs. accuracy tradeoff):

| Model | Speed | Accuracy | Notes |
|-------|-------|----------|-------|
| `tiny.en` | ~0.5s | Lower | Default, best for fast interactions |
| `small.en` | ~1.5s | Medium | Good balance |
| `large-v3` | Slow | High | Best accuracy, requires more resources |
| `distil-large-v3` | Moderate | High | Faster than large-v3 |

### Adding Custom Commands

You can define your own CLI commands for the assistant to use.

**Option 1: Edit the existing template**

Add new `@app.command()` functions to `commands/template.py`.

**Option 2: Create a new command file**

1. Copy the empty template:

```bash
cp commands/template_empty.py commands/my_commands.py
```

2. Add your Typer commands to the new file. Each command should follow this pattern:

```python
@app.command()
def my_command(
    arg: str = typer.Argument(..., help="Description of the argument"),
    flag: bool = typer.Option(False, "--flag", help="Description of the flag"),
):
    """
    Description of what this command does.
    """
    # Your implementation here
    result = f"Did something with {arg}"
    typer.echo(result)
    return result
```

3. Run the assistant with your new command file:

```bash
uv run python main_typer_assistant.py awaken \
  --typer-file commands/my_commands.py \
  --scratchpad scratchpad.md \
  --mode execute
```

**Tips for writing commands:**
- Use descriptive docstrings -- the LLM reads them to understand what each command does.
- Use `typer.Argument` for required positional arguments and `typer.Option` for optional flags.
- Function names use underscores (`create_user`), but the CLI automatically converts them to hyphens (`create-user`).

### Using Context Files

You can pass additional files as context to the assistant, giving it extra information to reference when generating commands:

```bash
uv run python main_typer_assistant.py awaken \
  --typer-file commands/template.py \
  --scratchpad scratchpad.md \
  --context data/notes.txt \
  --context data/config.json \
  --mode execute
```

Context files are injected into the LLM prompt alongside the scratchpad. This is useful for providing reference data, specifications, or any information the assistant might need.

## Example Interactions

Below are real examples from the scratchpad showing how the assistant handles voice requests.

**Simple command:**

> "Ada, ping the server, wait for a response."

Generated command:
```bash
uv run python commands/template.py ping-server --wait
```
Output: `Server pinged. Response time: 211 ms. (Waited for a response.)`

**Filtered query:**

> "Ada, list users that are viewers."

Generated command:
```bash
uv run python commands/template.py list-users --role viewer
```

**Multi-command from scratchpad context:**

> "Ada, go ahead and look at the update user block and run the respective create user and delete user commands."

The assistant read a structured block from the scratchpad and generated a chained command:
```bash
uv run python commands/template.py create-user Alex --role viewer && \
uv run python commands/template.py create-user Mary --role editor && \
uv run python commands/template.py create-user Steve --role admin && \
uv run python commands/template.py delete-user 11 --confirm && \
uv run python commands/template.py delete-user 22 --confirm && \
uv run python commands/template.py delete-user 4 --confirm
```

This demonstrates that the assistant can read structured data from the scratchpad and generate multiple chained commands in a single response.

## Project Structure

```
always-on-ai-assistant/
├── main_typer_assistant.py     # Entry point: voice-to-command assistant
├── main_base_assistant.py      # Entry point: conversational chat assistant
├── ada.sh                      # Shell shortcut to launch the Typer Assistant
├── assistant_config.yml        # Central configuration for both assistants
├── scratchpad.md               # Active memory (command history + context)
├── pyproject.toml              # Project metadata and dependencies
├── .env.sample                 # Environment variable template
│
├── modules/                    # Core application logic
│   ├── typer_agent.py          # Command generation, execution, and TTS
│   ├── base_assistant.py       # Conversational assistant with history
│   ├── deepseek.py             # DeepSeek API wrapper (prefix, FIM, JSON, chat)
│   ├── ollama.py               # Ollama local model wrapper
│   ├── assistant_config.py     # YAML config loader (dot-path access)
│   ├── execute_python.py       # Shell command execution
│   └── utils.py                # Logging, session IDs, file utilities
│
├── commands/                   # CLI command definitions
│   ├── template.py             # Full command set (users, tasks, files, DB, etc.)
│   └── template_empty.py       # Empty template for creating custom commands
│
├── prompts/                    # XML prompt templates for the LLM
│   ├── typer-commands.xml      # Prompt for generating CLI commands
│   └── concise-assistant-response.xml  # Prompt for voice feedback
│
├── tests/                      # Unit tests
│   ├── deepseek_test.py
│   ├── data_types_test.py
│   └── execute_python_test.py
│
├── output/                     # Session logs (auto-generated)
│   └── <session-id>/
│       └── session.log
│
└── ai_docs/                    # Documentation for AI context
    └── ai_docs.md
```

## Troubleshooting

### "Not Ada - ignoring"

The assistant is hearing speech but the wake word ("Ada") was not detected. Speak the name clearly at the beginning or within your sentence.

### Command not found

If the assistant responds with "I couldn't find that command," it means DeepSeek could not map your request to any available CLI command. Try rephrasing your request to more closely match one of the available commands.

### Slow transcription

The default STT model is `tiny.en`, which is fast but less accurate. If you need better accuracy and can tolerate slower response times, switch to `small.en` or `large-v3` in `main_typer_assistant.py`.

### ElevenLabs errors

- Verify your `ELEVEN_API_KEY` is set correctly in `.env`.
- Check your ElevenLabs account has available credits.
- As a fallback, switch to local TTS by setting `voice: local` in `assistant_config.yml`.

### DeepSeek API errors

- Verify your `DEEPSEEK_API_KEY` is set correctly in `.env`.
- Check your DeepSeek account has available credits.
- The Typer Assistant requires DeepSeek V3 specifically (it uses the prefix-constrained generation feature from the beta API).

### Ollama connection errors

If using Ollama for the Base Assistant:
- Ensure Ollama is running: `ollama serve`
- Ensure the model is pulled: `ollama pull phi4`
- Check the model name in `assistant_config.yml` matches an installed model.

### Microphone not detected

- Ensure your system microphone is configured and accessible.
- RealtimeSTT requires system audio input. Check your OS audio settings.
- On Linux, you may need to install PortAudio: `sudo apt-get install portaudio19-dev`

### Scratchpad validation error

The scratchpad must be a markdown file (`.md` or `.markdown` extension) and must exist at the path specified. Create an empty one if needed:

```bash
echo "# Scratchpad" > scratchpad.md
```

### Running tests

```bash
uv run pytest tests/
```
