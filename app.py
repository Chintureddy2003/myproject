from flask import Flask, request, redirect, render_template
import sqlite3
import re
import requests

app = Flask(__name__)

# Replace this with your YouTube API key
YOUTUBE_API_KEY = "AIzaSyBguXLgPDYRgBzAAkBLxLK877TwqcvBzfA"

# Database setup
def init_db():
    conn = sqlite3.connect('channels.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS channels
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       name TEXT NOT NULL, 
                       channel_id TEXT NOT NULL, 
                       content_type TEXT NOT NULL,
                       subscriber_count INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

# Extract Channel ID from YouTube URL or handle
def get_channel_id(channel_url_or_handle):
    # If the input contains @ (handle), process it
    if '@' in channel_url_or_handle:
        url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forHandle={channel_url_or_handle}&key={YOUTUBE_API_KEY}"
    else:
        # For URLs, we assume user provides the full URL (validate)
        channel_id_match = re.search(r"(?:channel/|user/|c/|/)([a-zA-Z0-9_-]{24})", channel_url_or_handle)
        if channel_id_match:
            return channel_id_match.group(1)
        else:
            return None
    
    response = requests.get(url).json()
    return response.get('items', [{}])[0].get('id', None)

# Fetch all channels
def fetch_channels():
    conn = sqlite3.connect('channels.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, channel_id, content_type FROM channels")
    channels = cursor.fetchall()
    conn.close()
    return channels

# Add channel to database
@app.route("/add", methods=["POST"])
def add_channel():
    name = request.form['name']
    link = request.form['link']
    content_type = request.form['content_type']
    
    channel_id = get_channel_id(link)
    if not channel_id:
        return "Invalid YouTube channel link or handle!", 400
    
    # Add to database
    conn = sqlite3.connect('channels.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO channels (name, channel_id, content_type) VALUES (?, ?, ?)",
                   (name, channel_id, content_type))
    conn.commit()
    conn.close()
    return redirect("/")

# Home route to display channels
@app.route("/")
def index():
    channels = fetch_channels()
    return render_template("index.html", channels=channels)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
