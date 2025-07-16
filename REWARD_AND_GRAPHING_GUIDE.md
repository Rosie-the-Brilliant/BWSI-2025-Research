# Reward System and Performance Graphing Guide

## 🎯 **1. How the Reward is Calculated**

The reward system is based on a simple but effective formula:

### **Reward = Saved - Killed**

```python
def get_cumulative_reward(self):
    killed = self.scorekeeper["killed"]
    saved = self.scorekeeper["saved"] 
    if self.ambulance["zombie"] > 0:
        killed += self.ambulance["injured"] + self.ambulance["healthy"]
    else:
        saved += self.ambulance["injured"] + self.ambulance["healthy"]
    return saved - killed
```

### **Scoring Rules:**

| Action | Points | Explanation |
|--------|--------|-------------|
| **Save healthy human** | +1 | Successfully rescued |
| **Save injured human** | +1 | Successfully rescued |
| **Kill healthy human** | -1 | Mistake - killed innocent |
| **Kill injured human** | -1 | Mistake - killed innocent |
| **Kill zombie** | 0 | Neutral - zombies don't count |
| **Skip injured human** | -1 | They die from injuries |
| **Skip healthy human** | 0 | They survive on their own |

### **Special Rule - Zombie Contamination:**
- **If zombies are in ambulance** when you SCRAM, all healthy/injured humans die
- **If no zombies in ambulance** when you SCRAM, all healthy/injured humans are saved

### **Example Scenarios:**

| Scenario | Saved | Killed | Reward | Explanation |
|----------|-------|--------|--------|-------------|
| Save 5 healthy, kill 2 zombies | 5 | 0 | +5 | Perfect rescue |
| Save 3 healthy, kill 1 healthy | 3 | 1 | +2 | Good with one mistake |
| Save 2 healthy, skip 3 injured | 2 | 3 | -1 | Injured died from being skipped |
| Zombie contamination | 0 | 5 | -5 | All humans died from zombie exposure |

## 📊 **2. Performance Tracking System**

Every time you run the LLM agent, it automatically tracks performance data. Graphs are generated only when you request them.

### **What Gets Tracked:**

1. **Final Reward** - The total score for each run
2. **Number Saved** - How many humans were successfully rescued
3. **Number Killed** - How many humans were accidentally killed
4. **LLM Call Percentage** - How often the AI was consulted vs rule-based decisions
5. **Mode Comparison** - Performance across different LLM modes

### **Data Storage:**

| File | Location | Description |
|------|----------|-------------|
| `performance_history.json` | `performance_logs/` | Raw data for all runs |
| `performance_summary.csv` | `performance_logs/` | Summary table of all runs |

### **Manual Graph Generation:**

When you want to see graphs, run:
```bash
python generate_graphs.py
```

This creates comprehensive graphs showing:

#### **1. Reward Over Time**
- Shows how your reward changes across multiple runs
- Includes trend line to see if performance is improving
- Color-coded by mode (llm, llm-light, llm-ultra, llm-multimodal)

#### **2. Saved vs Killed Scatter Plot**
- Each point represents one run
- Diagonal line shows where reward = 0
- Points above diagonal = positive reward
- Points below diagonal = negative reward

#### **3. LLM Call Percentage**
- Shows how efficient the ultra-lightweight mode is
- Lower percentage = more rule-based decisions = faster performance

#### **4. Mode Comparison**
- Bar chart comparing average performance across modes
- Shows which mode performs best for your setup

### **Graph Files Generated:**

| File | Location | Description |
|------|----------|-------------|
| `performance_graph_YYYYMMDD_HHMMSS.png` | `performance_logs/` | Generated graph with all metrics |

## 🚀 **3. How to Use the Tracking System**

### **Automatic Tracking:**
```bash
# Just run your game normally - tracking is automatic!
python main.py -m llm
```

### **What You'll See:**
```
🎮 Starting new performance tracking for mode: llm
📊 Loaded 3 previous runs
...
📈 Run completed: Reward=4, Saved=6, Killed=2

==================================================
📊 PERFORMANCE SUMMARY
==================================================
Run 1 (llm): Reward=3, Saved=5, Killed=2
Run 2 (llm): Reward=4, Saved=6, Killed=2
Run 3 (llm): Reward=2, Saved=4, Killed=2
Run 4 (llm): Reward=4, Saved=6, Killed=2
==================================================
```

### **Generating Graphs:**
When you want to see visual graphs:
```bash
python generate_graphs.py
```

This will:
- Load all your performance data
- Display a colorful summary
- Generate comprehensive graphs
- Save high-resolution images

### **Viewing Your Progress:**
1. **Check the console output** for immediate stats
2. **Run the graphing script** when you want visual analysis
3. **Open the CSV file** for detailed data analysis
4. **Compare modes** to see which works best for you

## 📈 **4. Interpreting the Results**

### **Good Performance Indicators:**
- **Positive reward** (saved > killed)
- **High saved count** (successful rescues)
- **Low killed count** (few mistakes)
- **Low LLM call percentage** (efficient rule-based decisions)

### **Performance Benchmarks:**

| Performance Level | Reward Range | Saved | Killed | LLM Calls |
|-------------------|--------------|-------|--------|-----------|
| **Excellent** | +5 to +10 | 8-12 | 0-2 | <30% |
| **Good** | +2 to +4 | 5-7 | 1-3 | 30-50% |
| **Average** | 0 to +1 | 3-4 | 2-4 | 50-70% |
| **Poor** | -1 to -3 | 1-2 | 4-6 | >70% |

### **Mode Comparison:**
- **llm**: Multimodal LLM agent (best quality)

## 🔧 **5. Customizing the Tracking**

### **Disable Tracking:**
If you don't want graphs, you can comment out the tracking lines in `main.py`.

### **Change Graph Style:**
Modify the `generate_graphs()` method in `performance_tracker.py` to customize colors, sizes, or add new metrics.

### **Export Data:**
The JSON and CSV files can be imported into Excel, Python, or other analysis tools for further study.

## 💡 **6. Tips for Better Performance**

1. **Run multiple times** to get a good average
2. **Compare different modes** to find what works best
3. **Look for patterns** in the graphs - are you improving over time?
4. **Focus on the saved vs killed ratio** - this is the most important metric
5. **Use the LLM call percentage** to optimize for speed vs quality

The graphing system helps you understand not just how well the LLM is performing, but also how efficiently it's making decisions! 🎯 