
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str

# Database initialization
def init_db():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS extracted_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT,
                        text_content TEXT,
                        links TEXT,
                        images TEXT
                      )''')
    conn.commit()
    conn.close()

init_db()

# Serve the frontend from /
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")

@app.post("/extract")
async def extract_text(request: URLRequest):
    url = request.url
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching URL: {e}")

    soup = BeautifulSoup(response.text, "html.parser")
    for script in soup(["script", "style", "noscript"]):
        script.decompose()

    text = soup.get_text(separator="\n", strip=True)
    links = [a.get("href") for a in soup.find_all("a", href=True)]
    images = [img.get("src") for img in soup.find_all("img", src=True)]

    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO extracted_data (url, text_content, links, images) VALUES (?, ?, ?, ?)",
                   (url, text, str(links), str(images)))
    conn.commit()
    conn.close()

    return {"url": url, "text": text, "links": links, "images": images}
