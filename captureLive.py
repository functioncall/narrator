import subprocess
import os

def get_stream_url(youtube_url):
    # Command to get the direct video stream URL using yt-dlp
    command = ['yt-dlp', '--youtube-skip-dash-manifest', '-g', youtube_url]
    
    # Run the command and capture the output
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Return the direct stream URL
    return process.stdout.strip()

def capture_frames(stream_url, output_dir='frames', filename='frame.jpg', fps=1/5, width=250, height=140):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Construct the output file path
    output_path = os.path.join(output_dir, filename)
    
    # Command to capture a frame every 5 seconds and resize it to 250x140 using ffmpeg
    # The output will be saved to the same filename 'frame.jpg', overwriting it each time
    command = ['ffmpeg', '-i', stream_url, '-vf', f'fps={fps},scale={width}:{height}', '-update', '1', output_path]
    
    # Run the command
    subprocess.run(command)

# Example usage
youtube_url = "https://youtu.be/XZ_XEeXbsjw"
stream_url = get_stream_url(youtube_url)
if stream_url:
    print(f"Stream URL: {stream_url}")
    capture_frames(stream_url)
else:
    print("Failed to get stream URL")
