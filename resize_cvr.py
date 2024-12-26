import cv2
import moviepy as mp

def resize_video_with_audio(input_path, output_path, resolution=(640, 480), fps=30):
    # Temporary video path without audio
    temp_video_path = "temp_video.mp4"

    # Resize the video using OpenCV
    cap = cv2.VideoCapture(input_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video_path, fourcc, fps, resolution)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        resized_frame = cv2.resize(frame, resolution)
        out.write(resized_frame)

    cap.release()
    out.release()

    # Use moviepy to combine the resized video with audio
    video_clip = mp.VideoFileClip(temp_video_path)
    audio_clip = mp.AudioFileClip(input_path)
    final_clip = video_clip.with_audio(audio_clip)  # Updated method

    # Write the final video to the output path
    final_clip.write_videofile(output_path, codec="libx264", fps=fps)

    # Cleanup temporary file
    video_clip.close()
    audio_clip.close()
    import os
    os.remove(temp_video_path)

# Resize a video and retain audio
resize_video_with_audio(
    r"C:\Users\Rashmi\Downloads\final year pro\input\v1.mp4",
    r"C:\Users\Rashmi\Downloads\final year pro\input\cover_video.mp4",
    resolution=(640, 480)
)
