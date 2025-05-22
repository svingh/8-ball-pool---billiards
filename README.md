## 🛠️ Technologies Used

- **C** – for fast simulation code  
- **SWIG** – to interface C code with Python  
- **Python** – powers the web server and connects to the database  
- **CSS & JavaScript** – used for the frontend  

---

## 🎮 Features

- 2-player game system  
- Handles all major edge cases in pool (e.g. potting the black ball early, scratches, etc.)  
- Endless replayability  
- Surprisingly smooth animations on Chrome (given how it was made 😄)

---

## 🚀 How to Run the Project

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <project-directory>
   ```

2. **Create and activate a Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install the legacy CGI module**  
   Python 3.13+ removed the built-in `cgi` module, so install a replacement:
   ```bash
   pip install legacy-cgi
   ```

4. **Run the server**
   ```bash
   python server.py 8000
   ```

5. **Open the game in your browser**  
   Navigate to:
   ```
   http://localhost:8000/web/part3/index.html
   ```
