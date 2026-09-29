# 🌳 Optimal BST Visualizer

An interactive desktop app that builds an **Optimal Binary Search Tree (OBST)** using **Dynamic Programming**, then compares it against a standard balanced BST, with a colour-coded DP matrix and a step-by-step algorithm trace.

Built with **Python + Tkinter** (no third-party dependencies) as a mini-project for *21CSC204J – Design & Analysis of Algorithms*, SRM Institute of Science and Technology, Ramapuram Campus.

![Tree comparison](docs/screenshots/tree-comparison.png)

## ✨ Features

- **Tree comparison**: OBST and balanced BST drawn side by side, each with its average search cost (the lower one is marked ★).
- **DP matrix heatmap**: the `e[i][j]` cost table with the optimal root per cell. Click any cell to highlight that subtree on the OBST canvas.
- **Step-by-step trace**: walk through every subproblem with Prev / Next / Auto Play, and see every candidate root tested and the winner marked.
- **Flexible input**: add or delete key/frequency rows, and use **Sanitize** to validate, de-duplicate and sort keys.

| DP Matrix | Algorithm Trace |
|---|---|
| ![DP matrix](docs/screenshots/dp-matrix.png) | ![Algorithm trace](docs/screenshots/algorithm-trace.png) |

## 🧠 How it works

A normal BST's shape depends on insertion order. An OBST uses how often each key is searched and places frequent keys nearer the root to minimise the expected search cost.

For keys `1..n` with frequencies `freq[k]`:

```
w[i][j] = w[i][j-1] + freq[j]
e[i][j] = min over r in [i..j] of ( e[i][r-1] + e[r+1][j] + w[i][j] )
root[i][j] = the r that gives the minimum
```

- `e[i][j]`: minimum cost for keys `i..j`
- `w[i][j]`: sum of frequencies for keys `i..j`
- `root[i][j]`: optimal root, used to rebuild the tree recursively

**Complexity:** O(n³) time, O(n²) space.

**Example** (keys `10, 20, 30, 40, 50, 56` with frequencies `3, 3, 1, 1, 7, 8`):

| Tree | Avg. search cost |
|---|---|
| Optimal BST | **1.9565** |
| Balanced BST | 2.4783 |

## 🚀 Getting started

**Requirements:** Python 3.7+ with Tkinter (bundled with the standard Python installers for Windows and macOS).

On Debian/Ubuntu, install Tkinter first:

```bash
sudo apt install python3-tk
```

```bash
git clone https://github.com/Mithun0017/Optimal-BST-Visualizer.git
cd Optimal-BST-Visualizer
python obst_visualizer.py
```

## 🕹️ Usage

1. Enter keys (numbers) and their frequencies in the left panel. Use **+ Add Row** for more.
2. Click **✓ Sanitize** to sort keys and remove duplicates. *Do this before running if your keys are not already in ascending order.*
3. Click **▶ Run OBST**.
4. Explore the **Tree Comparison**, **DP Matrix** and **Algorithm Trace** tabs.


Inside `obst_visualizer.py`:

| Function / Class | Purpose |
|---|---|
| `obst_dp()` | Builds the `e`, `w` and `root` tables |
| `build_tree()` | Reconstructs the OBST from the root table |
| `build_balanced_bst()` | Builds the comparison tree |
| `avg_search_cost()` | Expected search cost of any tree |
| `OBSTApp` | Tkinter UI: input panel, tree canvases, DP grid, trace player |

## ⚠️ Known limitations

- Keys must be numeric, and there is no database or file input (in-memory only).
- Keys must be sorted and unique, so use **Sanitize** first.
- The Frequency/Probability toggle is currently cosmetic. Costs are normalised by the total, so both modes give the same result.
- Only successful searches are modelled (no dummy-key/failure probabilities as in CLRS).

## 👥 Authors

- **Mithun** ([@Mithun0017](https://github.com/Mithun0017))

