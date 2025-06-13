import requests
import websocket
import threading
import json

TEAMLY_TOKEN = "YOUR_TEAMLY_TOKEN"
HF_TOKEN = "YOUR_HUGGINGFACE_TOKEN"
MODEL = "mistralai/Mistral-7B-Instruct-v0.1"

ALLOWED_TEAM_ID = "your_team_id"
ALLOWED_CHANNEL_ID = "your_channel_id"

HEADERS = {
    "Authorization": f"Bearer {TEAMLY_TOKEN}",
    "Content-Type": "application/json"
}

HF_HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

def send_message(channel_id, content):
    url = f"https://api.teamly.one/v1/channels/{channel_id}/messages"
    data = {"content": content}
    response = requests.post(url, headers=HEADERS, json=data)
    return response.status_code

def query_ai(prompt):
    url = f"https://api-inference.huggingface.co/models/{MODEL}"
    data = {"inputs": prompt}
    response = requests.post(url, headers=HF_HEADERS, json=data)
    try:
        return response.json().get("generated_text", "AI yanıtı alınamadı.")
    except Exception:
        return str(response.text)

def on_message(ws, message):
    data = json.loads(message)
    if data.get("t") == "MESSAGE_SEND":
        content = data["d"]["content"]
        user_id = data["d"]["author"]["id"]
        channel_id = data["d"]["channel_id"]
        team_id = data["d"]["team_id"]

        if team_id != ALLOWED_TEAM_ID or channel_id != ALLOWED_CHANNEL_ID:
            return

        if not content.startswith("!"):  # Komut değilse
            yanit = query_ai(content)
            reply = f"<@{user_id}> {yanit}"
            send_message(channel_id, reply)

def start_bot():
    ws = websocket.WebSocketApp(
        "wss://api.teamly.one/gateway",
        on_message=on_message,
        header={"Authorization": f"Bearer {TEAMLY_TOKEN}"}
    )
    threading.Thread(target=ws.run_forever).start()

if __name__ == "__main__":
    start_bot()
