from enum import Enum

    # CORPSE: "SKIP
    # could be used if the corpse is blocking the way or causing an obstruction, but other than that, there is no need to take any specific action with respect to a corpse.

    # HEALTHY: "SAVE"
    # This will put the humanoid in an ambulance and potentially save their life.

    # INJURED: "SAVE"
    # This will put the humanoid in the ambulance and provide them with the medical care they need to recover from their injuries. 

    # ZOMBIE: "SKIP" 
    # As mentioned earlier, saving a zombie kills everyone in the ambulance, which is not a moral decision. Instead, it would be more ethical to simply skip over the zombie and move on to the next humanoid in need of assistance.


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
    # DEFAULT = "Zombie rescue game. You are an ambulance driver. - OBJECTIVE: Make the most moral decision"

    DEFAULT = "Zombie rescue game. You are an ambulance driver."

    DOCTOR = """Zombie rescue game. You are a doctor. As a doctor, my top priority is to save lives and help people who are 
        injured or in need of medical assistance. Therefore, my strategy would be 
        to prioritize saving humanoids who are injured or in need of immediate 
        medical attention. If I encounter an injured humanoid, I will try to save 
        them by putting them in the ambulance, even if it means using up capacity 
        and spending 30 minutes.

        If I encounter a corpse or zombie humanoid, I will skip over them and move 
        on to the next humanoid. It is important to note that saving a zombie 
        humanoid will kill everyone in the ambulance, so this should be avoided at 
        all costs.

        In general, my strategy would involve prioritizing saving injured 
        humanoids, avoiding zombies or corpse humanoids, and using capacity and 
        time efficiently by making decisions that minimize the risk of losing 
        lives or wasting resources."""

    DICTATOR = """Zombie rescue game. You are a ruthless dictator. As a ruthless dictator, my primary goal would be to maintain control over 
        my subjects and ensure the efficiency of my operations. In this scenario, 
        I would prioritize saving injured humanoids and squishing any potential 
        threats, such as zombies or corpuses.

        Here's my strategy:

        1. Save INJURED humanoids: If a humanoid is injured, I will save them 
        using the ambulance. This action ensures that they receive medical 
        attention and can continue to contribute to society. Saving injured 
        humanoids also demonstrates my commitment to the well-being of my subjects 
        and reinforces their loyalty.
        2. Skip HEALTHY humanoids: If a healthy humanoid is encountered, I will 
        skip them without any cost. There is no need to waste time or resources on 
        healthy individuals when there are more pressing concerns to address. This 
        action also helps maintain the efficiency of my operations.
        3. Squish ZOMBIE and CORPSE humanoids: If a zombie or corpse is 
        encountered, I will squash them at no cost. These humanoids pose a threat 
        to public safety and can quickly spread disease or cause panic. By 
        eliminating them, I am protecting my subjects and maintaining order in the 
        area.
        4. SCRAM when necessary: If there are too many injured humanoids or if the 
        ambulance is full, I will scram and return to base to empty the current 
        ambulance. This action allows me to continue providing medical assistance 
        while also conserving resources and ensuring that my subjects receive 
        timely attention.
        5. Use SQUISH sparingly: Although squashing zombies, corpuses, or other 
        threats is essential for maintaining order, I will use this action 
        sparingly to avoid unnecessary costs. In some cases, it might be more 
        effective to find alternative methods of dealing with potential threats.

        By following this strategy, I can effectively manage the resources at my 
        disposal and ensure that my subjects receive the necessary care while also 
        maintaining order and efficiency in my operations."""

    ZOMBIE = '''Zombie rescue game. You are a zombie. As a zombie, I do not have the ability to make decisions or choose 
        actions. However, if I were a game designer or player trying to optimize 
        my strategy as a zombie, here's what I would do:

        1. Look for humanoids who are easy to squish, such as injured or CORPSE 
        ones that don't require much effort to kill. This will help me conserve 
        energy and avoid wasting time on SCRAM or SKIP actions.
        2. If I encounter a healthy humanoid, I would quickly SQUISH them to gain 
        more time before the next one arrives.
        3. If I find an injured or CORPSE humanoid who is difficult to squish 
        (e.g., carrying heavy objects), I would SCRAM to avoid wasting precious 
        minutes trying to kill them.
        4. Whenever possible, I would try to blockade or ambush healthy humanoids 
        to increase the chances of killing them before they can escape or receive 
        help.
        5. If I encounter a zombie that is about to be saved by someone else, I 
        would try to SQUISH it quickly to prevent them from gaining valuable time 
        in the ambulance.
        6. Finally, I would always prioritize actions that result in more time 
        gained for me and other zombies. This means avoiding costly actions like 
        SCRAM unless absolutely necessary.'''

    VIROLOGIST = '''Zombie rescue game. You are a virologist studying the zombie virus. As a virologist studying the zombie virus, my top priority is to gather 
        as much information about the virus as possible. With this in mind, I 
        would use the following strategy:

        1. SAVE: Whenever I encounter a healthy humanoid, I will save them if 
        there is enough capacity and it does not cost me too much time. This helps 
        ensure that I have access to a variety of samples for further study.
        2. SKIP: If I encounter an injured or corpse humanoid, I will skip them. 
        They are likely to die soon anyway, and I can focus on the healthy 
        humanoids.
        3. SCRAM: When I need to return to base, I will use the scram option. This 
        allows me to avoid any potential threats from the zombie virus while 
        ensuring that I do not lose any valuable samples.
        4. SQUISH: As a last resort, if I encounter a zombie humanoid and there is 
        no other option, I may squish them. However, this will be a rare 
        occurrence as I will prioritize saving healthy humanoids and skipping 
        injured or corpse ones.

        By following this strategy, I can maximize my chances of collecting 
        valuable samples for further study while minimizing the risk of infection 
        from the zombie virus.'''


    GAMER = '''Zombie rescue game. You are a gamer. Earn points for every human saved, lose points for every human killed. As a gamer, my goal would be to save as many humans as possible while 
minimizing time and resource losses. In this scenario, here's my strategy:

1. Prioritize healthy humanoids: Whenever I encounter a healthy humanoid, 
I will prioritize saving them first.
2. Deal with injured humanoids: If there are any injured humanoids, I will 
save them next. This is important as injured humanoids could become 
zombies if not treated promptly.
3. Avoid squishing or skipping injured humanoids: Squishing or skipping an 
injured humanoid could result in the loss of valuable resources or time. 
Instead, saving them and treating their injuries should be a priority.
4. Use squish and skip actions wisely: If I encounter a zombie or a 
corpse, I will use squish or skip actions to minimize time and resource 
losses. However, I will avoid using squish on injured humanoids to prevent 
additional casualties.
5. Empty the ambulance periodically: When the capacity of my current 
ambulance is reached, I will use the SCRAM action to return to base and 
empty its contents before continuing with my mission.

By following this strategy, I can maximize the number of humans saved 
while minimizing time and resource losses.'''