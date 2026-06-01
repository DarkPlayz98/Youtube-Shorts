import os
import json
import random
import urllib.request
import asyncio
import edge_tts
from moviepy.editor import VideoFileClip, AudioFileClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# 1. SETUP API KEYS & CREDENTIALS
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
YOUTUBE_TOKEN_DATA = os.getenv("YOUTUBE_TOKEN")
YOUTUBE_SECRET_DATA = os.getenv("YOUTUBE_CLIENT_SECRET")

if not YOUTUBE_TOKEN_DATA and os.path.exists("token.json"):
    with open("token.json", "r") as f: YOUTUBE_TOKEN_DATA = f.read()
if not YOUTUBE_SECRET_DATA and os.path.exists("client_secret.json"):
    with open("client_secret.json", "r") as f: YOUTUBE_SECRET_DATA = f.read()

# 2. GENERATE SCRIPT WITH GEMINI
def generate_ai_script():
    try:
        print("[+] Generating viral script directly with Gemini API...")
        # Using 1.5-flash as it is the most stable endpoint for direct API calls
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [{
                    "text": "Write a highly engaging 40-second script for a YouTube Short about Stoic Philosophy or dark psychological facts. It must be structured like the channel 10X INCOME. Start with a massive hook, keep sentences short and punchy, and end with a call to action. Return ONLY the voiceover text. Do not include sound effects or visual notes."
                }]
            }]
        }
        
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode("utf-8"), 
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        raise Exception(f"Gemini API Error: {e}")

# 3. GENERATE CINEMATIC AI VOICE
async def generate_voice(text, output_audio):
    try:
        print("[+] Generating cinematic AI voice...")
        communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural")
        await communicate.save(output_audio)
    except Exception as e:
        raise Exception(f"Voice Generation Error: {e}")

# 4. DOWNLOAD BACKGROUND VIDEO (DISGUISED AS GOOGLE CHROME)
def download_background():
    try:
        print("[+] Downloading background footage...")
        video_urls = [
            "https://assets.mixkit.co/videos/preview/mixkit-abstract-laser-lights-background-loop-41852-large.mp4",
            "https://assets.mixkit.co/videos/preview/mixkit-digital-animation-of-screens-and-numbers-41864-large.mp4",
            "https://assets.mixkit.co/videos/preview/mixkit-stars-in-space-background-1611-large.mp4"
        ]
        url = random.choice(video_urls)
        
        # Disguise the request so Mixkit doesn't block GitHub's servers
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req) as response, open("background.mp4", 'wb') as out_file:
            out_file.write(response.read())
    except Exception as e:
        raise Exception(f"Video Download Error: {e}")

# 5. EDIT AND STITCH VIDEO
def create_final_video():
    try:
        print("[+] Stitching audio and video together...")
        video_clip = VideoFileClip("background.mp4")
        audio_clip = AudioFileClip("voice.mp3")
        
        final_clip = video_clip.set_audio(audio_clip).set_duration(audio_clip.duration)
        final_clip = final_clip.resize(newsize=(1080, 1920))
        final_clip.write_videofile("output.mp4", fps=24, codec="libx264", audio_codec="aac")
    except Exception as e:
        raise Exception(f"Video Stitching Error: {e}")

# 6. UPLOAD TO YOUTUBE
def upload_to_youtube():
    try:
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
    except Exception as e:
        raise Exception(f"YouTube Upload Error: {e}")

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

