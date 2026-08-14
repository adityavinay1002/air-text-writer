# AirWrite TV Search - Computer Vision Backend (Phase 1)

Clean, modular Python computer-vision foundation for **AirWrite TV Search**, powered by **OpenCV** and **MediaPipe Hands**.

---

## 🎯 Features (Phase 1)

1. **Webcam Capture**: Real-time OpenCV high-FPS video input.
2. **Dual-Hand MediaPipe Tracking**: Independent tracking of up to 2 hands simultaneously (`max_num_hands=2`).
3. **Palm-Aware Gesture Classification**: 3D geometric palm-relative finger extension analysis (tilt and rotation invariant).
4. **Mutually Exclusive Gestures**:
   - ☝️ **`WRITE`**: Index finger extended **ONLY**. (Displays glowing fingertip tracking point).
   - 🖐️ **`PEN_UP`**: Open palm / 3-4 fingers extended. (Pauses stroke recording; retains strokes).
   - ✌️ **`CONFIRM`**: Index + Middle fingers extended **ONLY**. (Freezes canvas & runs TrOCR).
   - ✊ **`CLEAR`**: Fist / all main fingers folded. (Resets active canvas).
   - ❓ **`NEUTRAL`**: Unassigned hand posture.
5. **Anti-Flicker Stabilizer**: Temporal sliding-window majority voting ($N=5$) for smooth, jitter-free state transitions.
6. **Isolated 2-Hand Control**: A ✌️ `CONFIRM` gesture on the confirmation hand never interferes with or triggers `WRITE`/`PEN_UP` on the writing hand.

---

## 🚀 Quickstart & Running

### 1. Set Up Virtual Environment

```bash
cd backend
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Windows Command Prompt:
.\venv\Scripts\activate.bat
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Phase 1 Live Studio Test

```bash
python run.py
```

Press `q` or `ESC` in the OpenCV window to exit cleanly.
