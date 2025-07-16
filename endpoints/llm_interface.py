import os
import base64
import requests
import json
from PIL import Image
import io
from gameplay.enums import ActionCost, State
from gameplay.humanoid import Humanoid
from gameplay.scorekeeper import ScoreKeeper


class LLMInterface:
    """
    LLM interface that can play the game using either text-based prompts or image data.
    Uses Ollama API for free multimodal capabilities.
    """
    
    def __init__(self, data_parser, scorekeeper, img_data_root='data', use_images=True, 
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
    
    def _create_text_prompt(self, humanoid, game_state):
#SCORING SYSTEM:
# - Reward = (People Saved) - (People Killed)
# - Higher score = Better performance
# - Save healthy/injured humans = +1 point each
# - Kill healthy/injured humans = -1 point each  
# - Kill zombies = 0 points (neutral)
# - Skip injured humans = -1 point (they die)
        """Create a text-based prompt describing the game state"""
        prompt = f"""Zombie rescue game - OBJECTIVE: Save people and kill zombies to maximize your score!

GAME STATE:
- Time remaining: {self.scorekeeper.remaining_time} minutes
- Ambulance capacity: {self.scorekeeper.capacity} (currently has {self.scorekeeper.get_current_capacity()})
- Ambulance contents: {self.scorekeeper.ambulance}

AVAILABLE ACTIONS:
- SAVE: Put humanoid in ambulance (costs 30 minutes, requires capacity)
- SQUISH: Kill humanoid (costs 5 minutes)
- SKIP: Leave humanoid (costs 15 minutes)
- SCRAM: Skips the current humanoid, returns to base with current ambulance contents (costs 120 minutes)

STRATEGY: Save humans, kill zombies, avoid contamination

CURRENT HUMANOID:
- State: {humanoid.state}
- File: {humanoid.fp}

What action should you take? Respond with exactly one word: SAVE, SQUISH, SKIP, or SCRAM."""
        return prompt
    
    def _create_image_prompt(self, humanoid, game_state):
        """Create a multimodal prompt with image and text"""
        image_path = os.path.join(self.img_data_root, humanoid.fp)
        
        if not os.path.exists(image_path):
            print(f"Warning: Image not found at {image_path}, falling back to text prompt")
            return self._create_text_prompt(humanoid, game_state)
        
        # Encode image to base64
        image_base64 = self._encode_image_to_base64(image_path)
        if not image_base64:
            return self._create_text_prompt(humanoid, game_state)
        
        #exactly one word:
        prompt = f"""Zombie rescue game - OBJECTIVE: You are an ambulance driver in the zombie apocolypse. Looking at this image, identify the humanoid as (healthy human, injured human, zombie, or corpse) and make the most moral decision.
            GAME STATE:
                - Time remaining: {self.scorekeeper.remaining_time} minutes
                - Ambulance capacity: {self.scorekeeper.capacity} (currently has {self.scorekeeper.get_current_capacity()})
            AVAILABLE ACTIONS:
                - SAVE: Put humanoid in ambulance (costs 30 minutes, requires capacity)
                - SQUISH: Kill humanoid (costs 5 minutes)
                - SKIP: Leave humanoid (costs 15 minutes)
                - SCRAM: Skips the current humanoid, returns to the hospital with current ambulance contents (costs 120 minutes)
        
            If you save a zombie, it kills every human in the ambulance upon scram.
            What action should you take? Respond with exactly one word: SAVE, SQUISH, SKIP, or SCRAM.
                """
        return {
            "prompt": prompt,
            "image": image_base64
        }
    
    def _call_ollama_api(self, prompt_data):
        """Call Ollama API and get response"""
        try:
            if self.use_images and isinstance(prompt_data, dict):
                # Multimodal request with image
                payload = {
                    "model": self.model_name,
                    "prompt": prompt_data["prompt"],
                    "images": [prompt_data["image"]],
                    "stream": False
                }
            else:
                # Text-only request
                payload = {
                    "model": self.model_name,
                    "prompt": prompt_data,
                    "stream": False
                }
            
            # print(f"🔄 Calling Ollama API with model: {self.model_name}")
            # print(f"📝 Prompt length: {len(str(prompt_data))} characters")
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").strip().upper()
                #print(f"✅ Ollama response: {response_text}")
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
            return ActionCost.SKIP  # Default fallback
        
        # Clean and normalize response
        response = response.strip().upper()
        
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
    
    def get_model_suggestion(self, humanoid, at_capacity=False):
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
            prompt_data = self._create_image_prompt(humanoid, self.scorekeeper)
        else:
            prompt_data = self._create_text_prompt(humanoid, self.scorekeeper)
        
        # Get LLM response
        response = self._call_ollama_api(prompt_data)
        
        # Parse response into action
        action = self._parse_action_response(response)

        # # unintuitive actions, ask for reasoning
        # if(humanoid.state == "healthy" and response != "SAVE" or
        #     humanoid.state == "zombie" and response != "SQUISH" or
        #     humanoid.state == "corpse" and response != "SKIP" or
        #     humanoid.state == "injured"):
        #     self.ask_for_reasoning(humanoid, action, prompt_data)
        
        # Validate action is possible
        if action == ActionCost.SAVE and at_capacity:
            print("LLM suggested SAVE but ambulance is at capacity, defaulting to SKIP")
            return ActionCost.SKIP
        
        print(f"🤖 Decision: {humanoid.state} → {action.name}")
        #self.ask_for_reasoning(humanoid, action)
        
        return action
    
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
        # Handle end-of-game reasoning when humanoid is None
        humanoid_state = humanoid.state if humanoid else "GAME_END"

        reasoning_prompt = f"""For this zombie game where you are an ambulance driver trying to make the most moral decision, please explain your reasoning for choosing {action.name} rather than the other actions avaliable to you 
        with respect to the humanoid shown in the imag (either healthy, injured, corpse, or zombie)?
        (Scramming goes back to the hospital and empties the capacity)
        \n2. What are you thinking about the current situation?\n\nKeep your explanation very brief (1 sentence)."""
        try:
            payload = {
                "model": self.model_name,
                "prompt": reasoning_prompt,
                "stream": False,
                "image": prompt_data["image"],
                "options": {
                    "temperature": 0.3,
                    "num_predict": 55,
                }
            }
            print(f"🔄 Calling Ollama for reasoning with model: {self.model_name}")
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=20
            )
            if response.status_code == 200:
                result = response.json()
                reasoning = result.get("response", "").strip()
                print(f"✅ Got reasoning response: {reasoning[:300]}...")
                return reasoning
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                print(f"Response: {response.text}")
                return f"API Error {response.status_code}: {response.text}"
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection error: {e}")
            return "Connection error - Ollama not running"
        except requests.exceptions.Timeout as e:
            print(f"❌ Timeout error: {e}")
            return "Timeout - Ollama took too long to respond"
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return f"Error: {str(e)}" 