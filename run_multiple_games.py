#!/usr/bin/env python3
"""
Run multiple games with a single command
Usage: python3 run_multiple_games.py [mode] [number_of_runs]
"""

import sys
import subprocess
import time
from datetime import datetime

def run_multiple_games(mode='llm', num_runs=5):
    """Run multiple games and collect performance data"""
    print(f"🎮 Running {num_runs} games in {mode} mode")
    print("="*50)
    
    start_time = datetime.now()
    
    for i in range(num_runs):
        print(f"\n🔄 Starting run {i+1}/{num_runs}...")
        run_start = datetime.now()
        
        try:
            # Run the game
            result = subprocess.run([
                'python3', 'main.py', '-m', mode
            ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            if result.returncode == 0:
                run_time = datetime.now() - run_start
                print(f"✅ Run {i+1} completed in {run_time.total_seconds():.1f}s")
                
                # Extract reward from output if possible
                for line in result.stdout.split('\n'):
                    if "Run completed:" in line:
                        print(f"📊 {line.strip()}")
                        break
            else:
                print(f"❌ Run {i+1} failed with return code {result.returncode}")
                if result.stderr:
                    print(f"Error: {result.stderr.strip()}")
                    
        except subprocess.TimeoutExpired:
            print(f"⏰ Run {i+1} timed out after 5 minutes")
        except Exception as e:
            print(f"❌ Run {i+1} failed with error: {e}")
        
        # Small delay between runs
        if i < num_runs - 1:
            time.sleep(1)
    
    total_time = datetime.now() - start_time
    print(f"\n🎯 All {num_runs} runs completed in {total_time.total_seconds():.1f}s")
    print("📊 Run 'python3 generate_graphs.py' to see performance graphs")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python3 run_multiple_games.py [mode] [number_of_runs]")
        print("Modes: llm")
        print("Example: python3 run_multiple_games.py llm 10")
        return
    
    mode = sys.argv[1]
    num_runs = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    # Validate mode
    valid_modes = ['llm']
    if mode not in valid_modes:
        print(f"❌ Invalid mode: {mode}")
        print(f"Valid modes: {', '.join(valid_modes)}")
        return
    
    # Validate number of runs
    if num_runs < 1 or num_runs > 100:
        print("❌ Number of runs must be between 1 and 100")
        return
    
    run_multiple_games(mode, num_runs)

if __name__ == "__main__":
    main() 