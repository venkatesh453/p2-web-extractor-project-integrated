
import subprocess
import webbrowser
import threading
import time

def run_uvicorn():
    subprocess.call(["uvicorn", "main:app", "--reload"])

threading.Thread(target=run_uvicorn).start()
time.sleep(3)
webbrowser.open("http://127.0.0.1:8000")
