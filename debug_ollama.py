#!/usr/bin/env python3
"""
Debug script for Ollama LLM integration
This script helps diagnose and fix Ollama connection issues.
"""

import requests
import subprocess
import sys
import os
import time

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama is installed but not working properly")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        return False

def check_ollama_running():
    """Check if Ollama service is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama service is running")
            return True
        else:
            print(f"❌ Ollama service returned error: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama service")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama service: {e}")
        return False

def start_ollama_service():
    """Start Ollama service"""
    print("🔄 Starting Ollama service...")
    try:
        # Start Ollama in background
        process = subprocess.Popen(['ollama', 'serve'], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
        
        # Wait for service to start
        time.sleep(3)
        
        # Check if it's running
        if check_ollama_running():
            print("✅ Ollama service started successfully")
            return True
        else:
            print("❌ Failed to start Ollama service")
            return False
            
    except Exception as e:
        print(f"❌ Error starting Ollama service: {e}")
        return False

def check_available_models():
    """Check what models are available"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print("📦 Available models:")
                for model in models:
                    print(f"  - {model['name']}")
                return [model['name'] for model in models]
            else:
                print("❌ No models found")
                return []
        else:
            print(f"❌ Error getting models: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return []

def test_model_response(model_name):
    """Test if a specific model can respond"""
    print(f"🧪 Testing model: {model_name}")
    try:
        payload = {
            "model": model_name,
            "prompt": "Say 'Hello' if you can hear me.",
            "stream": False
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Model {model_name} responded: {result.get('response', 'No response')[:50]}...")
            return True
        else:
            print(f"❌ Model {model_name} failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing model {model_name}: {e}")
        return False

def download_model(model_name):
    """Download a model"""
    print(f"📥 Downloading model: {model_name}")
    try:
        result = subprocess.run(['ollama', 'pull', model_name], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✅ Model {model_name} downloaded successfully")
            return True
        else:
            print(f"❌ Failed to download model {model_name}")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ Download timeout for model {model_name}")
        return False
    except Exception as e:
        print(f"❌ Error downloading model {model_name}: {e}")
        return False

def test_game_integration():
    """Test the game integration"""
    print("🎮 Testing game integration...")
    try:
        # Import the LLM interface
        sys.path.append(os.path.dirname(__file__))
        from endpoints.llm_interface import LLMInterface
        from endpoints.data_parser import DataParser
        from gameplay.scorekeeper import ScoreKeeper
        
        # Create test objects
        data_fp = os.path.join(os.path.dirname(__file__), 'data')
        data_parser = DataParser(data_fp)
        scorekeeper = ScoreKeeper(720, 10)
        
        # Test with text-only mode first
        llm_agent = LLMInterface(data_parser, scorekeeper, data_fp, use_images=False, model_name="llama2:3b")
        
        # Get a test humanoid
        if len(data_parser.unvisited) > 0:
            humanoid = data_parser.get_random()
            print(f"Testing with humanoid: {humanoid.state}")
            
            # Test the suggestion
            action = llm_agent.get_model_suggestion(humanoid, False)
            print(f"✅ LLM suggested action: {action}")
            return True
        else:
            print("❌ No humanoids available for testing")
            return False
            
    except Exception as e:
        print(f"❌ Error testing game integration: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main diagnostic function"""
    print("🔍 Ollama LLM Integration Diagnostic")
    print("=" * 50)
    
    # Step 1: Check if Ollama is installed
    if not check_ollama_installed():
        print("\n💡 To install Ollama:")
        print("curl -fsSL https://ollama.ai/install.sh | sh")
        return
    
    # Step 2: Check if Ollama service is running
    if not check_ollama_running():
        print("\n🔄 Attempting to start Ollama service...")
        if not start_ollama_service():
            print("\n💡 To start Ollama manually:")
            print("ollama serve")
            return
    
    # Step 3: Check available models
    available_models = check_available_models()
    
    # Step 4: Test with available models
    working_models = []
    for model in available_models:
        if test_model_response(model):
            working_models.append(model)
    
    # Step 5: If no working models, suggest downloading
    if not working_models:
        print("\n📥 No working models found. Let's download one...")
        print("Choose a model to download:")
        print("1. llama2:3b (fastest, ~2GB RAM)")
        print("2. llama2:7b (good balance, ~4GB RAM)")
        print("3. llava (multimodal, ~6GB RAM)")
        
        choice = input("Enter choice (1-3): ").strip()
        
        model_map = {
            "1": "llama2:3b",
            "2": "llama2:7b", 
            "3": "llava"
        }
        
        if choice in model_map:
            model_name = model_map[choice]
            if download_model(model_name):
                working_models.append(model_name)
        else:
            print("Invalid choice. Downloading llama2:3b...")
            if download_model("llama2:3b"):
                working_models.append("llama2:3b")
    
    # Step 6: Test game integration
    if working_models:
        print(f"\n🎮 Testing game integration with model: {working_models[0]}")
        if test_game_integration():
            print("\n✅ Everything is working! You can now run:")
            print("python main.py -m llm")
        else:
            print("\n❌ Game integration failed. Check the error above.")
    else:
        print("\n❌ No working models available.")
    
    print("\n" + "=" * 50)
    print("🔍 Diagnostic complete!")

if __name__ == "__main__":
    main() 