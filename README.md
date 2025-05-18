# **FocusLoop** – Real-time EEG × Eye-Tracking Neurofeedback to Help You Focus

![GitHub release](https://img.shields.io/github/v/release/Drivthrucover/focusloop.svg)
![GitHub downloads](https://img.shields.io/github/downloads/Drivthrucover/focusloop/total.svg)
![License](https://img.shields.io/github/license/Drivthrucover/focusloop)

**FocusLoop** is a closed-loop attention-training platform that uses low-cost **EEG** (Muse 2) and **eye-tracking** (GazeCloudAPI).  
A Unity mini-game reacts to your brain state: brightening the screen when focus drops and spawning distractors, light a blaring red light, when gaze shifts and focus is gone.  
Most neurofeedback models rely on a *single* signal (EEG *or* gaze/eye movement), but FocusLoop pairs both streams to **halve calibration time** and **boost engagement**.

---

## Key Features ☁️

| Feature | What it does |
|---------|--------------|
| **EEG Focus Index** | β / (θ + α) computed every 250 ms from 1 s sliding windows. |
| **Gaze Dispersion Score** | Real-time BCEA (visual steadiness) normalised 0 – 1. |
| **Sensor Fusion** | Combines EEG & gaze into a single *attention state* sent to Unity @ 10 Hz. |
| **Adaptive Feedback** | Unity OSC listener changes lighting, spawns distractions, or triggers TENS pulses. |
| **Demo / Playback Mode** | Run the game with pre-recorded data—perfect for demos or offline testing. |
| **Modular Python + Unity** | Swap hardware (Muse ↔ Emotiv) or run the *all-in-Unity* C# pipeline. |

---

## Hardware & Software Stack 🛠️

| Layer | Tech / Package |
|-------|----------------|
| EEG acquisition | Muse 2 / Emotiv Insight → **BrainFlow** → **LabStreamingLayer** |
| Eye tracking | **Tobii 5L** SDK (120 Hz) |
| Signal processing | **Python 3.11**, **MNE-Python**, **NumPy/PyFFTW** |
| Message bus | **ZeroMQ** (JSON) |
| Game engine | **Unity 2022 LTS** + **UnityOSC** |
| Optional haptics | Arduino / BLE microcontroller driving TENS (< 10 mA) |

> **Minimum dev machine:** macOS/Win/Linux, Python 3.11, Unity 2022 LTS, Muse BLE dongle or Emotiv USB.  
> **Optional:** Oculus Rift S for fully immersive tasks.

---

## Installation 🚀

### 1. Clone & set up Python backend

```bash
git clone --recursive https://github.com/Drivthrucover/focusloop.git
cd focusloop
conda env create -f env.yml          # installs mne, brainflow, pylsl, pyzmq …
conda activate focusloop
