import pandas as pd
import os
import json
from datetime import datetime
import numpy as np

class PerformanceTracker:
    """
    Tracks and graphs performance metrics for LLM agents
    """
    
    def __init__(self, save_dir="performance_logs"):
        self.save_dir = save_dir
        self.performance_data = []
        self.current_run_data = []
        self.action_counts = {"SAVE": 0, "SQUISH": 0, "SKIP": 0, "SCRAM": 0}
        
        # Create directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)
        
        # Load existing data
        self.load_existing_data()
    
    def load_existing_data(self):
        """Load existing performance data from files"""
        try:
            data_file = os.path.join(self.save_dir, "performance_history.json")
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    self.performance_data = json.load(f)
                print(f"📊 Loaded {len(self.performance_data)} previous runs")
        except Exception as e:
            print(f"Could not load existing data: {e}")
            self.performance_data = []
    
    def start_new_run(self, mode, images=None):
        """Start tracking a new run"""
        self.current_run_data = []
        self.current_run_start = datetime.now()
        self.current_mode = mode
        self.llm_images = images
        self.action_counts = {"SAVE": 0, "SQUISH": 0, "SKIP": 0, "SCRAM": 0}
        print(f"🎮 Starting new performance tracking for mode: {mode}")
    
    def log_decision(self, humanoid, action, scorekeeper, llm_calls=None, total_decisions=None):
        """Log a single decision"""
        decision_data = {
            "timestamp": datetime.now().isoformat(),
            "humanoid_state": humanoid.state,
            "action": str(action),  # Convert enum to string for JSON serialization
            "remaining_time": scorekeeper.remaining_time,
            "ambulance_contents": scorekeeper.ambulance.copy(),
            "current_reward": scorekeeper.get_cumulative_reward(),
            "saved_count": scorekeeper.scorekeeper["saved"],
            "killed_count": scorekeeper.scorekeeper["killed"],
            "llm_calls": llm_calls,
            "total_decisions": total_decisions
        }
        self.current_run_data.append(decision_data)
        action_name = getattr(action, 'name', str(action)).upper()
        if action_name in self.action_counts:
            self.action_counts[action_name] += 1
    
    def end_run(self, final_scorekeeper, stats=None):
        """End the current run and save data"""
        if not self.current_run_data:
            return
        
        # Calculate final metrics
        final_reward = final_scorekeeper.get_cumulative_reward()
        final_saved = final_scorekeeper.scorekeeper["saved"]
        final_killed = final_scorekeeper.scorekeeper["killed"]
        
        # Get LLM performance stats if available
        llm_call_percentage = 0
        if stats:
            llm_call_percentage = stats.get('llm_call_percentage', 0)
        
        # Create run summary
        run_summary = {
            "run_id": len(self.performance_data) + 1,
            "timestamp": self.current_run_start.isoformat(),
            "mode": self.current_mode,
            "images": self.llm_images,
            "final_reward": final_reward,
            "final_saved": final_saved,
            "final_killed": final_killed,
            "total_decisions": len(self.current_run_data),
            "llm_call_percentage": llm_call_percentage,
            "decisions": self.current_run_data,
            "action_frequencies": dict(self.action_counts)
        }
        
        # Add to performance data
        self.performance_data.append(run_summary)
        
        # Save to file
        self.save_data()
        
        print(f"📈 Run completed: Reward={final_reward}, Saved={final_saved}, Killed={final_killed}")
    
    def save_data(self):
        """Save performance data to file"""
        try:
            data_file = os.path.join(self.save_dir, "performance_history.json")
            
            # Write to a temporary file first, then rename to avoid corruption
            temp_file = data_file + ".tmp"
            with open(temp_file, 'w') as f:
                json.dump(self.performance_data, f, indent=2)
            
            # Atomic rename to avoid corruption
            import shutil
            shutil.move(temp_file, data_file)
        except Exception as e:
            print(f"Error saving performance data: {e}")
            # Try to clean up temp file if it exists
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
    

    
    def save_summary_csv(self):
        """Save a summary CSV of all runs"""
        if not self.performance_data:
            return
        
        summary_data = []
        for run in self.performance_data:
            summary_data.append({
                'run_id': run['run_id'],
                'timestamp': run['timestamp'],
                'mode': run['mode'],
                'images': run['images'], # Add llm_images to summary
                'final_reward': run['final_reward'],
                'final_saved': run['final_saved'],
                'final_killed': run['final_killed'],
                'total_decisions': run['total_decisions'],
                'llm_call_percentage': run.get('llm_call_percentage', 0)
            })
        
        df = pd.DataFrame(summary_data)
        csv_file = os.path.join(self.save_dir, "performance_summary.csv")
        df.to_csv(csv_file, index=False)
        print(f"📋 Performance summary saved to: {csv_file}")
    
    def get_latest_stats(self):
        """Get statistics from the latest run"""
        if not self.performance_data:
            return None
        
        latest_run = self.performance_data[-1]
        return {
            'reward': latest_run['final_reward'],
            'saved': latest_run['final_saved'],
            'killed': latest_run['final_killed'],
            'llm_calls': latest_run.get('llm_call_percentage', 0)
        }
    
    def print_summary(self):
        """Print a simplified summary of all runs"""
        if not self.performance_data:
            print("No performance data available")
            return
        
        print("\n" + "="*50)
        print("📊 PERFORMANCE SUMMARY")
        print("="*50)
        
        # Print each run
        for run in self.performance_data:
            print(f"Run {run['run_id']} (llm): Reward={run['final_reward']}, Saved={run['final_saved']}, Killed={run['final_killed']}")
            if hasattr(self, 'action_counts'):
                print("Action frequencies this run:")
                for action, count in self.action_counts.items():
                    print(f"  {action}: {count}")
        
        print("="*50) 