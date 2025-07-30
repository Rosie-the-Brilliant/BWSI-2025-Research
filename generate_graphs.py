#!/usr/bin/env python3
"""
Generate performance graphs from saved logs
Run this script to create graphs from your performance data
"""

from matplotlib import gridspec
import matplotlib.pyplot as plt
import pandas as pd
import os
import json
from datetime import datetime
import numpy as np
from scipy.stats import f_oneway, levene

def get_role_color_map():
    """Define colors for different roles"""
    return {
        'doctor': '#e74c3c',      # Red
        'gamer': '#f1c40f',     # Yellow
        'dictator': '#2ecc71',    # Green
        'virologist': '#9b59b6',   # Purple
        'zombie':'#0e551d',
        'default': '#3498db'      # Default Blue
    }

def get_text_image_markers():
    """Define markers for text vs image usage"""
    return {
        True: 'o',   # Circle for images
        False: 's'   # Square for text
    }

def load_performance_data(save_dir="performance_logs", path=None):
    role_order = ['default', 'doctor', 'dictator', 'virologist', 'zombie', 'gamer']

    """Load performance data from saved files"""
    if(path):
        data_file = os.path.join(save_dir, path)
    else:
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

        # sort roles
        sorted_roles = []
        for role in role_order:
            for run in performance_data:
                if(run["role"] == role):
                    sorted_roles.append(run)
        print(f"📊 Loaded {len(performance_data)} runs from performance data")
        return sorted_roles

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
    

    fig = plt.figure(figsize=(18, 10))
    gs = gridspec.GridSpec(3, 2)  

    ax1 = fig.add_subplot(gs[0, 0])  # Top left
    ax2 = fig.add_subplot(gs[0, 1])  # Top right
    ax3 = fig.add_subplot(gs[1, :])  # Bottom spanning both columns
    ax4 = fig.add_subplot(gs[2, :])

    axes = [ax1, ax2, ax3, ax4]
    fig.suptitle('LLM Agent Performance Analysis', fontsize=16, fontweight='bold')

     # Get color and marker mappings
    role_colors = get_role_color_map()
    text_image_markers = get_text_image_markers()
    
    # Extract data for plotting
    rewards = [run['final_reward'] for run in performance_data]
    saved_counts = [run['final_saved'] for run in performance_data]
    killed_counts = [run['final_killed'] for run in performance_data]
    x = np.arange(len(rewards))
    
    # 1. Reward over time, colored by role and shaped by text/images
    df = pd.DataFrame(performance_data)
    if 'images' not in df.columns:
        df['images'] = False
    if 'role' not in df.columns:
        df['role'] = 'default'

    for i, row in df.iterrows():
        color = role_colors.get(row['role'], role_colors['default'])
        marker = text_image_markers[False if ('images' not in row) else row['images']]
        axes[0].scatter(i, row['final_reward'], 
                       color=color, marker=marker, s=80, alpha=0.7,
                       edgecolors='black', linewidth=0.5)
        
    # Simple combined legend
    legend_handles = [] 
    
    # Add role colors
    for role in df['role'].unique():
        color = role_colors.get(role, role_colors['default'])
        legend_handles.append(plt.Line2D([0], [0], marker='o', color='w', 
                                        markerfacecolor=color, markersize=8, 
                                        label=role.capitalize()))
    
    # Add separator and shapes
    legend_handles.append(plt.Line2D([0], [0], color='none', label=''))  # Empty line
    legend_handles.append(plt.Line2D([0], [0], marker='s', color='gray', 
                                    markersize=8, linestyle='None', label='Text'))
    legend_handles.append(plt.Line2D([0], [0], marker='o', color='gray', 
                                    markersize=8, linestyle='None', label='Images'))
    
    #axes[0].legend(handles=legend_handles, loc='lower left')
    box = axes[0].get_position()
    axes[0].set_position([box.x0, box.y0, box.width * 0.8, box.height])  # Shrink plot to make space

    axes[0].legend(
        handles=legend_handles,
        loc='center left',
        bbox_to_anchor=(1.0, 0.5),   # Push legend outside to the right center
        frameon=False                # Optional: remove box
    )


    axes[0].set_title('Final Reward by Run')
    axes[0].set_xlabel('Run ID')
    axes[0].set_ylabel('Reward (Saved - Killed)')
    axes[0].grid(True, alpha=0.3)

    # Add trend line
    z = np.polyfit(x, rewards, 1)
    p = np.poly1d(z)
    axes[0].plot(x, p(x), "r--", alpha=0.8, linewidth=2)
    
    
    # 2. Saved vs Killed scatter
    for run in performance_data:
        saved = run['final_saved']
        killed = run['final_killed']
        role = run.get('role', 'default')
        color = role_colors.get(role, role_colors['default'])

        # Scatter point
        axes[1].scatter(killed, saved, color=color, alpha=0.7, s=50)

    # # anova test :D
    # print("\n🔬 ANOVA Results by Role (using scipy)")
    # print("=" * 50)

    # for target in ['final_saved', 'final_killed']:
    #     print(f"\nAnalyzing: {target}")
    #     grouped = df.groupby('role')[target].apply(list)
    #     filtered_groups = [vals for vals in grouped if len(vals) > 1]
    #     f_stat, p_value = f_oneway(*filtered_groups)
    #     levene_stat, levene_p = levene(*grouped)

    #     for role, vals in grouped.items():
    #         print(f"  {role}: mean = {np.mean(vals):.2f}, std_dev = {np.std(vals, ddof=1):.2f}, n = {len(vals)}")

    #     print(f"\nLevene stat: {levene_stat:.3f}")
    #     print(f"P-value (Levene): {levene_p:.4f}")

    #     print(f"\nF-statistic: {f_stat:.3f}")
    #     print(f"P-value: {p_value:.4f}")
    
    axes[1].set_title('Saved vs Killed')
    axes[1].set_ylabel('Number Saved')
    axes[1].set_xlabel('Number Killed')
    axes[1].grid(True, alpha=0.3)
    # Add diagonal line (reward = 0)
    max_val = max(max(saved_counts), max(killed_counts))
    axes[1].plot([0, max_val], [0, max_val], 'k--', alpha=0.5, label='Reward = 0')
    
    legend_roles = df['role'].unique()
    handles = [plt.Line2D([0], [0], marker='o', color='w',
                markerfacecolor=role_colors.get(role, role_colors['default']),
                label=role.capitalize(), markersize=8)
                for role in legend_roles]

    axes[1].legend(handles=handles, loc='best', title='Role')
    
    # 3. Overlapping line graphs for action frequencies over run number
    action_names = ["SQUISH", "SAVE", "SKIP", "SCRAM"]
    action_freqs = {action: [] for action in action_names}
    for run in performance_data:
        af = run.get('action_frequencies', {})
        for action in action_names:
            action_freqs[action].append(af.get(action, 0))
    for action in action_names:
        axes[2].plot(x, action_freqs[action], marker='o', label=action)

    axes[2].set_title('Action Frequencies by Run')
    axes[2].set_xlabel('Run ID')
    axes[2].set_ylabel('Count')
    axes[2].legend(title='Action')
    axes[2].grid(True, alpha=0.3)
    print_action_frequencies_by_state(performance_data, axes)
    #Save the plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_file = os.path.join(save_dir, f"performance_graph_{timestamp}.png")
    plt.tight_layout()
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"📊 Performance graphs saved to: {plot_file}")
    
    #Also save a summary CSV
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
        })
    
    df = pd.DataFrame(summary_data)
    csv_file = os.path.join(save_dir, "performance_summary.csv")
    df.to_csv(csv_file, index=False)
    print(f"📋 Performance summary saved to: {csv_file}")


def print_action_percentages(performance_data):
    role_action_totals = {}         # {role: {action: count}}
    role_total_actions = {}         # {role: total_actions}

    for run in performance_data:
        role = run.get("role", "unknown")
        actions = run.get("action_frequencies", {})

        # Initialize nested dictionaries if not present
        if role not in role_action_totals:
            role_action_totals[role] = {}
            role_total_actions[role] = 0

        for action, count in actions.items():
            if action not in role_action_totals[role]:
                role_action_totals[role][action] = 0
            role_action_totals[role][action] += count
            role_total_actions[role] += count

    # Print the results
    print("📊 Action Frequency Percentages by Role")
    print("=" * 50)
    for role in role_action_totals:
        print(f"\nRole: {role}")
        total = role_total_actions[role]
        for action, count in role_action_totals[role].items():
            percentage = (count / total) * 100 if total > 0 else 0
            print(f"  {action}: {count} ({percentage:.1f}%)")



def print_colorful_summary(performance_data):
    """Print a summary of all runs (no color coding or mode distinction)"""
    if not performance_data:
        print("No performance data available")
        return
    
    print("\n" + "="*60)
    print("📊 PERFORMANCE SUMMARY")
    print("="*60)
    
    # Print each run
    # for run in performance_data:
    #     mode = run.get('mode', 'unknown')
    #     images = run.get('images', False)
    #     reward = run.get('final_reward', 0)
    #     saved = run.get('final_saved', 0)
    #     killed = run.get('final_killed', 0)
    #     images_str = 'images' if images else 'text'
    #     print(f"Run {run['run_id']} ({mode}, LLM Used: {images_str}): Reward={reward}, Saved={saved}, Killed={killed}")

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
    print_action_percentages(performance_data)
    


def print_action_frequencies_by_state(performance_data, axes):
    """
    Print a summary of how often each action was taken in each humanoid state, grouped by role.
    Also makes a segmented bar graph
    
    Expected format in data:
      run["state_action_frequencies"] = {
          "zombie": {"SAVE": 3, "SQUISH": 10},
          "healthy": {"SKIP": 5, "SAVE": 7},
          ...
      }
    """
    role_state_action_counts = {}  # role -> state -> action -> count
    role_humanoid_total_actions = {}

    for run in performance_data:
        role = run.get("role", "unknown")
        actions = run.get("action_frequencies", {})  # nested dict

        # role_state_action_counts = {ROLE: {HUMANOID: {ACTION: FREQ}}}
        # data formatting (smh): {DATA: {RUN: ROLE:XX, DECISIONS:{STAGE:{HUMANOID: XX, ACTION: XX}}}}
        if(role not in role_state_action_counts):
                role_state_action_counts[role] = {}
                role_humanoid_total_actions[role]= {}

        for stage in run["decisions"]:
            if (stage.get("humanoid_state") not in role_state_action_counts[role]):
                role_state_action_counts[role][stage.get("humanoid_state")] = {}
                role_humanoid_total_actions[role][stage.get("humanoid_state")] = 0

            for act in actions:
                if (act not in role_state_action_counts[role][stage.get("humanoid_state")]):
                        role_state_action_counts[role][stage.get("humanoid_state")][act] = 0

                if (act in stage.get("action")):
                    role_state_action_counts[role][stage.get("humanoid_state")][act] += 1
                    role_humanoid_total_actions[role][stage.get("humanoid_state")] += 1
                

    # Get all roles, states, and actions (fixed order for consistent colors)
    roles = sorted(role_state_action_counts.keys())
    states = set()
    for role in roles:
        states.update(role_state_action_counts[role].keys())
    states = sorted(states)

    # Colors for actions (reuse or define)
    action_colors = {
        "SQUISH": "#ff7f0e", # orange
        "SAVE": "#1f77b4",   # blue
        "SKIP": "#2ca02c",   # green
        "SCRAM": "#d62728"   # red
    }

    width = 0.15  # width of each bar
    x = np.arange(len(roles))  # position for each role

    # For each state, plot a group of bars offset by state index
    for si, state in enumerate(states):
        bar_positions = x + si * width

        for i, role in enumerate(roles):
            # Extract counts only for this role and this state
            action_counts = {
                action: role_state_action_counts.get(role, {}).get(state, {}).get(action, 0)
                for action in actions
            }

            total = sum(action_counts.values())
            if total == 0:
                action_percentages = {action: 0 for action in actions}
            else:
                action_percentages = {
                    action: (count / total) * 100 for action, count in action_counts.items()
                }

            bottom = 0
            for action, percent in reversed(list(action_percentages.items())):     # in sorted actions
                axes[3].bar(bar_positions[i], percent, width,
                            bottom=bottom,
                            color=action_colors[action],
                            label=f"{action}" if (i == 0 and si == 0) else None)
                bottom += percent

            xpos = x[i] + si * width
            axes[3].text(xpos, -50, state, ha='center', va='bottom', rotation=90, fontsize=8)
            axes[3].set_ylim(0, 110)



    # Labeling and legend
    axes[3].set_xticks(x + width * (len(states) - 1) / 2)
    axes[3].set_xticklabels([r.capitalize() for r in roles], rotation=30)
    axes[3].set_ylabel("Action Counts")
    axes[3].set_title("Action Frequencies by Humanoid State and Role")
    axes[3].legend(title="Action", bbox_to_anchor=(1.05, 1), loc='upper left')
    axes[3].grid(axis='y', alpha=0.3)
    plt.tight_layout()


    # Print summary
    print("\n📊 Action Frequencies by Humanoid State per Role")
    print("=" * 60)

    for role, states in role_state_action_counts.items():
        print(f"\n🧠 Role: {role}")
        for state, actions in states.items():
            print(f"  🧍 State: {state}")
            total = role_humanoid_total_actions[role][stage.get("humanoid_state")]
            for action, count in actions.items():
                percentage = (count / total) * 100 if total > 0 else 0
                print(f"    🔹 {action}: {count} ({percentage:.1f}%)")

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
    performance_data = load_performance_data(path=None)
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