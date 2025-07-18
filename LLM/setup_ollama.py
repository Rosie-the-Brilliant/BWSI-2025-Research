#!/usr/bin/env python3
"""
Setup script for Ollama LLM integration
This script helps you install and configure Ollama for the zombie game LLM agent.
"""

import subprocess
import sys
import os
import requests
import time

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_ollama():
    """Install Ollama based on the operating system"""
    system = sys.platform
    
    print("Installing Ollama...")
    
    if system == "darwin":  # macOS
        print("Detected macOS. Installing Ollama...")
        try:
            subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh', '|', 'sh'], 
                         shell=True, check=True)
            print("Ollama installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install Ollama. Please install manually from https://ollama.ai/")
            return False
    
    elif system.startswith("linux"):
        print("Detected Linux. Installing Ollama...")
        try:
            subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh', '|', 'sh'], 
                         shell=True, check=True)
            print("Ollama installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install Ollama. Please install manually from https://ollama.ai/")
            return False
    
    elif system == "win32":
        print("Detected Windows. Please install Ollama manually from https://ollama.ai/")
        print("Download the Windows installer and follow the installation instructions.")
        return False
    
    else:
        print(f"Unsupported operating system: {system}")
        print("Please install Ollama manually from https://ollama.ai/")
        return False

def start_ollama_service():
    """Start the Ollama service"""
    print("Starting Ollama service...")
    try:
        # Start Ollama in the background
        subprocess.Popen(['ollama', 'serve'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        # Wait a moment for the service to start
        time.sleep(3)
        
        # Test if the service is running
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                print("Ollama service is running!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print("Ollama service may not be running. Please start it manually with: ollama serve")
        return False
        
    except Exception as e:
        print(f"Failed to start Ollama service: {e}")
        return False

def download_models():
    """Download required Ollama models"""
    print("Choose which models to download:")
    print("1. Ultra-lightweight (llama2:3b) - Best for 8GB RAM")
    print("2. Lightweight (llama2:7b) - Best for 16GB RAM") 
    print("3. Full multimodal (llava) - Best for 16GB+ RAM")
    print("4. All models")
    
    choice = input("Enter your choice (1-4): ").strip()
    
    models = []
    if choice == "1":
        models = ["llama2:3b"]
    elif choice == "2":
        models = ["llama2:7b"]
    elif choice == "3":
        models = ["llava"]
    elif choice == "4":
        models = ["llama2:3b", "llama2:7b", "llava"]
    else:
        print("Invalid choice. Downloading ultra-lightweight model by default.")
        models = ["llama2:3b"]
    
    for model in models:
        print(f"Downloading {model} model...")
        try:
            subprocess.run(['ollama', 'pull', model], check=True)
            print(f"{model} model downloaded successfully!")
        except subprocess.CalledProcessError:
            print(f"Failed to download {model} model. You can download it manually with: ollama pull {model}")

def test_ollama_connection():
    """Test connection to Ollama API"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama API is accessible!")
            return True
        else:
            print("❌ Ollama API returned error status")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Ollama API: {e}")
        return False

def get_available_actions(self, at_capacity):
    actions = []
    if self.scorekeeper.remaining_time > 0:
        if not at_capacity:
            actions.append("SAVE")
        actions.append("SQUISH")
        actions.append("SKIP")
        actions.append("SCRAM")
    return actions

def main():
    """Main setup function"""
    print("=== Ollama Setup for Zombie Game LLM Agent ===\n")
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        print("Ollama is not installed.")
        install_choice = input("Would you like to install Ollama now? (y/n): ").lower()
        if install_choice == 'y':
            if not install_ollama():
                print("Please install Ollama manually and run this script again.")
                return
        else:
            print("Please install Ollama manually from https://ollama.ai/ and run this script again.")
            return
    else:
        print("✅ Ollama is already installed!")
    
    # Start Ollama service
    if not start_ollama_service():
        print("Please start Ollama manually with: ollama serve")
        return
    
    # Test connection
    if not test_ollama_connection():
        print("Please ensure Ollama is running and try again.")
        return
    
    # Download models
    download_choice = input("Would you like to download the required models now? (y/n): ").lower()
    if download_choice == 'y':
        download_models()
    
    print("\n=== Setup Complete! ===")
    print("You can now run the LLM agent with:")
    print("\nFor M4 Mac (ultra-lightweight - recommended):")
    print("python main.py -m llm")
    print("\nFor M4 Mac with 16GB RAM (lightweight):")
    print("python main.py -m llm-light")
    print("\nFor M4 Mac with 16GB+ RAM (full multimodal):")
    print("python main.py -m llm-multimodal")
    print("\nSee M4_PERFORMANCE_GUIDE.md for detailed performance recommendations!")

if __name__ == "__main__":
    main() 