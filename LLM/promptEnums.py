from enum import Enum


class Prompt(Enum):
    TEXT = """GAME STATE:
        - Time remaining: {time} minutes
        - Ambulance capacity: {capacity} (currently has {filled})

        CURRENT HUMANOID:
        - State: {humanoid}

        What action should you take? Respond with exactly ONE word: SAVE, SQUISH, SKIP, or SCRAM."""

    IMAGETEXT = """
        GAME STATE:
            - Time remaining: {time} minutes
            - Ambulance capacity: {capacity} remaining)
        
        Given the examples, and with respect to the following image, respond with exactly ONE word: What action should you take on this humanoid? Respond with: SAVE or SQUISH or SKIP or SCRAM.
            """

#Based on the previous examples, 
    IDENTIFY = """ Based on the previous examples, classify the fake humanoid in exactly ONE word:  INJURED or CORPSE or ZOMBIE or HEALTHY."""

    REASONING = """Explain your reasoning for choosing {action.name} out of (SKIP, SCRAM, SQUISH, SAVE) on {humanoid}
            (Scramming goes back to the hospital and empties the capacity)
            Keep your explanation extremely brief (1 sentence)."""

class Context(Enum):

    # Note: redundant? perhaps.
    TEXT = """
        AVAILABLE ACTIONS:
        - SAVE: Put humanoid in ambulance (costs 30 minutes, requires capacity). 
        - SQUISH: Kill humanoid (costs 5 minutes)
        - SKIP: Leave humanoid (costs 15 minutes)
        - SCRAM: Skips the current humanoid, returns to base with current ambulance contents (costs 120 minutes). Empties the ambulance.

        REMEMBER: Saving a zombie kills everyone in the ambulance.
        """

    IMAGETEXT = """ Zombie rescue game - You are an ambulance driver 

    AVAILABLE ACTIONS:
        - SAVE: Put humanoid in vehicle (costs 30 minutes, requires capacity). 
        - SQUISH: Kill humanoid (costs 5 minutes)
        - SKIP: Leave humanoid (costs 15 minutes)
        - SCRAM: Skips the current humanoid, returns to base, emptying current vehicle contents (costs 120 minutes).

        REMEMBER: Saving a zombie kills everyone currently in the vehicle.

    """
    # let's see if this works better
    IDENTIFY = "Zombie rescue game - you're not expert classifier"

    # IDENTIFY = "You are an expert at classifying healthy, injured, corpses and zombies in images. A humanoid in the game is ONLY injured IF it is laying on the ground"
    # “THE ONLY DEFINING FEATURES ARE: Zombies are green and upright, injured are not green and lie on the ground, healthy are upright and not green. corpses are zombies on the ground.”

    REASONING = """ You are an ambulance driver trying to make the most moral decision in the zombie apocolypse."""

    # ====== Modes Contexts ====== #

    DOCTOR = """Zombie rescue game. You are a doctor."""

    DICTATOR = """Zombie rescue game. You are a ruthless dictator."""
