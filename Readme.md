# 🚗 Self-Driving Car — Neural Network + Genetic Algorithm

A self-driving car simulation built from scratch in Python. A population of cars, each controlled by its own feed-forward neural network, learns to drive a track using nothing but distance sensors — trained entirely through an evolutionary algorithm (no external ML libraries, no pre-labeled data).

![Training in progress](screenshots/training-overview.png)
*Replace this with a screenshot of the training simulation in action.*

---

## 📌 Overview

This project implements a full pipeline for training and running AI-controlled cars on a 2D track:

- A **neural network built from scratch** (no PyTorch/TensorFlow) — custom forward pass, weight/bias storage, and serialization.
- A **genetic algorithm** with elitism, crossover breeding, and adaptive mutation to evolve better drivers generation over generation.
- A **checkpointing system** that persists training progress to disk, so training can be safely paused and resumed at any time — including mid-generation, via an in-app "Stop & Save" control.
- A **real-time pygame simulation** with ray-cast style distance sensors, lap detection, and live fitness tracking.
- A **standalone playback script** to watch the fully trained brain drive the track on its own.

---

## ✨ Features

- 🧠 Neural network implemented from first principles (weights, biases, `tanh` activation, forward propagation)
- 🧬 Genetic algorithm with:
  - Elitism (top performers carried forward unchanged)
  - Uniform crossover between elite "parents"
  - Adaptive mutation strength that automatically increases when training plateaus
- 📡 7-sensor array per car for real-time obstacle/track-edge detection
- 🏁 Lap detection with forward/reverse tracking and distance-based fitness scoring
- 💾 Full training-state checkpointing (generation, elites, mutation strength, stagnation counter) — training resumes exactly where it left off
- ⏹️ In-simulation **Stop & Save** button for graceful, on-demand checkpointing without losing in-progress generations
- 🎮 Separate playback mode to run and visualize the trained model independently of training

---

## 🖼️ Screenshots

| Training | Trained Car Driving |
|---|---|
| ![Training screenshot](screenshots/training.png) | ![Trained car screenshot](screenshots/trained-run.png) |

| Console Output | Stop & Save Button |
|---|---|
| ![Console output](screenshots/console-output.png) | ![Stop and save button](screenshots/stop-save-button.png) |

*(Drop your `.png`/`.jpg` screenshots into a `screenshots/` folder in the project root using the filenames above, or update the paths to match your own.)*

---

## 🧠 How It Works

### 1. Perception
Each car has 7 directional sensors that cast rays outward and measure distance to the nearest track edge, normalized to a `0–1` range. This is the only input the neural network receives.

### 2. Decision-Making
The sensor readings are fed into a feed-forward neural network with architecture `[7, 8, 2]`:

- **7 inputs** → sensor readings
- **8 hidden neurons** → `tanh` activation
- **2 outputs** → throttle and steering, both in `[-1, 1]`

### 3. Fitness
A car's fitness is the total distance it travels along the track centerline (accounting for laps), and it never decreases mid-run — only forward progress counts.

### 4. Evolution
After every generation:
1. All cars are ranked by distance traveled.
2. The top performers ("elites") are kept unchanged.
3. The rest of the next generation is produced by crossing over two randomly chosen elites and applying random mutation.
4. If no meaningful improvement happens for several generations in a row, mutation strength is automatically increased to help escape local optima — then reset once progress resumes.

### 5. Persistence
All of this state — generation number, elite brains, best distance achieved, stagnation counter, and current mutation strength — is saved to `training_checkpoint.json` after every generation (or on demand via the Stop & Save button), so training can be interrupted and resumed without losing progress.

---

## 🛠️ Tech Stack

- **Python 3**
- **Pygame** — simulation, rendering, and input handling
- **Custom neural network** — pure Python, no ML frameworks
- **JSON** — checkpoint serialization

---

## 📁 Project Structure

```
.
├── neural_network.py          # Neural network (Layer, Neural_Network classes)
├── simulation.py               # Core simulation loop, sensors, fitness, rendering
├── train.py                    # Training entry point / genetic algorithm driver
├── run_trained.py              # Loads a saved checkpoint and drives autonomously
├── car.py                      # Car physics/state
├── sensor.py                   # Distance sensor logic
├── tracks/
│   └── three.json               # Track definition (inner/outer boundary points)
├── training_checkpoint.json    # Auto-generated training state (created on first run)
└── screenshots/                 # Screenshots for this README
```

---

## 🚀 Getting Started

### Prerequisites

```bash
pip install pygame
```

### Train the model

```bash
python train.py
```

- Training runs continuously, generation after generation.
- Close the window (❌) to abort the current generation without saving it.
- Click **Stop & Save** (top-right of the window) to end the current generation early and save progress immediately.
- Re-running `python train.py` automatically resumes from `training_checkpoint.json` if one exists.

### Watch the trained car drive

```bash
python run_trained.py
```

Loads the best brain from `training_checkpoint.json` and drives the track autonomously with no further learning.

---

## ⚙️ Configuration

Key hyperparameters, found at the top of `train.py`:

| Setting | Description | Default |
|---|---|---|
| `POPULATION_SIZE` | Cars trained per generation | `10` |
| `ARCHITECTURE` | Neural network shape | `[7, 8, 2]` |
| `ELITE_COUNT` | Top performers kept each generation | `3` |
| `MUTATION_RATE` | Probability each weight/bias mutates | `0.10` |
| `BASE_MUTATION_STRENGTH` | Default mutation magnitude | `0.30` |
| `MAX_MUTATION_STRENGTH` | Ceiling for adaptive mutation | `1.20` |
| `STAGNATION_LIMIT` | Generations without improvement before boosting mutation | `4` |

To train on a different track, add a new `tracks/<name>.json` file and update `TRACK_NAME` in `simulation.py` and `run_trained.py`.

---

## 🗺️ Roadmap / Possible Improvements

- [ ] Multi-track training with per-track checkpoints
- [ ] Headless/fast training mode (no rendering) for faster iteration
- [ ] Configurable sensor count/angles via command-line flags
- [ ] Export standalone `best_brain.json` snapshots alongside the full checkpoint
- [ ] Web-based visualization dashboard for training metrics over time

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👤 Author

**Your Name**
[GitHub](https://github.com/your-username) · [LinkedIn](https://linkedin.com/in/your-profile) · [Portfolio](https://your-portfolio.com)

*Built as a hands-on exploration of neural networks and evolutionary algorithms implemented entirely from scratch, without relying on machine learning frameworks.*