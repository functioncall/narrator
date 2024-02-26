import os
import base64
import time
import errno
from openai import OpenAI
from elevenlabs import generate, play, set_api_key

client = OpenAI()

set_api_key(os.environ.get("ELEVENLABS_API_KEY"))

def encode_image(image_path):
    while True:
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except IOError as e:
            if e.errno != errno.EACCES:
                raise  # Not a "file in use" error, re-raise
            time.sleep(0.1)  # File is being written to, wait a bit and retry

def play_audio(text):
    audio = generate(text, voice=os.environ.get("ELEVENLABS_VOICE_ID"))
    
    unique_id = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8").rstrip("=")
    dir_path = os.path.join("narration", unique_id)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, "audio.wav")
    
    with open(file_path, "wb") as f:
        f.write(audio)

    play(audio)

def generate_new_line(base64_image):
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image"},
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                },
            ],
        },
    ]

def analyze_image(base64_image, script):
    print("script", script)
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": """
                You are comedian Andrew Schulz. Narrate the picture of the person. Make it super short like a sentence.
                Make it snarky and funny in his crowdwork style. Don't repeat yourself. If I do anything remotely interesting, make a big deal about it!.
                """,
            },
        ] + script + generate_new_line(base64_image),
        max_tokens=100,
    )
    response_text = response.choices[0].message.content
    return response_text

def main():
    # Initial system context message reinforcing the desired narration style
    script = [
        {
            "role": "system",
            "content": """
            You are comedian Andrew Schulz. Narrate the picture of the person. Make it super short like a sentence.
            Make it snarky and funny in his crowdwork style. Don't repeat yourself. If I do anything remotely interesting, make a big deal about it!.
            """
        }
    ]

    while True:
        image_path = os.path.join(os.getcwd(), "./frames/frame.png")
        base64_image = encode_image(image_path)

        print("👀 Observing...")
        analysis = analyze_image(base64_image, script=script)

        print("🎙️ Narration:")
        print(analysis)

        play_audio(analysis)

        script = script + [{"role": "assistant", "content": analysis}]

        time.sleep(5)  # Wait for 5 seconds before the next cycle

if __name__ == "__main__":
    main()
