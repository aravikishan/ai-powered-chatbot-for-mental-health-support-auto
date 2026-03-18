
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
from datetime import datetime
import sqlite3

# Initialize FastAPI app
app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Database setup
DATABASE = 'database.db'

# Data models
class UserProfile(BaseModel):
    user_id: int
    name: str
    email: str
    preferences: str

class ChatMessage(BaseModel):
    message_id: int
    user_id: int
    content: str
    timestamp: datetime

class Resource(BaseModel):
    resource_id: int
    title: str
    description: str
    link: str

# Create tables and seed data
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_profile (
                        user_id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL,
                        preferences TEXT
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS chat_message (
                        message_id INTEGER PRIMARY KEY,
                        user_id INTEGER,
                        content TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES user_profile(user_id)
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS resource (
                        resource_id INTEGER PRIMARY KEY,
                        title TEXT NOT NULL,
                        description TEXT,
                        link TEXT
                    )''')
    # Seed data
    cursor.execute("INSERT OR IGNORE INTO user_profile (user_id, name, email, preferences) VALUES (1, 'John Doe', 'john@example.com', 'anxiety')")
    cursor.execute("INSERT OR IGNORE INTO resource (resource_id, title, description, link) VALUES (1, 'Mental Health America', 'Resources for mental health support', 'https://www.mhanational.org/')")
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chat(request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def profile(request):
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/resources", response_class=HTMLResponse)
async def resources(request):
    return templates.TemplateResponse("resources.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/api/chat", response_model=List[ChatMessage])
async def get_chat_messages():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT message_id, user_id, content, timestamp FROM chat_message")
    rows = cursor.fetchall()
    conn.close()
    return [ChatMessage(message_id=row[0], user_id=row[1], content=row[2], timestamp=row[3]) for row in rows]

@app.post("/api/users", response_model=UserProfile)
async def create_or_update_user(user: UserProfile):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO user_profile (user_id, name, email, preferences) VALUES (?, ?, ?, ?)",
                   (user.user_id, user.name, user.email, user.preferences))
    conn.commit()
    conn.close()
    return user

@app.get("/api/resources", response_model=List[Resource])
async def get_resources():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT resource_id, title, description, link FROM resource")
    rows = cursor.fetchall()
    conn.close()
    return [Resource(resource_id=row[0], title=row[1], description=row[2], link=row[3]) for row in rows]

@app.get("/api/user/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, email, preferences FROM user_profile WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return UserProfile(user_id=row[0], name=row[1], email=row[2], preferences=row[3])
    raise HTTPException(status_code=404, detail="User not found")
