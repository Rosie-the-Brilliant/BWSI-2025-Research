import os
import base64
import requests
from PIL import Image
from gameplay.enums import ActionCost
from gameplay.humanoid import Humanoid
from gameplay.scorekeeper import ScoreKeeper
from LLM.promptEnums import *

class GeminiLLMInterface:
    def __init__(self, data_parser, scorekeeper, img_data_root='data', use_images=True, role=None, model_name="gemini-2.0-flash-lite"):
        self.API_KEY = os.environ.get("GEMINI_API_KEY")
        self.data_parser = data_parser
        self.scorekeeper = scorekeeper
        self.img_data_root = img_data_root
        self.use_images = use_images
        self.role = role
        self.model_name = model_name
        self.llm_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"

    def _encode_image_to_base64(self, image_path):
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image {image_path}: {e}")
            return None

    def get_model_suggestion(self, humanoid, at_capacity=False, identify=False):
        print(f"Starting Gemini {self.model_name} run of zombie game")
        if self.use_images:
            prompt_data = self._create_image_prompt(humanoid, identify)
        else:
            context = Context.TEXT.value
            if self.role and self.role.upper() in Context.__members__:
                context = Context[self.role.upper()].value

            prompt_data = {
                "context": context + Context.TEXT.value,
                "prompt": Prompt.TEXT.value.format(
                    time=self.scorekeeper.remaining_time,
                    capacity=self.scorekeeper.capacity - self.scorekeeper.get_current_capacity(),
                    humanoid=humanoid)
            }

        response = self._call_gemini_api(prompt_data)
        if response is None:
            print("❌ LLM API call failed or returned no response.")
            return "UNKNOWN"

        response = response.upper()
        if identify:
            print(f"Humanoid: {humanoid.state} \n🤖 Guess: {response})")
            return response

        action = self._parse_action_response(response)
        print(f"{humanoid.state} → {action.name}")

        if action == ActionCost.SAVE and at_capacity:
            print("LLM suggested SAVE but ambulance is at capacity, defaulting to SKIP")
            return ActionCost.SKIP

        return action

    def _create_image_prompt(self, humanoid, identify=False):
        image_path = os.path.join(self.img_data_root, humanoid.fp)
        if not os.path.exists(image_path):
            print(f"Warning: Image not found at {image_path}, falling back to text prompt")
            self.use_images = False
            return Prompt.TEXT.value.format(time=self.scorekeeper.remaining_time, capacity=self.scorekeeper.capacity, filled=self.scorekeeper.get_current_capacity(), humanoid=humanoid)

        image_base64 = self._encode_image_to_base64(image_path)
        prompt_text = Prompt.IDENTIFY.value if identify else Prompt.IMAGETEXT.value.format(
            time=self.scorekeeper.remaining_time,
            capacity=self.scorekeeper.capacity - self.scorekeeper.get_current_capacity())

        context = Context.IDENTIFY.value if identify else Context.IMAGETEXT.value

        return {
            "prompt": prompt_text,
            "context": context,
            "image": image_base64
        }

    def _call_gemini_api(self, prompt_data):
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.API_KEY
        }

        url = f"{self.llm_url}?key={self.API_KEY}"

        if self.use_images:
            contents = [
                {"parts": [
                    {"text": prompt_data["context"]},
                    {"inline_data": {
                        "mime_type": "image/jpeg",
                        "data": prompt_data["image"]
                    }},
                    {"text": prompt_data["prompt"]}
                ]}
            ]
        else:
            contents = [
                {"parts":[
                    {"text": prompt_data["context"]},
                    {"text": prompt_data["prompt"]}
            ]}]


        payload = {
            "contents": contents
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            result = response.json()
            
            if "candidates" not in result:
                print(f"❌ Unexpected API response: {result}")
                return None
            return result["candidates"][0]["content"]["parts"][0]["text"]
        
        except Exception as e:
            print(f"❌ Error calling Gemini API: {e}")
            return None

    def _parse_action_response(self, response):
        if not response:
            print("no response")
            return ActionCost.SKIP

        response = response.strip().upper().split(" ")[0]
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

        if response in action_mapping:
            return action_mapping[response]

        for key, action in action_mapping.items():
            if key in response or response in key:
                return action

        print(f"Could not parse LLM response '{response}', defaulting to SKIP")
        return ActionCost.SKIP
