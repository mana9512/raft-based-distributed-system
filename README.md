# 🚀 Raft Consensus Distributed System

This project is a simulation of the **Raft Consensus Algorithm** built using **Python (Flask)** for the backend and a **responsive HTML/JavaScript frontend UI** to visualize leader election and heartbeat propagation across distributed nodes.

---

## 📌 Features
- Leader election between Raft nodes
- Heartbeat messaging from leaders
- Node status monitoring via UI
- Visual indicators for leader, heartbeat activity, and unreachable nodes
- Start individual nodes independently

---

## 💡 Technologies Used
- Python (Flask)
- HTML/CSS/JavaScript (Vanilla)
- REST APIs
- Flask-CORS

---

## 📁 Directory Structure
```
raft-consensus-system/
├── raft_node.py                  # Python backend for each Raft node
├── static/
│   └── index.html               # Frontend UI
```

---

## UI
<img width="1440" alt="Screenshot 2025-03-23 at 10 35 24 AM" src="https://github.com/user-attachments/assets/8ff0dd2d-7e9d-4f8a-8d67-f5573d69f851" />


## 🔧 Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/raft-consensus-system.git
cd raft-consensus-system
```

### 2️⃣ Install Dependencies
```bash
pip install flask flask-cors requests
```

### 3️⃣ Run Individual Node
```bash
python raft_node.py 0  # Starts Node 0
python raft_node.py 1  # Starts Node 1
python raft_node.py 2  # Starts Node 2
```
> You can start one node at a time or multiple in separate terminals.

### 4️⃣ Open UI Dashboard
Open the `static/index.html` file in your browser:
```
Right click → Open with browser
```
> By default, UI triggers election/heartbeat from Node 0. If you are running only Node 2, modify the `index.html` JavaScript URLs accordingly.

---
