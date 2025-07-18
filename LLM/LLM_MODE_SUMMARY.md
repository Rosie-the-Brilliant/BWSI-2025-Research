# LLM Mode Summary

## 🎯 **Default Mode (Recommended for M4 MacBook Air)**

```bash
python main.py -m llm
```

**What it does:**
- ✅ **Multimodal LLM agent** (uses LLaVA by default)
- ✅ **Best performance and decision quality**
- ✅ **Requires 16GB+ RAM for best results**
- ✅ **Image + text reasoning**

## 📋 **Available Mode**

| Mode | Command | Best For | RAM Usage | Speed | LLM Calls |
|------|---------|----------|-----------|-------|-----------|
| **llm** | `python main.py -m llm` | M4 MacBook Air/Pro (default) | ~6GB | ⚡⚡⚡ | 100% |

## 🚀 **Quick Start**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup Ollama
python setup_ollama.py

# 3. Run the LLM agent
python main.py -m llm
```

## 📊 **Performance**

- **Game Completion:** 5-8 minutes
- **Memory Usage:** ~6GB
- **Decision Quality:** Best (full visual context)

## 💡 **Why Multimodal is Smart**

The LLM agent uses both image and text context for every decision, maximizing rescue accuracy and strategic play. 