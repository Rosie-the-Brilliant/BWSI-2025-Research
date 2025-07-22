import os
import base64
from pyexpat.errors import messages
import string
import requests
import json
from PIL import Image
import io
from gameplay.enums import ActionCost, ActionState, State
from gameplay.humanoid import Humanoid
from gameplay.scorekeeper import ScoreKeeper
from LLM.promptEnums import *


class LLMInterface:
    """
    LLM interface that can play the game using either text-based prompts or image data.
    Uses Ollama API for free multimodal capabilities.
    """
    
    def __init__(self, data_parser, scorekeeper, img_data_root='data', use_images=True, role=None,
                 ollama_url="http://localhost:11434", model_name="llava"):
        """
        Initialize LLM interface
        
        Args:
            data_parser: DataParser object containing humanoid data
            scorekeeper: ScoreKeeper object for game state
            img_data_root: Root directory for image data
            use_images: Whether to use image-based prompts (True) or text-based (False)
            ollama_url: URL for Ollama API (default: localhost)
            model_name: Ollama model to use (llava for multimodal, llama2 for text-only)
        """
        self.data_parser = data_parser
        self.scorekeeper = scorekeeper
        self.img_data_root = img_data_root
        self.use_images = use_images
        self.role = role
        self.ollama_url = ollama_url
        self.model_name = model_name
        
        # Test connection to Ollama
        self._test_connection()
    
    def _test_connection(self):
        """Test if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags") 
            if response.status_code != 200:
                print(f"Warning: Ollama API not accessible at {self.ollama_url}")
                print("Please install and run Ollama: https://ollama.ai/")
                print("For multimodal support, pull llava: ollama pull llava")
        except requests.exceptions.ConnectionError:
            print(f"Warning: Cannot connect to Ollama at {self.ollama_url}")
            print("Please install and run Ollama: https://ollama.ai/")
    
    def _encode_image_to_base64(self, image_path):
        """Convert image to base64 string for API"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image {image_path}: {e}")
            return None
    
    def _create_image_prompt(self, humanoid, identify=False):
        # example images for llm context
        healthy_path = os.path.join(self.img_data_root, 'consolidated_dataset/test_00000.png')
        #168
        injured_path = os.path.join(self.img_data_root, 'consolidated_dataset/test_00147.png')
        corpse_path = os.path.join(self.img_data_root, 'consolidated_dataset/test_00173.png')
        zombie_path = os.path.join(self.img_data_root, 'consolidated_dataset/test_00177.png')

        example_images = [self._encode_image_to_base64(image) for image in (healthy_path, injured_path, corpse_path, zombie_path)]
        #print(example_images[0][:10] if (example_images[0] != None) else "")

        """Create a multimodal prompt with image and text"""
        image_path = os.path.join(self.img_data_root, humanoid.fp)
        #print(image_path)

        if not os.path.exists(image_path):
            print(f"Warning: Image not found at {image_path}, falling back to text prompt")
            self.use_images = False
            return Prompt.TEXT.value.format(time=self.scorekeeper.remaining_time, capacity=self.scorekeeper.capacity, filled=self.scorekeeper.get_current_capacity(),humanoid=humanoid.state)
        
        # Encode image to base64
        image_base64 = self._encode_image_to_base64(image_path)
        
        if not (image_base64):
            print(f"Warning: Image not found at {image_base64}, falling back to text prompt")

        # Note: might be good to error catch here
        return {
            "prompt": Prompt.IDENTIFY.value if identify else Prompt.IMAGETEXT.value.format(time=self.scorekeeper.remaining_time, capacity=(self.scorekeeper.capacity-self.scorekeeper.get_current_capacity())),
            "image": image_base64,
            "context": Context.IDENTIFY.value if identify else Context.IMAGETEXT.value,
            "example_images" : example_images
        }
    
    def _call_ollama_api(self, prompt_data):
        """Call Ollama API and get response"""
        try:
            if self.use_images and isinstance(prompt_data, dict):
                # Multimodal request with image
                #length = len(prompt_data["image"])
                #print(prompt_data["image"][length//2:length//2+10])

                payload = {
                    "model": self.model_name, 
                    "messages": [
                        {"role": "system", "content": prompt_data["context"]},
                        {"role": "user", "content": "This image is classified as HEALTHY.", "images": [prompt_data["example_images"][0]]},
                        {"role": "user", "content": "This image is classified as INJURED.", "images": [prompt_data["example_images"][1]]},
                        {"role": "user", "content": "This image is classified as CORPSE.", "images": [prompt_data["example_images"][2]]},
                        {"role": "user", "content": "This image is classified as ZOMBIE.", "images": [prompt_data["example_images"][3]]},
                        
                        #{"role": "system", "content": prompt_data["context"] + "These are examples of HEALTHY then INJURED then CORPSE then ZOMBIE", "images": prompt_data["example_images"]},
                        
                        {"role": "user", "content": prompt_data["prompt"], "images": [prompt_data["image"]]}
                    ],
                    "stream": False,
                    "options": {
                        "num_predict": 30,
                    }
                }

               
            else:
                # Text-only request, yes prompt_data is a string, yes that could be a bad idea
                payload = {
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": prompt_data["context"]},
                        {"role": "user", "content": prompt_data["prompt"]}
                    ],
                    "stream": False,
                    "options":  {
                        "num_predict": 50,
                    }
                }
            
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=100
            )

            if response.status_code == 200:
                result = response.json()
                response_text = result.get("message", {}).get("content", "").strip()
                return response_text
            else:
                print(f"❌ Error calling Ollama API: {response.status_code}")
                print(f"Response text: {response.text}")
                return None
                
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection error: Cannot connect to Ollama at {self.ollama_url}")
            print("💡 Make sure Ollama is running: ollama serve")
            return None
        except requests.exceptions.Timeout as e:
            print(f"❌ Timeout error: Ollama took too long to respond")
            print("💡 Try using a smaller model or restart Ollama")
            return None
        except Exception as e:
            print(f"❌ Error calling Ollama API: {e}")
            print(f"💡 Check if Ollama is running and the model '{self.model_name}' is available")
            return None
    
    def _parse_action_response(self, response):
        """Parse LLM response into game action"""
        if not response:
            print("no response")
            return ActionCost.SKIP  # Default fallback
        
        # Clean and normalize response
        # print(response)
        response = response.strip().upper().split(" ")
        response = response[0]
        
        # Map common variations to actions
        action_mapping = {
            "SAVE": ActionCost.SAVE,
            "SQUISH": ActionCost.SQUISH,
            "SKIP": ActionCost.SKIP,
            "SCRAM": ActionCost.SCRAM,
            "KILL": ActionCost.SQUISH,
            "LEAVE": ActionCost.SKIP,
            "RUN": ActionCost.SCRAM,
            "RESCUE": ActionCost.SAVE,
            "HELP": ActionCost.SAVE,
            "IGNORE": ActionCost.SKIP
        }
        
        # Try exact match first
        if response in action_mapping:
            return action_mapping[response]
        
        # Try partial matches
        for key, action in action_mapping.items():
            if key in response or response in key:
                return action
        
        # If no match found, return SKIP as safe default
        print(f"Could not parse LLM response '{response}', defaulting to SKIP")
        return ActionCost.SKIP
    
    def get_model_suggestion(self, humanoid, at_capacity=False, identify=False):
        """
        Get action suggestion from LLM for the given humanoid
        
        Args:
            humanoid: Humanoid object to evaluate
            at_capacity: Whether ambulance is at capacity
            
        Returns:
            ActionCost enum value
        """
        # Create appropriate prompt based on mode
        if self.use_images:
            prompt_data = self._create_image_prompt(humanoid, identify)

        else:
            context = "Zombie rescue game. You are an ambulance driver. - OBJECTIVE: Make the most moral decision"
            if(self.role == 'doctor'):
                context = Context.DOCTOR.value
            
            prompt_data = {
                # appending role in front of the game rules
                "context": context + Context.TEXT.value,
                "prompt": Prompt.TEXT.value.format(time=self.scorekeeper.remaining_time, capacity=self.scorekeeper.capacity, filled=self.scorekeeper.get_current_capacity(),humanoid=humanoid.state)
            }
        
        # Get LLM response
        response = self._call_ollama_api(prompt_data)
        if response is None:
            print("❌ LLM API call failed or returned no response.")
            return "UNKNOWN"
        response = response.upper()

        if(identify):
            print(f"Humanoid: {humanoid.state} \n🤖 Guess: {response})")
            return response
        
        # Parse response into action
        action = self._parse_action_response(response)
        print(f"🤖 Decision: {humanoid.state} → {action.name}")
        #self.ask_for_reasoning(humanoid, action)
        # unintuitive actions, ask for reasoning
        # if(humanoid.state == "healthy" and response != "SAVE" or
        #     humanoid.state == "zombie" and response != "SQUISH" or
        #     humanoid.state == "corpse" and response != "SKIP" or
        #     humanoid.state == "injured"):
        # if(humanoid.state == "zombie" and response != "SQUISH"):
        #     self.ask_for_reasoning(humanoid, action, prompt_data)

        # Validate action is possible
        if action == ActionCost.SAVE and at_capacity:
            print("LLM suggested SAVE but ambulance is at capacity, defaulting to SKIP")
            return ActionCost.SKIP
        
        return action
    
    #unused
    def act(self, humanoid):
        """
        Take action on humanoid using LLM suggestion
        
        Args:
            humanoid: Humanoid object to act on
        """
        action = self.get_model_suggestion(humanoid, self.scorekeeper.at_capacity())
        
        # Execute action
        if action == ActionCost.SAVE:
            self.scorekeeper.save(humanoid)
        elif action == ActionCost.SQUISH:
            self.scorekeeper.squish(humanoid)
        elif action == ActionCost.SKIP:
            self.scorekeeper.skip(humanoid)
        elif action == ActionCost.SCRAM:
            self.scorekeeper.scram(humanoid)
        else:
            raise ValueError(f"Invalid action: {action}")
        
        return action 

    def ask_for_reasoning(self, humanoid, action, prompt_data, at_capacity=False):
        """
        Ask the LLM to explain its decision
        """
        try:
            messages = {
                "context": Context.REASONING.value,
                "prompt": Prompt.REASONING.value.format(action=action,humanoid=humanoid.state),

            }
            # Attach the image if available
            if "images" in prompt_data and prompt_data["images"]:
                messages["images"] = prompt_data["images"]
            response_text = self._call_ollama_api(messages)
            if response_text:
                print(f"✅ Got reasoning response: {response_text}...")
                return response_text
            else:
                print(f"❌ Ollama API call failed or returned no response.")
                return "API call failed or returned no response."
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return f"Error: {str(e)}" 