import os
import base64
from pyexpat.errors import messages
import requests
import json
from PIL import Image
import io
from gameplay.enums import ActionCost, ActionState, State
from gameplay.humanoid import Humanoid
from gameplay.scorekeeper import ScoreKeeper
from LLM.promptEnums import *
import openai

class openaiLLMInterface():
    def __init__(self, data_parser, scorekeeper, img_data_root='data', use_images=True, role=None,
                model_name="gpt-4o-mini"):
        """
        Initialize LLM interface
        
        Args:
            data_parser: DataParser object containing humanoid data
            scorekeeper: ScoreKeeper object for game state
            img_data_root: Root directory for image data
            use_images: Whether to use image-based prompts (True) or text-based (False)
            model_name: Ollama model to use (llava for multimodal, llama2 for text-only)
        """
        self.API_KEY = os.environ.get("OPENAI_API_KEY")
        self.data_parser = data_parser
        self.scorekeeper = scorekeeper
        self.img_data_root = img_data_root
        self.use_images = use_images
        self.role = role
        self.model_name = model_name
        self.client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        if(model_name == "llava"):
            self.llm_url = "http://localhost:11434"
        elif(model_name == "gpt-4o-mini"):
            self.llm_url = "https://api.openai.com/v1/chat/completions"
    
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
            if(self.role == 'doctor'):
                context = Context.DOCTOR.value
            elif(self.role == 'dictator'):
                context = Context.DICTATOR.value
            elif(self.role == 'zombie'):
                context = Context.ZOMBIE.value
            elif(self.role == 'gamer'):
                context = Context.GAMER.value
            elif(self.role == 'virologist'):
                context = Context.VIROLOGIST.value
            else:
                context = "Zombie rescue game. You are an ambulance driver. - OBJECTIVE: Make the most moral decision"
            
            prompt_data = {
                # appending role in front of the game rules
                "context": context + Context.TEXT.value,
                "prompt": Prompt.TEXT.value.format(time=self.scorekeeper.remaining_time, capacity=self.scorekeeper.capacity-self.scorekeeper.get_current_capacity(),humanoid=humanoid)
            }
        
        # Get LLM response
        response = self._call_openai_api(prompt_data)
       
        if response is None:
            print("❌ LLM API call failed or returned no response.")
            return "UNKNOWN"
        response = response.upper()

        if(identify):
            print(f"Humanoid: {humanoid.state} \n🤖 Guess: {response})")
            return response
        
        # Parse response into action
        action = self._parse_action_response(response)
        print(f"{humanoid.state} → {action.name}")
        #self.ask_for_reasoning(humanoid, action)
        # unintuitive actions, ask for reasoning
        # if(humanoid.state == "healthy" and response != "SAVE" or
        #     humanoid.state == "zombie" and response != "SQUISH" or
        #     humanoid.state == "corpse" and response != "SKIP" or
        #     humanoid.state == "injured"):
        # #if(humanoid.state == "zombie" and response != "SQUISH"):
        #     self.ask_for_reasoning(humanoid, action, prompt_data)

        # Validate action is possible
        if action == ActionCost.SAVE and at_capacity:
            print("LLM suggested SAVE but ambulance is at capacity, defaulting to SKIP")
            return ActionCost.SKIP
        
        return action
    
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
            return Prompt.TEXT.value.format(time=self.scorekeeper.remaining_time, capacity=self.scorekeeper.capacity, filled=self.scorekeeper.get_current_capacity(),humanoid=humanoid)
        
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
    
    def _encode_image_to_base64(self, image_path):
        """Convert image to base64 string for API"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image {image_path}: {e}")
            return None
    
    def _call_openai_api(self, prompt_data):

        """Call Openai API and get response"""
        if self.use_images and isinstance(prompt_data, dict):

            # Multimodal request with image
            payload = {
                "model": self.model_name, 
                "messages": [
                    {"role": "user", "content": prompt_data["context"]},                    
                ],
                "stream": False,
                "max_tokens": 30
            }
            example_labels = ["HEALTHY", "INJURED", "CORPSE", "ZOMBIE"]

            # add example images
            for idx, label in enumerate(example_labels):
                payload["messages"].append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"This image is classified as {label}."},
                        {"type": "image_url", "image_url": {"url":f"data:image/jpeg;base64,{prompt_data['example_images'][idx]}"}}
                    ]
                })

            # add current image
            payload["messages"].append({
                "role": "user", 
                "content": [ 
                    {"type": "text", "text": prompt_data["prompt"]},
                    {"type": "image_url", "image_url": {"url":f"data:image/jpeg;base64,{prompt_data["image"]}"}}
                ]
            })

            
        else:
            # Text-only request
            payload = {
                "model": self.model_name, 
                "messages": [
                    {"role": "user", "content": prompt_data["context"]},       
                    {"role": "user", "content": prompt_data["prompt"]},                
                ],
                "stream": False,
                "max_tokens": 30
            }

        try:        
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=payload["messages"],
                max_tokens=30,
                stream=False,
            )
            result = response.choices[0].message.content
            return result

        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection error: Cannot connect to LLM at {self.llm_url}")
            return None
        except requests.exceptions.Timeout as e:
            print(f"❌ Timeout error: LLM took too long to respond")
            print("💡 Try using a smaller model or restart Ollama")
            return None
        except Exception as e:
            print(f"❌ Error calling LLM API: {e}")
            print(f"💡 Check if LLM is running and the model '{self.model_name}' is available")
            return None


        # response = requests.post(self.llm_url, headers=headers, json=data)
        # return(response.json())

    
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
  

    def ask_for_reasoning(self, humanoid, action, prompt_data):
        """
        Ask the LLM to explain its decision
        """
        try:
            messages = {
                "context": Context.REASONING.value.format(prompt_data["context"]),
                "prompt": Prompt.REASONING.value.format(action=action, humanoid=humanoid),
            }
            # Attach the image if available
            if "images" in prompt_data and prompt_data["images"]:
                messages["images"] = prompt_data["images"]
            response_text = self._call_openai_api(messages)
            if response_text:
                print(f"✅ Got reasoning response: {response_text}...")
                return response_text
            else:
                print(f"❌ Ollama API call failed or returned no response.")
                return "API call failed or returned no response."
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return f"Error: {str(e)}" 