import os
import asyncio
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from pydub import AudioSegment

import firebase_admin
from firebase_admin import credentials, firestore, storage

app = FastAPI(title="Kavyanjali Edge Audio Engine")

@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")

# --- Firebase Initialization ---
cred = credentials.Certificate("serviceAccountKey.json")
try:
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'kavyanjali-6f2b3.firebasestorage.app'
    })
except ValueError:
    pass

db = firestore.client()
bucket = storage.bucket()

# --- Voice Mapping for Edge-TTS ---
EDGE_VOICES = {
    "HI_FEMALE": "hi-IN-MadhuramNeural",
    "HI_MALE": "hi-IN-DivyayanNeural",
    "EN_FEMALE": "en-IN-NeerjaNeural",
    "EN_MALE": "en-IN-PrabhatNeural"
}

# 🚀 Safe CLI Subprocess Execution (Using the existing running loop)
async def run_edge_tts(text: str, voice: str, output_path: str):
    process = await asyncio.create_subprocess_exec(
        "edge-tts",
        "--voice", voice,
        "--text", text,
        "--write-media", output_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        error_msg = stderr.decode().strip()
        raise Exception(f"Edge-TTS CLI Error: {error_msg}")

# 🛠️ Is function ko 'async def' bana diya taaki loop conflict na ho
async def process_edge_audio_pipeline(poem_id: str, text: str, gender: str, lang: str):
    temp_voice = f"{poem_id}_edge_voice.mp3"
    final_audio_mp3 = f"{poem_id}_final.mp3"
    
    try:
        lang_upper = lang.upper().strip()
        gender_upper = gender.upper().strip()
        
        voice_key = f"{lang_upper}_{gender_upper}"
        selected_voice = EDGE_VOICES.get(voice_key, "hi-IN-MadhuramNeural")
        
        print(f">>> [Edge-Audio-Engine] Voice Locked: '{selected_voice}' for Poem ID: {poem_id}")
        
        # Text cleaning and formatting
        clean_text = text.replace("||", " ").replace("|", " ")
        
        # 🎙️ Yahan direct 'await' kar rahe hain, bina asyncio.run() ke jhanjhat ke!
        await run_edge_tts(clean_text, selected_voice, temp_voice)
        
        if not os.path.exists(temp_voice) or os.path.getsize(temp_voice) == 0:
            raise Exception("Edge-TTS voice generation failed or file is empty.")
            
        # --- BACKGROUND MUSIC MIXING (Pydub) ---
        voice_audio = AudioSegment.from_file(temp_voice)
        voice_duration_ms = len(voice_audio)
        
        if os.path.exists("bg_lofi.wav"):
            bg_music = AudioSegment.from_file("bg_lofi.wav") - 22
        else:
            bg_music = AudioSegment.silent(duration=voice_duration_ms)
            
        if len(bg_music) < voice_duration_ms:
            loops_needed = (voice_duration_ms // len(bg_music)) + 1
            bg_music = bg_music * loops_needed
            
        mixed_audio = bg_music.overlay(voice_audio, position=0)
        mixed_audio = mixed_audio[:voice_duration_ms + 400]
        
        mixed_audio.export(final_audio_mp3, format="mp3", bitrate="192k")
        
        # --- FIREBASE SYNCHRONIZATION ---
        audio_blob = bucket.blob(f"poem_audios/{poem_id}.mp3")
        audio_blob.upload_from_filename(final_audio_mp3)
        audio_blob.make_public()
        
        db.collection("poems").document(poem_id).update({
            "audioGenerationStatus": "completed",
            "audioUrl": audio_blob.public_url
        })
        print(f"🎉 Edge Audio Mixed & Uploaded successfully for ID: {poem_id}")
        
    except Exception as e:
        print(f"🔥 EDGE PIPELINE EXCEPTION: {str(e)}")
        db.collection("poems").document(poem_id).update({
            "audioGenerationStatus": "failed"
        })
        raise e
    finally:
        # Local cleanup safely
        for f in [temp_voice, final_audio_mp3]:
            if os.path.exists(f):
                 os.remove(f)

@app.post("/generate-full-media/")
async def generate_full_media(
    poem_id: str, 
    text: str, 
    gender: str = "female",
    lang: str = "HI"
):
    db.collection("poems").document(poem_id).update({
        "audioGenerationStatus": "processing"
    })
    
    try:
        # 🛑 Pipeline function ke aage 'await' laga diya taaki yeh response block kare
        await process_edge_audio_pipeline(poem_id, text, gender, lang)
        return {
            "audioGenerationStatus": "Success",
            "message": "Edge studio-audio generated and synced successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Edge Pipeline Internal Error: {str(e)}")
