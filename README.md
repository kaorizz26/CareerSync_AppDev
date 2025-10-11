# Project Quick Start Guide

This guide assumes you are starting from your machine's general command line or terminal.

### 1. Clone and Navigate 🧭

Download the project files from GitHub and move into the correct directory where the setup files are located.

| Step | Command | Resulting Directory |
| :--- | :--- | :--- |
| **Clone** | `git clone https://github.com/kaorizz26/CareerSync_AppDev.git` | `CareerSync_AppDev/` |
| **Navigate** | `cd CareerSync_AppDev/prototype` | `CareerSync_AppDev/prototype/` |

---

### 2. Virtual Environment & Dependencies 🛠️

Ensure your virtual environment is active before installing dependencies.

| Step | Command | Purpose |
| :--- | :--- | :--- |
| **Activate venv (Windows)** | `.\venv\Scripts\Activate` | Activates the environment. *(For macOS/Linux, use `source venv/bin/activate`)* |
| **Install** | `pip install -r requirements.txt` | Installs all required project libraries. |

---

### 3. Run the Application 🚀

After setting your required **`GROQ_API_KEY` environment variable** (as instructed separately), you can launch the application.

| Step | Command | Result |
| :--- | :--- | :--- |
| **Execute** | `python app.py` | Starts the Flask web server. |
