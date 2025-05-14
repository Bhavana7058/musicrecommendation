from flask import Flask, render_template, Response, request, send_from_directory, jsonify
from camera import gen_frames
import os

app = Flask(__name__)

# Music folders by emotion
emotion_songs = {
    "angry": "static/songs/angry",
    "disgust": "static/songs/disgust",
    "fear": "static/songs/fear",
    "happy": "static/songs/happy",
    "neutral": "static/songs/neutral",
    "sad": "static/songs/sad",
    "surprise": "static/songs/surprise"
}

current_song_list = []
current_index = 0
playing = False
detected_emotion = "neutral"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(lambda emotion: update_emotion(emotion)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def update_emotion(emotion):
    global detected_emotion, current_song_list, current_index
    if emotion != detected_emotion:
        detected_emotion = emotion
        print(f"Detected emotion: {detected_emotion}")
        song_path = emotion_songs.get(detected_emotion, emotion_songs["neutral"])
        try:
            current_song_list = os.listdir(song_path)
            current_song_list = [f for f in current_song_list if f.endswith('.mp3')]
            if current_song_list:
                current_index = 0
        except FileNotFoundError:
            print(f"Folder not found for emotion: {detected_emotion}, using 'neutral'")
            detected_emotion = "neutral"
            current_song_list = os.listdir(emotion_songs["neutral"])
            current_song_list = [f for f in current_song_list if f.endswith('.mp3')]
            current_index = 0

@app.route('/start')
def start():
    global playing
    playing = True
    return play_song()

@app.route('/stop')
def stop():
    global playing
    playing = False
    return '', 204

@app.route('/next')
def next_song():
    global current_index
    if current_song_list:
        current_index = (current_index + 1) % len(current_song_list)
    return play_song()

@app.route('/prev')
def prev_song():
    global current_index
    if current_song_list:
        current_index = (current_index - 1) % len(current_song_list)
    return play_song()

@app.route('/get_current_emotion')
def get_current_emotion():
    return jsonify({"emotion": detected_emotion})

def play_song():
    if not playing or not current_song_list:
        return '', 204
    try:
        song_path = emotion_songs.get(detected_emotion, emotion_songs["neutral"])
        song_file = current_song_list[current_index]
        return send_from_directory(song_path, song_file)
    except Exception as e:
        print(f"Error playing song: {e}")
        return '', 500

if __name__ == '__main__':
    app.run(debug=True)
