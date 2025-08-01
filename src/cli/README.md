# Perplexity CLI

A command-line interface replica of Perplexity AI with conversation memory and intelligent chat capabilities.

## 🚀 Quick Install

### One-line install (recommended)

```bash
curl -sSL https://raw.githubusercontent.com/megh-khaire/perplexity-cli/main/install.sh | bash
```

### Install from GitHub

```bash
pip install git+https://github.com/megh-khaire/perplexity-cli.git
```

### Install from source

```bash
git clone https://github.com/megh-khaire/perplexity-cli.git
cd perplexity-cli
pip install -e .
```

## ⚙️ Setup

1. **Set up your OpenAI API key:**

   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

2. **Set up your SerpAPI key for internet search:**

   ```bash
   export SERPAPI_KEY='your-serpapi-key-here'
   ```

   Get your free SerpAPI key at: <https://serpapi.com/>

   Or add both keys to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

   ```bash
   echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
   echo 'export SERPAPI_KEY="your-serpapi-key-here"' >> ~/.bashrc
   source ~/.bashrc
   ```

## 💬 Usage

### Start a New Conversation

Start a fresh conversation with the AI:

```bash
perplexity-cli chat start
```

With a custom title:

```bash
perplexity-cli chat start --title "My Research Session"
```

### Resume an Existing Conversation

Resume from where you left off. Shows an interactive menu to select from recent conversations:

```bash
perplexity-cli chat resume
```

Resume a specific conversation by ID:

```bash
perplexity-cli chat resume --session abc12345
```

### View Conversation History

List all your conversations:

```bash
perplexity-cli chat history
```

Limit the number of conversations shown:

```bash
perplexity-cli chat history --limit 5
```

Search through your conversations:

```bash
perplexity-cli chat history --search "python programming"
```

### Show a Specific Conversation

View details and full message history of a conversation:

```bash
perplexity-cli chat show abc12345
```

### Export Conversations

Export a conversation to JSON format:

```bash
perplexity-cli chat export abc12345
```

Export to a specific file:

```bash
perplexity-cli chat export abc12345 --output my-conversation.json
```

### Clear Conversations

Clear a specific conversation:

```bash
perplexity-cli chat clear --session abc12345
```

Clear all conversations (use with caution):

```bash
perplexity-cli chat clear --all
```

## 🎮 Interactive Chat Commands

Once you're in a chat session, you can use these special commands:

- **`/help`** - Show available chat commands
- **`/export`** - Export current conversation to JSON
- **`/clear`** - Delete current conversation
- **`history`** - Show full conversation history
- **`exit`**, **`quit`**, or **`bye`** - End the chat session

## 📁 Data Storage

- Conversations are stored locally in SQLite database
- Default location: `~/.perplexity-cli/conversations.db`
- Custom location via environment variable: `PERPLEXITY_CLI_DB_PATH`

## 🔧 Configuration

Set custom configuration via environment variables:

```bash
# Database location
export PERPLEXITY_CLI_DB_PATH="/path/to/custom/db"

# Configuration file location
export PERPLEXITY_CLI_CONFIG_PATH="~/.perplexity-cli/config.yml"

# Maximum conversation history to keep
export PERPLEXITY_CLI_MAX_HISTORY=100
```

## 💡 Features

- **Internet-Powered Chat**: Every message searches the web for current information
- **Intelligent Query Analysis**: Automatically breaks down complex questions
- **Multi-Source Research**: Searches multiple queries to gather comprehensive info
- **Persistent Memory**: All conversations are saved and can be resumed
- **Context Awareness**: AI remembers the full conversation history
- **Interactive Selection**: Easy-to-use conversation picker
- **Rich CLI**: Beautiful formatted output with colors and panels
- **Export/Import**: JSON export for conversation backup
- **Search**: Full-text search through conversation history
- **Real-time Streaming**: Responses stream in real-time like ChatGPT
- **Cross-platform**: Works on macOS, Linux, and Windows

## 🔍 Examples

### Internet-Powered Research Session

```bash
# Start a research conversation
perplexity-cli chat start --title "Climate Change Research"

# In chat:
# You: "What are the latest developments in climate change for 2024?"
# Assistant: [Searches the internet and provides current information with sources]
# You: "How do these compare to previous years?"
# Assistant: [Searches for historical data and provides contextual comparison]
```

### Resume Previous Work

```bash
# List recent conversations
perplexity-cli chat history

# Resume the most relevant one
perplexity-cli chat resume --session abc12345
```

### Export for Documentation

```bash
# Export important conversations
perplexity-cli chat export abc12345 --output research-notes.json
```

## 🆘 Help

Get help with any command:

```bash
perplexity-cli --help
perplexity-cli chat --help
perplexity-cli chat start --help
```

## 🐛 Troubleshooting

**API Key Error**: Make sure your OpenAI API key is set correctly:

```bash
echo $OPENAI_API_KEY
```

**Database Issues**: Delete and recreate the database:

```bash
rm ~/.perplexity-cli/conversations.db
```

**Installation Issues**: Try reinstalling in a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```
