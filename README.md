# Anthropic API Proxy for Gemini & OpenAI Models 🔄

**Use Anthropic clients (like Claude Code) with Gemini or OpenAI backends.** 🤝

A proxy server that lets you use Anthropic clients with Gemini or OpenAI models via LiteLLM. 🌉


![Anthropic API Proxy](pic.png)

## Quick Start ⚡

### Prerequisites

- OpenAI API key 🔑
- Google AI Studio (Gemini) API key (if using Google provider) 🔑
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

   *   `ANTHROPIC_API_KEY`: (Optional) Needed only if proxying *to* Anthropic models.
   *   `OPENAI_API_KEY`: Your OpenAI API key (Required if using the default OpenAI preference or as fallback).
   *   `OPENAI_API_BASE`: (Optional) Custom OpenAI API base URL. Use this to point to your own LiteLLM proxy or compatible endpoint.
   *   `GEMINI_API_KEY`: Your Google AI Studio (Gemini) API key (Required if PREFERRED_PROVIDER=google).
   *   `PREFERRED_PROVIDER` (Optional): Set to `openai` (default) or `google`. This determines the primary backend for mapping `haiku`/`sonnet`.
   *   `BIG_MODEL` (Optional): The model to map `sonnet` requests to. Defaults to `gpt-4.1` (if `PREFERRED_PROVIDER=openai`) or `gemini-2.5-pro-preview-03-25`.
   *   `SMALL_MODEL` (Optional): The model to map `haiku` requests to. Defaults to `gpt-4.1-mini` (if `PREFERRED_PROVIDER=openai`) or `gemini-2.0-flash`.

   **Mapping Logic:**
   - If `PREFERRED_PROVIDER=openai` (default), `haiku`/`sonnet` map to `SMALL_MODEL`/`BIG_MODEL` prefixed with `openai/`.
   - If `PREFERRED_PROVIDER=google`, `haiku`/`sonnet` map to `SMALL_MODEL`/`BIG_MODEL` prefixed with `gemini/` *if* those models are in the server's known `GEMINI_MODELS` list (otherwise falls back to OpenAI mapping).

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

### Using with LiteLLM Proxy 🔗

You can also use this proxy to connect to your own LiteLLM proxy instance:

1. **Set up your LiteLLM proxy** (running on e.g., http://localhost:4000)

2. **Configure the proxy to use your LiteLLM instance**:
   ```bash
   export OPENAI_API_BASE="http://localhost:4000/v1"
   export OPENAI_API_KEY="your-litellm-api-key"  # Or any key your LiteLLM proxy expects
   ```

3. **Run the proxy** as usual:
   ```bash
   uv run uvicorn server:app --host 0.0.0.0 --port 8082 --reload
   ```

4. **Connect Claude Code**:
   ```bash
   ANTHROPIC_BASE_URL=http://localhost:8082 claude
   ```

This setup allows you to chain proxies: `Claude Code` → `This Proxy` → `LiteLLM Proxy` → `Multiple LLM Providers` 🔄

## Model Mapping 🗺️

The proxy automatically maps Claude models to either OpenAI or Gemini models based on the configured model:

| Claude Model | Default Mapping | When BIG_MODEL/SMALL_MODEL is a Gemini model |
|--------------|--------------|---------------------------|
| haiku | openai/gpt-4o-mini | gemini/[model-name] |
| sonnet | openai/gpt-4o | gemini/[model-name] |

### Supported Models

#### OpenAI Models
The following OpenAI models are supported with automatic `openai/` prefix handling:
- o3-mini
- o1
- o1-mini
- o1-pro
- gpt-4.5-preview
- gpt-4o
- gpt-4o-audio-preview
- chatgpt-4o-latest
- gpt-4o-mini
- gpt-4o-mini-audio-preview
- gpt-4.1
- gpt-4.1-mini

#### Gemini Models
The following Gemini models are supported with automatic `gemini/` prefix handling:
- gemini-2.5-pro-preview-03-25
- gemini-2.0-flash

### Model Prefix Handling
The proxy automatically adds the appropriate prefix to model names:
- OpenAI models get the `openai/` prefix 
- Gemini models get the `gemini/` prefix
- The BIG_MODEL and SMALL_MODEL will get the appropriate prefix based on whether they're in the OpenAI or Gemini model lists

For example:
- `gpt-4o` becomes `openai/gpt-4o`
- `gemini-2.5-pro-preview-03-25` becomes `gemini/gemini-2.5-pro-preview-03-25`
- When BIG_MODEL is set to a Gemini model, Claude Sonnet will map to `gemini/[model-name]`

### Customizing Model Mapping

Control the mapping using environment variables in your `.env` file or directly:

**Example 1: Default (Use OpenAI)**
No changes needed in `.env` beyond API keys, or ensure:
```dotenv
OPENAI_API_KEY="your-openai-key"
GEMINI_API_KEY="your-google-key" # Needed if PREFERRED_PROVIDER=google
# PREFERRED_PROVIDER="openai" # Optional, it's the default
# BIG_MODEL="gpt-4.1" # Optional, it's the default
# SMALL_MODEL="gpt-4.1-mini" # Optional, it's the default
```

**Example 2: Prefer Google**
```dotenv
GEMINI_API_KEY="your-google-key"
OPENAI_API_KEY="your-openai-key" # Needed for fallback
PREFERRED_PROVIDER="google"
# BIG_MODEL="gemini-2.5-pro-preview-03-25" # Optional, it's the default for Google pref
# SMALL_MODEL="gemini-2.0-flash" # Optional, it's the default for Google pref
```

**Example 3: Use Specific OpenAI Models**
```dotenv
OPENAI_API_KEY="your-openai-key"
GEMINI_API_KEY="your-google-key"
PREFERRED_PROVIDER="openai"
BIG_MODEL="gpt-4o" # Example specific model
SMALL_MODEL="gpt-4o-mini" # Example specific model
```

**Example 4: Use LiteLLM Proxy**
```dotenv
OPENAI_API_KEY="your-litellm-api-key" # Whatever your LiteLLM proxy expects
OPENAI_API_BASE="http://localhost:4000/v1" # Your LiteLLM proxy URL
PREFERRED_PROVIDER="openai"
BIG_MODEL="claude-3-5-sonnet-20241022" # Any model supported by your LiteLLM proxy
SMALL_MODEL="claude-3-5-haiku-20241022" # Any model supported by your LiteLLM proxy
```

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
