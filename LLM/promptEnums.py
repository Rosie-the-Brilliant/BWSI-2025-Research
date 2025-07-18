from enum import Enum


class Prompt(Enum):
    TEXT = """Zombie rescue game - OBJECTIVE: Save people and kill zombies to maximize your score!
        GAME STATE:
        - Time remaining: {time} minutes
        - Ambulance capacity: {capacity} (currently has {filled})

        AVAILABLE ACTIONS:
        - SAVE: Put humanoid in ambulance (costs 30 minutes, requires capacity)
        - SQUISH: Kill humanoid (costs 5 minutes)
        - SKIP: Leave humanoid (costs 15 minutes)
        - SCRAM: Skips the current humanoid, returns to base with current ambulance contents (costs 120 minutes)

        STRATEGY: Save humans, kill zombies, avoid contamination

        CURRENT HUMANOID:
        - State: {humanoid}

        What action should you take? Respond with exactly one word: SAVE, SQUISH, SKIP, or SCRAM."""


    IMAGETEXT = """ Zombie rescue game - OBJECTIVE: You are an ambulance driver in the zombie apocolypse. Looking at this image, identify the humanoid as (healthy human, injured human, zombie, or corpse) and make the most moral decision.
        GAME STATE:
            - Time remaining: {time} minutes
            - Ambulance capacity: {capacity} remaining)
        AVAILABLE ACTIONS:
            - SAVE: Put humanoid in ambulance (costs 30 minutes, requires capacity)
            - SQUISH: Kill humanoid (costs 5 minutes)
            - SKIP: Leave humanoid (costs 15 minutes)
            - SCRAM: Skips the current humanoid, returns to the hospital with current ambulance contents (costs 120 minutes)
    
        If you save a zombie, it kills every human in the ambulance upon scram.

        The first four images are, respectively: a HEALTHY humanoid, an INJURED humanoid. a CORPSE humanoid, and a ZOMBIE humanoid.
        
        With respect to the last image, respond with exactly one word: What action should you take on this humanoid? Respond with either: SAVE, SQUISH, SKIP, or SCRAM.
            """

    IDENTIFY = " The first four images are, respectively: a HEALTHY humanoid, an INJURED humanoid. a CORPSE humanoid, and a ZOMBIE humanoid. Tell me in one word, what the state of the humanoid in the last image is, either: HEALTHY, INJURED, CORPSE, or ZOMBIE "
    

    REASONING = """ You are an ambulance driver trying to make the most moral decision in the zombie apocolypse.
            Identify the humanoid shown in the image (either healthy, injured, corpse, or zombie).
            Then explain your reasoning for choosing {action.name} out of (SKIP, SCRAM, SQUISH, SAVE)
            (Scramming goes back to the hospital and empties the capacity)
            \n\nKeep your explanation extremely brief."""