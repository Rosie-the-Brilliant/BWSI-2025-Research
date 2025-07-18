# LLM Integration for Zombie Game

This document explains how to integrate Large Language Models (LLMs) to play the zombie apocalypse rescue game.

## Overview

The LLM integration allows an AI model to play the game by:
1. **Text-based mode**: Receiving game state as text descriptions
2. **Image-based mode**: Receiving actual screenshots of humanoids + game state

The LLM makes decisions about what actions to take (SAVE, SQUISH, SKIP, SCRAM) based on the current game situation.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Ollama

Ollama is a free, local LLM server that provides multimodal capabilities.

**Option A: Automatic Setup**
```bash
python setup_ollama.py
```

**Option B: Manual Installation**
- Visit [https://ollama.ai/](https://ollama.ai/)
- Download and install for your operating system
- Start the service: `ollama serve`

### 3. Download Models

```bash
# For image + text support (recommended)
ollama pull llava

# For text-only support (faster, smaller)
ollama pull llama2
```

## Usage

### Running the LLM Agent

```bash
# Run with image support (default)
python main.py -m llm

# Run with logging enabled
python main.py -m llm -l True
```

### Configuration Options

You can modify the LLM behavior by editing the `LLMInterface` initialization in `main.py`:

```python
# Image + text mode (default)
llm_agent = LLMInterface(self.data_parser, self.scorekeeper, self.data_fp, use_images=True)

# Text-only mode (faster)
llm_agent = LLMInterface(self.data_parser, self.scorekeeper, self.data_fp, use_images=False)

# Custom Ollama URL
llm_agent = LLMInterface(self.data_parser, self.scorekeeper, self.data_fp, 
                        ollama_url="http://your-ollama-server:11434")

# Different model
llm_agent = LLMInterface(self.data_parser, self.scorekeeper, self.data_fp, 
                        model_name="llama2")
```

## How It Works

### Game State Information

The LLM receives the following information for each decision:

- **Time remaining**: Minutes left in the shift
- **Ambulance capacity**: Maximum and current capacity
- **Current contents**: What's already in the ambulance
- **Humanoid state**: Text description or image of the current humanoid
- **Available actions**: What actions are possible

### Action Mapping

The LLM can respond with various phrases that get mapped to game actions:

| LLM Response | Game Action | Description |
|--------------|-------------|-------------|
| SAVE, RESCUE, HELP | SAVE | Put humanoid in ambulance |
| SQUISH, KILL | SQUISH | Kill the humanoid |
| SKIP, LEAVE, IGNORE | SKIP | Leave humanoid behind |
| SCRAM, RUN | SCRAM | Return to base |

### Prompt Engineering

The system uses carefully crafted prompts to ensure the LLM understands:

1. **Game rules and scoring system**
2. **Time and resource constraints**
3. **Strategic considerations** (e.g., zombies contaminate the ambulance)
4. **Available actions and their costs**

## Performance Considerations

### Text vs Image Mode

| Mode | Pros | Cons |
|------|------|------|
| **Text** | Faster, smaller models, less memory | No visual information |
| **Image** | Full visual context, better decisions | Slower, larger models, more memory |

### Model Selection

- **llava**: Best for image + text, ~4GB RAM
- **llama2**: Good for text-only, ~2GB RAM
- **llama2:7b**: Smaller text model, ~1GB RAM

### Optimization Tips

1. **Use text mode** for faster gameplay and testing
2. **Use image mode** for better decision-making
3. **Adjust model size** based on your hardware
4. **Run Ollama on GPU** if available for better performance

## Troubleshooting

### Common Issues

**"Cannot connect to Ollama API"**
- Ensure Ollama is running: `ollama serve`
- Check if port 11434 is available
- Verify firewall settings

**"Model not found"**
- Download the required model: `ollama pull llava`
- Check available models: `ollama list`

**"Image not found"**
- Verify image paths in the data directory
- Check file permissions

**Slow performance**
- Use text-only mode: `use_images=False`
- Use a smaller model: `model_name="llama2:7b"`
- Ensure sufficient RAM/GPU

### Debug Mode

Enable debug output by modifying the LLM interface:

```python
# Add to LLMInterface.__init__
self.debug = True

# Add debug prints in _call_ollama_api and _parse_action_response
```

## API Costs

**Ollama is completely free!** Unlike commercial APIs (OpenAI, Anthropic, etc.), Ollama:
- Runs locally on your machine
- Has no usage fees
- No rate limits
- No internet required after setup

## Alternative LLM Providers

If you prefer commercial APIs, you can modify the `_call_ollama_api` method to use:

- **OpenAI GPT-4V**: Best multimodal performance, but costs money
- **Anthropic Claude**: Good performance, paid service
- **Google Gemini**: Good performance, paid service
