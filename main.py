import os
import json
import random
import urllib.request
import asyncio
import google.generativeai as genai
import edge_tts
from moviepy.editor import VideoFileClip, AudioFileClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# 1. SETUP API KEYS & CREDENTIALS FROM GITHUB SECRETS
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
YOUTUBE_TOKEN_DATA = os.getenv("YOUTUBE_TOKEN")
YOUTUBE_SECRET_DATA = os.getenv("YOUTUBE_CLIENT_SECRET")

# Fallback to local files if running manually in Termux
if not YOUTUBE_TOKEN_DATA and os.path.exists("token.json"):
    with open("token.json", "r") as f: YOUTUBE_TOKEN_DATA = f.read()
if not YOUTUBE_SECRET_DATA and os.path.exists("client_secret.json"):
    with open("client_secret.json", "r") as f: YOUTUBE_SECRET_DATA = f.read()

# 2. GENERATE SCRIPT WITH GEMINI AI
def generate_ai_script():
    print("[+] Generating viral script with Gemini...")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = """
    Write a highly engaging 40-second script for a YouTube Short about Stoic Philosophy or dark psychological facts. 
    It must be structured like the channel 10X INCOME. 
    Start with a massive hook, keep sentences short and punchy, and end with a call to action. 
    Return ONLY the voiceover text. Do not include sound effects or visual notes.
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# 3. GENERATE CINEMATIC AI VOICE
async def generate_voice(text, output_audio):
    print("[+] Generating cinematic AI voice...")
    # Using a high-quality deep male voice (Christopher)
    communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural")
    await communicate.save(output_audio)

# 4. DOWNLOAD RANDOM BACKGROUND VIDEO
def download_background():
    print("[+] Downloading background footage...")
    # Direct links to clean vertical abstract/nature loop clips
    video_urls = [
        "https://assets.mixkit.co/videos/preview/mixkit-abstract-laser-lights-background-loop-41852-large.mp4",
        "https://assets.mixkit.co/videos/preview/mixkit-digital-animation-of-screens-and-numbers-41864-large.mp4",
        "https://assets.mixkit.co/videos/preview/mixkit-stars-in-space-background-1611-large.mp4"
    ]
    url = random.choice(video_urls)
    urllib.request.urlretrieve(url, "background.mp4")

# 5. EDIT AND STITCH VIDEO
def create_final_video():
    print("[+] Stitching audio and video together...")
    video_clip = VideoFileClip("background.mp4")
    audio_clip = AudioFileClip("voice.mp3")
    
    # Trim background video to match audio length
    final_clip = video_clip.set_audio(audio_clip).set_duration(audio_clip.duration)
    
    # Ensure standard vertical shorts format (1080x1920)
    final_clip = final_clip.resize(newsize=(1080, 1920))
    final_clip.write_videofile("output.mp4", fps=24, codec="libx264", audio_codec="aac")

# 6. UPLOAD TO YOUTUBE
def upload_to_youtube():
    print("[+] Uploading final video to YouTube...")
    token_info = json.loads(YOUTUBE_TOKEN_DATA)
    client_info = json.loads(YOUTUBE_SECRET_DATA)["installed"]
    
    creds = Credentials(
        token=token_info["access_token"],
        refresh_token=token_info.get("refresh_token"),
        token_uri=token_info.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=client_info["client_id"],
        client_secret=client_info["client_secret"]
    )
    
    youtube = build("youtube", "v3", credentials=creds)
    
    body = {
        "snippet": {
            "title": "This Realization Will Change You... #shorts #motivation #philosophy",
            "description": "Automated motivational content. Sub for daily value.",
            "tags": ["shorts", "motivation", "stoic"],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }
    
    media = MediaFileUpload("output.mp4", chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[+] Upload progress: {int(status.progress() * 100)}%")
            
    print(f"[+++] Success! Video uploaded successfully. Video ID: {response['id']}")

# MAIN PIPELINE EXECUTION
if __name__ == "__main__":
    try:
        script_text = generate_ai_script()
        asyncio.run(generate_voice(script_text, "voice.mp3"))
        download_background()
        create_final_video()
        upload_to_youtube()
    except Exception as e:
        print(f"[-] Automation critical error: {e}")

