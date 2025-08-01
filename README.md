# Perplexity CLI

A command-line interface replica of Perplexity AI with conversation memory and intelligent internet-powered chat.

## Quick Start

### Local Development

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd perlexity-cli
   ```

2. **Set up environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

3. **Configure API keys:**

   ```bash
   export OPENAI_API_KEY='your-openai-api-key'
   export SERPAPI_KEY='your-serpapi-key'
   ```

4. **Run the CLI:**

   ```bash
   perplexity-cli chat start
   ```

## Documentation

For detailed usage instructions, commands, and features, see the [CLI Documentation](src/cli/README.md).
