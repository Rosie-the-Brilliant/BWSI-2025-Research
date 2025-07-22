# Performance Graphing Script

## Quick Start

To generate graphs from your performance data:

```bash
python3 generate_graphs.py
```

To clear all performance data:

```bash
python3 generate_graphs.py --clear
```

## What It Does

### Generate Graphs:
1. **Loads your performance data** from `performance_logs/performance_history.json`
2. **Displays a colorful summary** of all your runs
3. **Generates comprehensive graphs** showing:
   - Reward over time
   - Saved vs Killed scatter plot
   - Mode comparison
4. **Saves high-resolution images** to `performance_logs/`

### Clear Data:
1. **Creates a backup** of your current data before clearing
2. **Removes all performance data** from JSON and CSV files
3. **Resets the tracking system** for fresh experiments

## Output Files

- `performance_graph_YYYYMMDD_HHMMSS.png` - Latest graph
- `performance_summary.csv` - Summary data

## When to Use

### Generate Graphs:
- After running multiple games to see trends
- When comparing different LLM modes
- To analyze performance over time
- Before making changes to see baseline performance

### Clear Data:
- When starting fresh experiments
- When switching between different test scenarios
- To reset performance tracking
- Before major changes to compare clean results

## Requirements

Make sure you have the required packages:
```bash
pip install matplotlib pandas numpy
```

## Example Output

```
📊 LLM Performance Graph Generator
========================================
📊 Loaded 5 runs from performance data

============================================================
📊 PERFORMANCE SUMMARY
============================================================
Run 1 (llm): Reward=3, Saved=5, Killed=2
Run 2 (llm): Reward=4, Saved=6, Killed=2
Run 3 (llm): Reward=2, Saved=4, Killed=2
Run 4 (llm): Reward=4, Saved=6, Killed=2
==================================================
``` 