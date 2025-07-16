#!/usr/bin/env python3
"""
Generate performance graphs from saved logs
Run this script to create graphs from your performance data
"""

import matplotlib.pyplot as plt
import pandas as pd
import os
import json
from datetime import datetime
import numpy as np

def load_performance_data(save_dir="performance_logs"):
    """Load performance data from saved files"""
    data_file = os.path.join(save_dir, "performance_history.json")
    if not os.path.exists(data_file):
        print("❌ No performance data found. Run the game first to collect data.")
        return None
    
    try:
        with open(data_file, 'r') as f:
            content = f.read().strip()
            if not content:
                print("📝 Performance data file is empty. Run the game first to collect data.")
                return None
            performance_data = json.loads(content)
        print(f"📊 Loaded {len(performance_data)} runs from performance data")
        return performance_data
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error in performance data: {e}")
        print("💡 This usually happens when the file was corrupted during writing.")
        print("🔄 Attempting to fix the file...")
        
        # Try to fix the file by creating a backup and starting fresh
        backup_file = os.path.join(save_dir, "performance_history_corrupted_backup.json")
        try:
            import shutil
            shutil.copy2(data_file, backup_file)
            print(f"📋 Corrupted file backed up to: {backup_file}")
            
            # Create a fresh empty file
            with open(data_file, 'w') as f:
                json.dump([], f)
            print("✅ Created fresh performance data file")
            return []
        except Exception as backup_error:
            print(f"❌ Could not fix the file: {backup_error}")
            return None
    except Exception as e:
        print(f"❌ Error loading performance data: {e}")
        return None

def generate_graphs(performance_data, save_dir="performance_logs"):
    """Generate comprehensive performance graphs"""
    if not performance_data:
        print("❌ No data to graph")
        return
    
    # Set up the plotting style
    plt.style.use('default')
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('LLM Agent Performance Analysis', fontsize=16, fontweight='bold')
    
    # Extract data for plotting
    run_ids = [run['run_id'] for run in performance_data]
    rewards = [run['final_reward'] for run in performance_data]
    saved_counts = [run['final_saved'] for run in performance_data]
    killed_counts = [run['final_killed'] for run in performance_data]
    llm_percentages = [run.get('llm_call_percentage', 0) for run in performance_data]
    
    # 1. Reward over time
    axes[0].scatter(run_ids, rewards, color='blue', alpha=0.7, s=50)
    axes[0].plot(run_ids, rewards, color='blue', alpha=0.3, linewidth=1)
    axes[0].set_title('Final Reward by Run')
    axes[0].set_xlabel('Run ID')
    axes[0].set_ylabel('Reward (Saved - Killed)')
    axes[0].grid(True, alpha=0.3)
    
    # Add trend line
    if len(run_ids) > 1:
        z = np.polyfit(run_ids, rewards, 1)
        p = np.poly1d(z)
        axes[0].plot(run_ids, p(run_ids), "r--", alpha=0.8, linewidth=2)
    
    # 2. Saved vs Killed scatter
    axes[1].scatter(saved_counts, killed_counts, color='blue', alpha=0.7, s=50)
    axes[1].set_title('Saved vs Killed')
    axes[1].set_xlabel('Number Saved')
    axes[1].set_ylabel('Number Killed')
    axes[1].grid(True, alpha=0.3)
    
    # Add diagonal line (reward = 0)
    max_val = max(max(saved_counts), max(killed_counts))
    axes[1].plot([0, max_val], [0, max_val], 'k--', alpha=0.5, label='Reward = 0')
    axes[1].legend()
    
    # 3. LLM Call Percentage
    if any(llm_percentages):
        axes[2].scatter(run_ids, llm_percentages, color='blue', alpha=0.7, s=50)
        axes[2].set_title('LLM Call Percentage')
        axes[2].set_xlabel('Run ID')
        axes[2].set_ylabel('LLM Calls (%)')
        axes[2].grid(True, alpha=0.3)
    else:
        axes[2].text(0.5, 0.5, 'No LLM call data available', 
                       ha='center', va='center', transform=axes[2].transAxes)
        axes[2].set_title('LLM Call Percentage')
    
    # Save the plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_file = os.path.join(save_dir, f"performance_graph_{timestamp}.png")
    plt.tight_layout()
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"📊 Performance graphs saved to: {plot_file}")
    
    # Also save a summary CSV
    save_summary_csv(performance_data, save_dir)

def save_summary_csv(performance_data, save_dir):
    """Save a summary CSV of all runs"""
    if not performance_data:
        return
    
    summary_data = []
    for run in performance_data:
        summary_data.append({
            'run_id': run['run_id'],
            'timestamp': run['timestamp'],
            'final_reward': run['final_reward'],
            'final_saved': run['final_saved'],
            'final_killed': run['final_killed'],
            'total_decisions': run['total_decisions'],
            'llm_call_percentage': run.get('llm_call_percentage', 0)
        })
    
    df = pd.DataFrame(summary_data)
    csv_file = os.path.join(save_dir, "performance_summary.csv")
    df.to_csv(csv_file, index=False)
    print(f"📋 Performance summary saved to: {csv_file}")

def print_colorful_summary(performance_data):
    """Print a summary of all runs (no color coding or mode distinction)"""
    if not performance_data:
        print("No performance data available")
        return
    
    print("\n" + "="*60)
    print("📊 PERFORMANCE SUMMARY")
    print("="*60)
    
    # Print each run
    for run in performance_data:
        print(f"Run {run['run_id']} (llm): Reward={run['final_reward']}, Saved={run['final_saved']}, Killed={run['final_killed']}")
    
    # Overall stats
    total_runs = len(performance_data)
    avg_reward = np.mean([run['final_reward'] for run in performance_data])
    best_reward = max([run['final_reward'] for run in performance_data])
    worst_reward = min([run['final_reward'] for run in performance_data])
    
    print(f"\n📈 Overall Stats:")
    print(f"Total Runs: {total_runs}")
    print(f"Average Reward: {avg_reward:.2f}")
    print(f"Best Reward: {best_reward}")
    print(f"Worst Reward: {worst_reward}")
    print("="*60)

def clear_performance_data(save_dir="performance_logs"):
    """Clear all performance data"""
    data_file = os.path.join(save_dir, "performance_history.json")
    csv_file = os.path.join(save_dir, "performance_summary.csv")
    
    if os.path.exists(data_file):
        # Create backup before clearing
        backup_file = os.path.join(save_dir, f"performance_history_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        import shutil
        shutil.copy2(data_file, backup_file)
        print(f"📋 Data backed up to: {backup_file}")
        
        # Clear the file
        with open(data_file, 'w') as f:
            json.dump([], f)
        print("🗑️ Performance data cleared")
    else:
        print("📝 No performance data to clear")
    
    # Also clear CSV if it exists
    if os.path.exists(csv_file):
        os.remove(csv_file)
        print("🗑️ Performance summary CSV cleared")

def main():
    """Main function to generate graphs"""
    import sys
    
    # Check for clear command
    if len(sys.argv) > 1 and sys.argv[1] == '--clear':
        print("🗑️ Clearing performance data...")
        clear_performance_data()
        return
    
    print("📊 LLM Performance Graph Generator")
    print("="*40)
    print("Usage:")
    print("  python3 generate_graphs.py          # Generate graphs")
    print("  python3 generate_graphs.py --clear  # Clear all data")
    print("="*40)
    
    # Load performance data
    performance_data = load_performance_data()
    if not performance_data:
        return
    
    # Print colorful summary
    print_colorful_summary(performance_data)
    
    # Generate graphs
    print("\n🔄 Generating graphs...")
    generate_graphs(performance_data)
    
    print("\n✅ Graph generation complete!")
    print("💡 Run this script anytime to update your graphs with new data.")

if __name__ == "__main__":
    main() 