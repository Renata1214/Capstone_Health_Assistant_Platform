# 🧠 Brain - AI Agent Orchestrator

An intelligent orchestrator system that routes user queries to specialized AI agents using OpenRouter API.

## Features

- **Orchestrator Agent**: Intelligently routes requests to specialized agents
- **Daily Stats Agent**: Tracks and reports daily metrics (activity, sleep, mood, productivity)
- **Well-Being Agent**: Provides holistic health and wellness support
- **Terminal Interface**: Simple CLI for conversational interaction
- **OpenRouter API**: Uses OpenRouter for flexible model selection

## Architecture

```
User Input
    ↓
Orchestrator Agent (routes request)
    ↓
├── Daily Stats Agent
├── Well-Being Agent
└── General Handler
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenRouter API key:

```
OPENROUTER_API_KEY=your_openrouter_api_key_here
MODEL_NAME=anthropic/claude-3.5-sonnet
```

You can get an OpenRouter API key at: https://openrouter.ai/

### 3. Run the Application

```bash
python main.py
```

## Usage

### Commands

- `quit` or `exit` - Exit the program
- `reset` - Clear all conversation history
- `help` - Show help message

### Example Conversations

**Daily Stats:**
```
You: How many steps did I take today?
[Routing to Daily Stats Agent]
...
```

**Well-Being:**
```
You: I'm feeling stressed. Any tips?
[Routing to Well-Being Agent]
...
```

**General:**
```
You: Hello!
[General Response]
...
```

## Project Structure

```
brain/
├── main.py              # CLI interface
├── orchestrator.py      # Orchestrator agent
├── agents.py           # Specialized agent classes
├── requirements.txt    # Python dependencies
├── .env.example       # Environment template
├── .gitignore         # Git ignore file
└── README.md          # This file
```

## Agent Descriptions

### Orchestrator Agent
- Routes user queries to appropriate specialized agents
- Uses LLM to classify intent
- Handles general queries directly

### Daily Stats Agent
Specializes in:
- Daily activity levels
- Sleep patterns
- Mood tracking
- Productivity metrics
- Health indicators
- Exercise and fitness data

### Overall Well-Being Agent
Specializes in:
- Mental health and emotional wellness
- Physical health and fitness
- Work-life balance
- Stress management
- Personal growth
- Social connections

## Extending the System

### Adding New Agents

1. Create a new agent class in `agents.py`:

```python
class NewAgent(BaseAgent):
    def __init__(self):
        name = "New Agent"
        role = "Your role description"
        instructions = "Your detailed instructions"
        super().__init__(name, role, instructions)
```

2. Register the agent in `orchestrator.py`:

```python
self.new_agent = NewAgent()
self.agents["new_agent"] = self.new_agent
```

3. Update the routing logic in `route_request()`

## Configuration

### Model Selection

You can change the AI model by updating `MODEL_NAME` in `.env`:

```
MODEL_NAME=anthropic/claude-3.5-sonnet
# or
MODEL_NAME=openai/gpt-4
# or
MODEL_NAME=google/gemini-pro
```

See available models at: https://openrouter.ai/models

## Troubleshooting

### API Key Issues
- Ensure your `.env` file exists and contains a valid `OPENROUTER_API_KEY`
- Check that the key has proper permissions

### Import Errors
- Run `pip install -r requirements.txt`
- Ensure you're using Python 3.8+

### Connection Issues
- Check your internet connection
- Verify OpenRouter API status

## License

MIT

## Contributing

Feel free to open issues or submit pull requests!
# capstone_orch
