import cv2
import moviepy as mp

def get_video_properties(video_path):
    """
    Gets video properties like frame count, resolution, and FPS.

    Args:
        video_path (str): Path to the video.
    Returns:
        dict: Video properties including fps, frame_count, frame_width, frame_height.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video at {video_path}")
        return None
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    cap.release()

    return {
        "fps": int(fps),
        "frame_count": frame_count,
        "frame_width": frame_width,
        "frame_height": frame_height
    }

def resize_and_adjust_video_with_audio(input_path, output_path, frame_count, resolution, fps):
    """
    Adjusts a video's dimensions and frame count while retaining audio.

    Args:
        input_path (str): Path to the input video.
        output_path (str): Path to save the adjusted video.
        frame_count (int): Target frame count.
        resolution (tuple): Target resolution (width, height).
        fps (int): Target frames per second.
    """
    # Temporary video path without audio
    temp_video_path = "temp_video.mp4"

    # Adjust video dimensions and FPS using OpenCV
    cap = cv2.VideoCapture(input_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video_path, fourcc, fps, resolution)

    # Calculate frame skipping or duplication rate
    original_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_ratio = original_frame_count / frame_count
    frame_indices = [int(i * frame_ratio) for i in range(frame_count)]

    current_frame = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if current_frame in frame_indices:
            resized_frame = cv2.resize(frame, resolution)
            out.write(resized_frame)
        current_frame += 1

    cap.release()
    out.release()

    # Use moviepy to combine the resized video with audio
    video_clip = mp.VideoFileClip(temp_video_path)
    audio_clip = mp.AudioFileClip(input_path)
    final_clip = video_clip.with_audio(audio_clip)

    # Write the final video to the output path
    final_clip.write_videofile(output_path, codec="libx264", fps=fps)

    # Cleanup temporary file
    video_clip.close()
    audio_clip.close()
    import os
    os.remove(temp_video_path)

def preprocess_secret_video(secret_video_path, cover_video_path, output_path):
    """
    Preprocesses the secret video to match the dimensions, frame count, and audio of the cover video.

    Args:
        secret_video_path (str): Path to the secret video.
        cover_video_path (str): Path to the cover video.
        output_path (str): Path to save the preprocessed secret video.
    """
    # Get cover video properties
    cover_properties = get_video_properties(cover_video_path)
    if not cover_properties:
        print("Error: Could not retrieve cover video properties.")
        return

    frame_count = cover_properties["frame_count"]
    resolution = (cover_properties["frame_width"], cover_properties["frame_height"])
    fps = cover_properties["fps"]

    # Resize and adjust secret video
    resize_and_adjust_video_with_audio(secret_video_path, output_path, frame_count, resolution, fps)

# Example usage
preprocess_secret_video(
    secret_video_path=r"C:\Users\Rashmi\Downloads\final year pro\input\v2.mp4",
    cover_video_path=r"C:\Users\Rashmi\Downloads\final year pro\input\cover_video.mp4",
    output_path=r"C:\Users\Rashmi\Downloads\final year pro\input\secret_video.mp4"
)
