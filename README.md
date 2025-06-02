# Anthropic API Proxy for Gemini & OpenAI Models 🔄

**Use Anthropic clients (like Claude Code) with Gemini or OpenAI backends.** 🤝

A proxy server that lets you use Anthropic clients with Gemini or OpenAI models via LiteLLM. 🌉


![Anthropic API Proxy](pic.png)

## Quick Start ⚡

### Prerequisites

- LiteLLM Proxy Server and API Key 
- [uv](https://github.com/astral-sh/uv) installed.

### Setup 🛠️

1. **Clone this repository**:
   ```bash
   git clone https://github.com/1rgs/claude-code-openai.git
   cd claude-code-openai
   ```

2. **Install uv** (if you haven't already):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   *(`uv` will handle dependencies based on `pyproject.toml` when you run the server)*

3. **Configure Environment Variables**:
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and fill in your API keys and model configurations:

   *   `OPENAI_API_KEY`: Your LiteLLM API key (Required).
   *   `OPENAI_API_BASE`: Your LiteLLM server URL (Required).
   *   `PREFERRED_PROVIDER`: Set to `openai` (default). This determines the primary backend for mapping `haiku`/`sonnet`.
   *   `BIG_MODEL` (Optional): The model to map `sonnet` requests to. Defaults to `anthropic/claude-sonnet-4-20250514`.
   *   `SMALL_MODEL` (Optional): The model to map `haiku` requests to. Defaults to `anthropic/claude-3-5-haiku-latest`.

4. **Run the server**:
   ```bash
   uv run uvicorn server:app --host 0.0.0.0 --port 8082 --reload
   ```
   *(`--reload` is optional, for development)*

### Using with Claude Code 🎮

1. **Install Claude Code** (if you haven't already):
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **Connect to your proxy**:
   ```bash
   ANTHROPIC_BASE_URL=http://localhost:8082 claude
   ```

3. **That's it!** Your Claude Code client will now use the configured backend models (defaulting to OpenAI) through the proxy. 🎯

### Architecture 🏗️

This setup allows you to chain proxies: `Claude Code` → `This Proxy` → `LiteLLM Proxy` → `Multiple LLM Providers` 🔄

## Model Mapping 🗺️

The proxy automatically maps Claude models to every model available based on the configured model:

### Model Prefix Handling
The proxy automatically adds the appropriate prefix to model names:
- OpenAI models get the `openai/` prefix 
- Gemini models get the `gemini/` prefix
- The BIG_MODEL and SMALL_MODEL will get the appropriate prefix based on whether they're in the OpenAI or Gemini model lists

For example:
- `gpt-4o` becomes `openai/gpt-4o`
- `gemini-2.5-pro-preview-03-25` becomes `gemini/gemini-2.5-pro-preview-03-25`
- When BIG_MODEL is set to a Gemini model, Claude Sonnet will map to `gemini/[model-name]`

## How It Works 🧩

This proxy leverages **LiteLLM** to provide seamless translation between different LLM providers while maintaining Anthropic API compatibility.

### LiteLLM Integration 🔗

The proxy is built on top of [LiteLLM](https://github.com/BerriAI/litellm), a unified interface for calling 100+ LLM APIs. This provides several key benefits:

- **Universal Provider Support**: Connect to OpenAI, Google (Gemini), Anthropic, Azure, AWS Bedrock, and many other providers
- **Automatic Format Translation**: LiteLLM handles the conversion between different API formats automatically
- **Consistent Response Structure**: All providers return responses in a standardized format
- **Built-in Error Handling**: Robust error handling and retry logic across providers

### Request Flow 🌊

The proxy works by:

1. **Receiving requests** in Anthropic's API format 📥
2. **Model mapping** - translates Claude model names (haiku/sonnet) to target provider models 🗺️
3. **LiteLLM processing** - uses LiteLLM's unified interface to call the target provider 🔄
4. **Response formatting** - converts LiteLLM's standardized response back to Anthropic format 🔄
5. **Returning** the formatted response to the client ✅

### Key Features 🚀

- **Streaming Support**: Full support for streaming responses via LiteLLM's streaming capabilities
- **Provider Fallbacks**: Can fallback between providers (e.g., Google → OpenAI) if needed
- **Model Prefix Handling**: Automatically adds provider prefixes (`openai/`, `gemini/`) for LiteLLM routing
- **Flexible Configuration**: Environment-based configuration for easy provider switching
- **Chain-able**: Can proxy to other LiteLLM instances for complex routing scenarios

The proxy maintains full compatibility with all Claude clients while providing access to the entire LiteLLM ecosystem. 🌟

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request. 🎁
