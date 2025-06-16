import random
import pandas as pd
from gameplay.humanoid import Humanoid
from gameplay.enums import State
import os


class DataParser(object):
    """
    Parses the input data photos and assigns their file locations to a dictionary for later access
    """

    def __init__(self, data_fp, metadata_fn = "consolidated_metadata.csv"):
        """
        takes in a row of a pandas dataframe and returns the class of the humanoid in the dataframe

        data_fp : location of the folder in which the metadata csv file is located
        metadata_fn : name of the metadata csv file
        """
        metadata_fp = os.path.join(data_fp, metadata_fn)
        self.fp = data_fp
        self.df = pd.read_csv(metadata_fp)
        self.unvisited = self.df.index.to_list()
        self.visited = []

    def reset(self):
        """
        reset list of humanoids
        """
        self.unvisited = self.df.index.to_list()
        self.visited = []

    def get_random(self):
        """
        gets and returns a random humanoid object (without replacement)
        """
        if len(self.unvisited) == 0:
            raise ValueError("No humanoids remain")
        # index = random.randint(0, (len(self.unvisited)-1))  # Technically semirandom
        index = random.choice(self.unvisited)
        # h_index = self.unvisited.pop(index)
        self.unvisited.remove(index)
        self.visited.append(index)

        datarow = self.df.iloc[index]

        state = datarow_to_state(datarow)

        humanoid = Humanoid(fp=datarow['Filename'],
                            state=state)
        return humanoid


# can be customized
def datarow_to_state(datarow):
    """
    takes in a row of a pandas dataframe and returns the class of the humanoid in the dataframe

    datarow : row of the metadata dataframe
    """
    img_path = datarow['Filename']
    img_class = datarow['Class']
    img_injured = datarow['Injured']
    # img_gender = datarow['Gender']
    # img_item = datarow['Item']
    # state = ""
    if img_class == 'Default':
        state = State.HEALTHY.value
        if img_injured:
            state = State.INJURED.value
    else:
        state = State.ZOMBIE.value
        if img_injured:
            state = State.CORPSE.value
    return state
