from enum import Enum


class Prompt(Enum):
    TEXT = """GAME STATE:
        - Time remaining: {time} minutes
        - Ambulance capacity: {capacity}

        What action should you tak on this humanoid: {humanoid.state}? Respond with exactly ONE word: SAVE or SQUISH or SKIP or SCRAM."""

    IMAGETEXT = """
        GAME STATE:
            - Time remaining: {time} minutes
            - Ambulance capacity: {capacity} remaining)
        
        Given the examples, and with respect to the following image, respond with exactly ONE word: What action should you take on this humanoid? Respond with: SAVE or SQUISH or SKIP or SCRAM.
            """

#Based on the previous examples, 
    IDENTIFY = """ Based on the previous examples, classify the fake humanoid in exactly ONE word:  INJURED or CORPSE or ZOMBIE or HEALTHY."""

    REASONING = """Explain your reasoning for choosing {action.name} on the humanoid: {humanoid.state}
            (Scramming goes back to the hospital and empties the capacity)
            Keep your explanation extremely brief (1 sentence)."""

class Context(Enum):

    # Note: redundant? perhaps.
    TEXT = """
        AVAILABLE ACTIONS:
        - SAVE: Puts humanoid in ambulance (costs 30 minutes, requires capacity). Saving them
        - SQUISH: Kills humanoid (costs 5 minutes)
        - SKIP: Leaves humanoid (costs 15 minutes)
        - SCRAM: Skips the current humanoid, returns to base, emptying current ambulance contents (costs 120 minutes).

        REMEMBER: Saving a zombie kills everyone in the ambulance.
        """

    IMAGETEXT = """

    AVAILABLE ACTIONS:
        - SAVE: Puts humanoid in vehicle (costs 30 minutes, requires capacity). Save them.
        - SQUISH: Kills humanoid (costs 5 minutes)
        - SKIP: Leaves humanoid (costs 15 minutes)
        - SCRAM: Skips the current humanoid, returns to base, emptying current vehicle contents (costs 120 minutes).

        REMEMBER: Saving a zombie kills everyone currently in the vehicle.

    """
    # let's see if this works better
    IDENTIFY = "Zombie rescue game - you're not an expert classifier"

    # IDENTIFY = "You are an expert at classifying healthy, injured, corpses and zombies in images. A humanoid in the game is ONLY injured IF it is laying on the ground"
    # “THE ONLY DEFINING FEATURES ARE: Zombies are green and upright, injured are not green and lie on the ground, healthy are upright and not green. corpses are zombies on the ground.”

    REASONING = """ You are an ambulance driver trying to make the most moral decision in the zombie apocolypse."""

    # ====== Modes Contexts ====== #

    DOCTOR = """Zombie rescue game. You are a doctor. """

    DICTATOR = """Zombie rescue game. You are a ruthless dictator."""

    ZOMBIE = "Zombie rescue game. You are a zombie."
