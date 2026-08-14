<div align="center">

# ✍️ AirWrite TV Search

### *Hands-Free Air-Writing & Cinematic Movie Discovery Powered by Computer Vision & Vision Transformers*

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand--Tracking-00599C.svg?logo=google&logoColor=white)](https://google.github.io/mediapipe/)
[![TrOCR](https://img.shields.io/badge/Microsoft-TrOCR--Small--Handwritten-EE4C2C.svg?logo=pytorch&logoColor=white)](https://huggingface.co/microsoft/trocr-small-handwritten)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg?logo=react&logoColor=white)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev/)

</div>

---

## 🌟 Overview

**AirWrite TV Search** is a state-of-the-art computer vision application that enables users to **write movie or TV show titles in mid-air** using natural hand gestures. 

By combining 3D palm-plane geometry for gesture classification, MediaPipe hand tracking, smooth trajectory rendering, and Microsoft's pre-trained **TrOCR (Transformer OCR)** model, AirWrite turns air handwriting into actionable TV and movie searches in real-time.

```text
 ☝️ Air Write      🖐️ Pen Up      ✌️ Confirm          🤖 TrOCR           📺 Movie Search
┌───────────┐   ┌───────────┐   ┌───────────┐     ┌───────────┐     ┌────────────────┐
│ Track     │──>│ Pause     │──>│ Freeze    │────>│ Vision    │────>│ TV & Movie     │
│ Fingertip │   │ Stroke    │   │ Canvas    │     │ Transformer│    │ Poster Results │
└───────────┘   └───────────┘   └───────────┘     └───────────┘     └────────────────┘
```

---

## ✨ Features

- ☝️ **Continuous Fingertip Air Writing (`WRITE`)**: Tracks your index fingertip in real-time ($1280 \times 720$ canvas resolution) with sub-pixel trajectory smoothing.
- 🖐️ **Natural Stroke Separation (`PEN_UP`)**: Show an open palm to pause stroke recording without erasing existing writing—allowing seamless multi-stroke character and word creation.
- ✌️ **Vision Transformer Recognition (`CONFIRM`)**: Extend index and middle fingers (peace sign) to freeze handwriting and pass auto-cropped handwriting regions to **Microsoft TrOCR** (`microsoft/trocr-small-handwritten`) with multi-variant image preprocessing & beam search.
- ✊ **Canvas Reset (`CLEAR`)**: Make a fist (or click the Clear button) to reset the virtual handwriting canvas and session state.
- 🖼️ **Persistent Canvas & Result Preview**: Retains the captured handwriting image preview, glowing stroke paths, and recognized search queries without vanishing on gesture transitions.
- 📺 **Live Backend Stream (`MJPEG`)**: Streams real-time OpenCV desktop feeds directly into the browser with MediaPipe hand skeletons, wrist status badges, and glowing fingertip tracking points.
- 🔍 **Automated & Manual Search**: Recognized text automatically populates the search bar and queries public media APIs (TVMaze) for real movie poster cards with ratings, release years, genres, and streaming badges.
- 📜 **LocalStorage Search History**: Retains past confirmed search queries with timestamps and confidence scores.
- 🎨 **Cinematic Dark UI**: Premium glassmorphic interface built with React, Vite, and Lucide icons.

---

## 🖐️ Gesture Control Reference

| Gesture | Hand Pose | Description | Action |
| :---: | :---: | :--- | :--- |
| **`WRITE`** | ☝️ Index Finger Extended | Tracks index fingertip $(x, y)$ coordinates continuously | Draws live glowing strokes on screen & trajectory canvas |
| **`PEN_UP`** | 🖐️ Open Palm | 3 or 4 fingers extended | Pauses stroke recording; keeps current strokes visible |
| **`CONFIRM`** | ✌️ Two Fingers Extended | Index & middle fingers extended (Peace Sign) | Freezes canvas, auto-crops region, and runs TrOCR |
| **`CLEAR`** | ✊ Closed Fist | All main fingers folded | Resets virtual handwriting canvas and session state |

---

## 🏗️ System Architecture

```text
React Frontend (http://localhost:5173)
 ├── Centralized API Config (src/config.ts)
 ├── [ START CAMERA ]  ──> POST /api/camera/start  ──> Launches OpenCV stream & CV loop
 ├── [ STOP CAMERA ]   ──> POST /api/camera/stop   ──> Releases camera & stops loop
 ├── Live Video Feed   <── GET /api/camera/stream  <── Streams MJPEG camera frames
 ├── Live Gestures     <── WS /ws                  <── Broadcasts WRITE/PEN_UP/CONFIRM/CLEAR
 ├── TrOCR Result      <── WS /ws                  <── RECOGNIZED word & confidence
 └── Search Query      ──> GET /api/search?q=...   ──> Queries REST API for movie cards
```

---

## 📂 Project Structure

```
air-writer/
├── backend/
│   ├── app/
│   │   ├── camera/
│   │   │   └── stream.py          # OpenCV DirectShow video capture wrapper
│   │   ├── config/
│   │   │   └── settings.py        # Centralized settings & hyper-parameters
│   │   ├── gestures/
│   │   │   ├── classifier.py      # 3D Palm-aware Euclidean distance finger classifier
│   │   │   └── stabilizer.py      # Sliding-window gesture voter (N=5)
│   │   ├── hand_tracking/
│   │   │   └── detector.py        # MediaPipe Hands pipeline wrapper
│   │   ├── recognition/
│   │   │   ├── canvas.py          # 1280x720 Virtual handwriting canvas & auto-crop
│   │   │   └── trocr_engine.py    # Microsoft TrOCR Small Handwritten & multi-variant decoder
│   │   ├── services/
│   │   │   └── movie_search.py    # TVMaze public API client & card formatter
│   │   ├── trajectory/
│   │   │   └── engine.py          # Multi-stroke word session manager
│   │   └── main.py                # FastAPI app (REST endpoints, MJPEG stream, WebSocket /ws)
│   ├── run.py                     # Standalone OpenCV Desktop Studio runner
│   ├── test_gestures.py           # Gesture classifier unit test suite
│   ├── test_trajectory.py         # Trajectory tracking unit test suite
│   ├── test_word_engine.py        # Word engine session unit test suite
│   └── test_trocr_v51.py          # TrOCR recognition unit test suite
├── src/
│   ├── components/
│   │   ├── AirWritingCanvas.tsx   # SVG multi-stroke trajectory renderer
│   │   ├── CameraControlPanel.tsx # Camera controls & status badge
│   │   ├── CameraPanel.tsx        # MJPEG video stream preview component
│   │   ├── ControlButtons.tsx     # Clear, Backspace, and Search buttons
│   │   ├── GestureGuide.tsx       # Visual gesture reference card
│   │   ├── Header.tsx             # Main header with tab navigation
│   │   ├── HistoryPanel.tsx       # LocalStorage search history view
│   │   ├── HowItWorks.tsx         # Interactive step-by-step user guide
│   │   ├── ModeSelector.tsx       # Mode selector toggle buttons
│   │   ├── MovieCard.tsx          # Movie poster card component
│   │   ├── RecognitionPanel.tsx   # TrOCR result, confidence & cropped preview
│   │   ├── SearchBar.tsx          # Search input field & Enter key listener
│   │   ├── SearchResults.tsx      # Movie card grid & loading skeletons
│   │   └── StatusIndicator.tsx    # Live WebSocket connection status badge
│   ├── config.ts                  # Centralized API configuration
│   ├── App.tsx                    # Main state machine, WebSocket hook & routing
│   ├── main.tsx                   # React entry point
│   ├── types.ts                   # TypeScript interfaces & type definitions
│   └── index.css                  # Modern dark glassmorphic stylesheet
├── package.json                   # React frontend dependencies & Vite scripts
└── vite.config.ts                 # Vite bundler configuration
```

---

## ⚡ Prerequisites

Ensure you have the following installed on your machine:

- **Python**: `3.9` or higher
- **Node.js**: `18.0.0` or higher
- **npm**: `9.0.0` or higher
- **Webcam**: Standard USB or built-in laptop camera

---

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/adityavinay1002/air-text-writer.git
cd air-writer
```

### 2. Backend Environment Setup (Python)

Create a Python virtual environment and install the required dependencies:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Install Python requirements
pip install -r backend/requirements.txt
```

> **Required Python Packages**: `opencv-python`, `mediapipe`, `torch`, `transformers`, `fastapi`, `uvicorn`, `pillow`, `numpy`.

### 3. Frontend Environment Setup (React / Node.js)

Install npm packages in the project root directory:

```bash
npm install
```

---

## 🚀 Running the Application

### Method A: Full Integrated Web Application (Recommended)

To run the complete web application with the FastAPI backend and React frontend:

#### Terminal 1: Run Python FastAPI Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
> *The backend will start on `http://localhost:8000` and pre-load the Microsoft TrOCR model asynchronously.*

#### Terminal 2: Run React Frontend Dev Server

```bash
# In the project root directory
npm run dev
```
> *Open **`http://localhost:5173`** in your web browser.*

---

### Method B: Standalone Desktop OpenCV Studio (Python Only)

If you wish to test the computer vision, gesture tracking, and TrOCR engine directly as a native OpenCV window:

```bash
python backend/run.py
```

- Press **`q`** or **`ESC`** to exit the OpenCV window.
- Press **`c`** to clear the virtual handwriting canvas.

---

## 🧪 Running Unit Tests

Run the Python backend test suites to verify system components independently:

```bash
# Test Gesture Classifier & 3D Palm Plane Geometry
python backend/test_gestures.py

# Test Trajectory Tracker & Multi-Stroke Session
python backend/test_trajectory.py

# Test Word Engine Workflow
python backend/test_word_engine.py

# Test Microsoft TrOCR Vision-Transformer Engine
python backend/test_trocr_v51.py
```

---

## 📡 API Reference

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| **`/health`** | `GET` | Health check endpoint returning backend connection & camera status |
| **`/api/camera/start`** | `POST` | Safely opens the OpenCV webcam capture device & launches CV loop |
| **`/api/camera/stop`** | `POST` | Releases the webcam capture device cleanly without server restart |
| **`/api/camera/stream`** | `GET` | Live MJPEG multipart video feed of the annotated OpenCV camera preview |
| **`/api/session/clear`** | `POST` | Clears the active virtual handwriting canvas and session trajectory |
| **`/api/search?q=<query>`** | `GET` | Queries TVMaze API for real movie cards matching the search term |
| **`/ws`** | `WebSocket` | Real-time WebSocket connection broadcasting gestures, strokes, & TrOCR results |

---

## ❓ Troubleshooting

<details>
<summary><b>1. Camera fails to open on Windows</b></summary>

Windows cameras often require the `cv2.CAP_DSHOW` backend. Ensure your webcam isn't currently being used by Zoom, Teams, or another application. You can test camera detection by running:
```bash
python backend/run.py
```
</details>

<details>
<summary><b>2. TrOCR model download time</b></summary>

On first launch, Hugging Face `transformers` will automatically download `microsoft/trocr-small-handwritten` (~250 MB). Ensure you have an active internet connection on startup.
</details>

<details>
<summary><b>3. React frontend displays "Backend Offline"</b></summary>

Ensure the FastAPI server is running on port `8000` (`uvicorn app.main:app --port 8000`). You can verify by visiting `http://localhost:8000/health` in your browser.
</details>

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

<div align="center">

Made with ❤️ by the AirWrite Team

</div>
