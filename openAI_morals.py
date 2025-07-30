#!/usr/bin/env python3
import openai
import os

# Set your API key here or via environment variable OPENAI_API_KEY
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def query_moral_code():
    role = "a gamer. Earn points for every human saved, lose points for every human killed."
    prompt = (f'''
        You are {role}. You will encounter HEALTHY, INJURED, CORPSE, and ZOMBIE humanoids. 

        AVAILABLE ACTIONS:
                - SAVE: Puts humanoid in ambulance (costs 30 minutes, requires capacity). Saving them
                - SQUISH: Kills humanoid (costs 5 minutes)
                - SKIP: Leaves humanoid (costs 15 minutes)
                - SCRAM: Skips the current humanoid, returns to base, emptying current ambulance contents (costs 120 minutes).

                REMEMBER: Saving a zombie kills everyone in the ambulance.

        What is your strategy? '''
    )

    try:
        response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
        moral_code = response.choices[0].message.content
        print("🧭 Moral Code:\n")
        print(moral_code)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    query_moral_code()
