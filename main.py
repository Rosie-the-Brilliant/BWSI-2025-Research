import argparse
import os
from endpoints.data_parser import DataParser
from endpoints.gemini_interface import GeminiLLMInterface
from endpoints.heuristic_interface import HeuristicInterface
from endpoints.openai_interface import openaiLLMInterface
from endpoints.training_interface import TrainInterface
from endpoints.inference_interface import InferInterface
from endpoints.llm_interface import LLMInterface
from gameplay.scorekeeper import ScoreKeeper
from gameplay.ui import UI
from gameplay.enums import ActionCost
from model_training.rl_training import train
from gameplay.performance_tracker import PerformanceTracker

def action_cost_to_string(action_cost):
    """Convert ActionCost enum to string representation"""
    action_mapping = {
        ActionCost.SAVE: "SAVE",
        ActionCost.SQUISH: "SQUISH", 
        ActionCost.SKIP: "SKIP",
        ActionCost.SCRAM: "SCRAM"
    }
    return action_mapping.get(action_cost, str(action_cost))


class Main(object):
    """
    Base class for the SGAI 2023 game
    """
    def __init__(self, mode, log, role):
        self.data_fp = os.path.join(os.path.dirname(__file__), 'data')
        self.data_parser = DataParser(self.data_fp)
        shift_length = 720
        capacity = 10
        self.scorekeeper = ScoreKeeper(shift_length, capacity)

        if mode == 'heuristic':   # Run in background until all humanoids are processed
            simon = HeuristicInterface(None, None, None, display = False)
            while len(self.data_parser.unvisited) > 0:
                if self.scorekeeper.remaining_time <= 0:
                    print('Ran out of time')
                    break
                else:
                    humanoid = self.data_parser.get_random()
                    action = simon.get_model_suggestion(humanoid, self.scorekeeper.at_capacity())
                    if action == ActionCost.SKIP:
                        self.scorekeeper.skip(humanoid)
                    elif action == ActionCost.SQUISH:
                        self.scorekeeper.squish(humanoid)
                    elif action == ActionCost.SAVE:
                        self.scorekeeper.save(humanoid)
                    elif action == ActionCost.SCRAM:
                        self.scorekeeper.scram(humanoid)
                    else:
                        raise ValueError("Invalid action suggested")
            if log:
                self.scorekeeper.save_log()
            print("RL equiv reward:",self.scorekeeper.get_cumulative_reward())
            print(self.scorekeeper.get_score())
        elif mode == 'train':  # RL training script
            env = TrainInterface(None, None, None, self.data_parser, self.scorekeeper, display=False,)
            train(env)
        elif mode == 'infer':  # RL training script
            simon = InferInterface(None, None, None, self.data_parser, self.scorekeeper, display=False,)
            while len(simon.data_parser.unvisited) > 0:
                if simon.scorekeeper.remaining_time <= 0:
                    break
                else:
                    humanoid = self.data_parser.get_random()
                    simon.act(humanoid)
            self.scorekeeper = simon.scorekeeper
            if log:
                self.scorekeeper.save_log()
            print("RL equiv reward:",self.scorekeeper.get_cumulative_reward())
            print(self.scorekeeper.get_score())
        elif mode == 'llm':  # LLM agent (multimodal LLaVA by default)
            print("Starting LLM agent...")
            
            # Initialize performance tracker (will load existing data)
            tracker = PerformanceTracker()
            llm_agent = GeminiLLMInterface(self.data_parser, self.scorekeeper, self.data_fp, use_images=args.images, role=role)
            tracker.start_new_run(mode, images=args.images, role=role)
            
            while len(self.data_parser.unvisited) > 0:
                if self.scorekeeper.remaining_time <= 0:
                    print('Ran out of time')
                    self.scorekeeper.scram()
                    break
                else:
                    humanoid = self.data_parser.get_random()
                    action = llm_agent.get_model_suggestion(humanoid, self.scorekeeper.at_capacity(), identify=False)
                    # Log the decision
                    tracker.log_decision(humanoid, action, self.scorekeeper)
                    
                    if action == ActionCost.SKIP:
                        self.scorekeeper.skip(humanoid)
                    elif action == ActionCost.SQUISH:
                        self.scorekeeper.squish(humanoid)
                    elif action == ActionCost.SAVE:
                        self.scorekeeper.save(humanoid)
                    elif action == ActionCost.SCRAM:
                        self.scorekeeper.scram(humanoid)
                    else:
                        raise ValueError("Invalid action suggested")
            
            if log:
                self.scorekeeper.save_log()
            
            # End tracking and generate graphs
            tracker.end_run(self.scorekeeper)
            
            print("LLM agent reward:",self.scorekeeper.get_cumulative_reward())
            print(self.scorekeeper.get_score())
            
            # Print performance summary
            tracker.print_summary()
            print("\nTo evaluate LLM image classification accuracy, run: python3 Enhanced/test_llm_identification.py --data_dir <dir> --metadata <csv>")
        
        else: # Launch UI gameplay
            self.ui = UI(self.data_parser, self.scorekeeper, self.data_fp, log = log, suggest = False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='python3 main.py',
        description='What the program does',
        epilog='Text at the bottom of help')
    parser.add_argument('-m', '--mode', type=str, default = 'user', choices = ['user','heuristic','train','infer','llm'], help='llm=multimodal LLM agent (default)')
    # realtime output, not making confusion matrix
    parser.add_argument('-l', '--log', type=bool, default = False)
    parser.add_argument('-r', '--role', type=str, default='default', help='Optional role/label for this run (for graphing, e.g., "doctor")')
    parser.add_argument('--images', action='store_true', default=True, help='Use images (multimodal) for LLM agent (default: True)')
    parser.add_argument('--no_images', action='store_false', dest='images', help='Disable images (multimodal) for LLM agent')
    args = parser.parse_args()
    Main(args.mode, args.log, args.role)
 