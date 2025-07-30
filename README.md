# Game Assistant

A Flask-based application to optimize and visualize village production and transfer routes, toy project to practice with linear programming, app development (with Flask) and app deployment (with Docker).

---

## Features

- Optimize routes between villages using linear programming (PuLP)
- Visualize village network and transfers using D3.js
- Interactive graph with directional arrows showing resource flow

---

## Requirements

- Python 3.12+
- Docker (optional, for containerized deployment)
- See `requirements.txt` for Python dependencies

---

## Installation

### Using Python virtual environment

```bash
git clone https://github.com/gabrielbuffet/game_assistant.git
cd game_assistant
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

pip install -r requirements.txt
pip install -e .
python -m game_assistant/app.py --instance "your_instance.json"
```

### Run in  Docker

```bash
docker build -t game-assistant .
docker run -d -p 5000:5000 game-assistant
```
---