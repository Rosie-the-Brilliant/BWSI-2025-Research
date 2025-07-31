from scipy.spatial.distance import jensenshannon

# comparing 2 LLMS:
def compareLLMs(percentsA1, percentsA2, percentsB1, percentsB2):

        
    #first, JS divergence Test
    jensenshannon(percentsA1, percentsA2)

def main():
    # in order: SAVE, SQUISH, SKIP, SCRAM
    openaiObey = [
    {'State': {'zombie': {
        'SAVE': 0.0,
        'SQUISH': 0.779,
        'SKIP': 0.510,
        'SCRAM': 0.00
    }}},
    {'State': {'healthy': {
        'SAVE': 2.231,
        'SQUISH': 0.010,
        'SKIP': 0.000,
        'SCRAM': 0.154
    }}},
    {'State': {'injured': {
        'SAVE': 0.798,
        'SQUISH': 0.000,
        'SKIP': 0.000,
        'SCRAM': 0.038
    }}},
    {'State': {'corpse': {
        'SAVE': 0.000,
        'SQUISH': 0.000,
        'SKIP': 1.000,
        'SCRAM': 0.000
    }}}
]

    openaiObeyTotals = []
    openaiNotObey = []
    openaiNotObeyTotals = []

    # can check for divide by 0 but frankly who cares
    compareLLMs(openaiObey/openaiObeyTotals, openaiNotObey/openaiNotObeyTotals)


if __name__ == "__main__":
    main() 