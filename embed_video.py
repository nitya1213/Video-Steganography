import cv2
import numpy as np
import os
from concurrent.futures import ThreadPoolExecutor
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import subprocess

def encrypt_frame_buffer(frames, key):
    """
    Encrypt the entire frame buffer using AES encryption.

    Args:
        frames (list): List of frames to encrypt.
        key (bytes): 16-byte AES encryption key.
    Returns:
        tuple: Encrypted bytes and initialization vector (iv).
    """
    cipher = AES.new(key, AES.MODE_CFB)
    frame_bytes = b''.join(frame.tobytes() for frame in frames)
    encrypted = cipher.encrypt(pad(frame_bytes, AES.block_size))
    return encrypted, cipher.iv

def embed_data_in_frame(cover_frame, binary_data, capacity):
    """
    Embed binary data into a single cover frame using vectorized numpy operations.

    Args:
        cover_frame (numpy.ndarray): Cover frame to embed data into.
        binary_data (numpy.ndarray): Binary data to embed.
        capacity (int): Number of bits that can be embedded per frame.
    Returns:
        numpy.ndarray: Frame with embedded binary data.
    """
    flat_pixels = cover_frame[:, :, 0].flatten()  # Use blue channel (index 0)
    binary_data = binary_data[:capacity]  # Limit data to frame capacity

    # Safely modify pixel values
    flat_pixels[:len(binary_data)] = (flat_pixels[:len(binary_data)] & 0xFE).astype(np.uint8)  # Clear LSB
    flat_pixels[:len(binary_data)] |= binary_data  # Set LSB based on binary_data

    cover_frame[:, :, 0] = flat_pixels.reshape(cover_frame[:, :, 0].shape)
    return cover_frame

def binary_to_numpy(binary_data):
    """
    Convert binary string to numpy array of bits.

    Args:
        binary_data (str): Binary string.
    Returns:
        numpy.ndarray: Numpy array of bits.
    """
    return np.array(list(binary_data), dtype=np.uint8)

def process_frame(cover_frame, binary_data, capacity):
    """
    Embed binary data into a single frame.

    Args:
        cover_frame (numpy.ndarray): Cover frame to process.
        binary_data (numpy.ndarray): Binary data to embed.
        capacity (int): Frame embedding capacity.
    Returns:
        numpy.ndarray: Frame with embedded data.
    """
    return embed_data_in_frame(cover_frame, binary_data, capacity)

def extract_audio(video_path, output_audio_path):
    """
    Extract audio from a video file using FFmpeg.
    """
    command = [
        "ffmpeg", "-y", "-i", video_path,
        "-q:a", "0", "-map", "0:a:0", output_audio_path
    ]
    subprocess.run(command, check=True)

def embed_audio_with_ffmpeg(video_path, audio_path, output_path):
    """
    Embed audio into a video using FFmpeg.
    """
    command = [
        "ffmpeg", "-y", "-i", video_path, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        "-map", "0:v:0", "-map", "1:a:0", output_path
    ]
    subprocess.run(command, check=True)

def main():
    # Input and output paths
    cover_video_path = r'C:\Users\91945\OneDrive\Desktop\steg\final year pro\input\cover_video.mp4'
    secret_video_path = r'C:\Users\91945\OneDrive\Desktop\steg\final year pro\input\secret_video.mp4'
    output_video_path_noaudio = r'C:\Users\91945\OneDrive\Desktop\steg\final year pro\output\stego_video_noaudio.mp4'
    extracted_audio_path = r'C:\Users\91945\OneDrive\Desktop\steg\final year pro\output\cover_audio.aac'
    final_output_video_path = r'C:\Users\91945\OneDrive\Desktop\steg\final year pro\output\stego_video_with_audio.mp4'

    # Load videos
    cover_video = cv2.VideoCapture(cover_video_path)
    secret_video = cv2.VideoCapture(secret_video_path)

    if not cover_video.isOpened() or not secret_video.isOpened():
        print("Error: Could not open one or both input videos.")
        return

    # Get cover video properties
    cover_fps = int(cover_video.get(cv2.CAP_PROP_FPS))
    cover_frame_width = int(cover_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    cover_frame_height = int(cover_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    capacity_per_frame = cover_frame_width * cover_frame_height  # Bits per frame

    # Prepare output video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path_noaudio, fourcc, cover_fps, (cover_frame_width, cover_frame_height))

    # Generate encryption key
    encryption_key = os.urandom(16)

    # Read and encrypt secret frames
    secret_frames = []
    while secret_video.isOpened():
        ret, frame = secret_video.read()
        if not ret:
            break
        secret_frames.append(frame)
    secret_video.release()

    encrypted_data, iv = encrypt_frame_buffer(secret_frames, encryption_key)
    encrypted_binary_data = binary_to_numpy(''.join(format(byte, '08b') for byte in encrypted_data))

    # Process cover frames
    binary_index = 0
    with ThreadPoolExecutor() as executor:
        while cover_video.isOpened():
            ret, cover_frame = cover_video.read()
            if not ret or binary_index >= len(encrypted_binary_data):
                break

            # Embed data into frame
            stego_frame = executor.submit(
                process_frame, cover_frame, encrypted_binary_data[binary_index:], capacity_per_frame
            ).result()

            # Write frame to output video
            out.write(stego_frame)
            binary_index += capacity_per_frame

    cover_video.release()
    out.release()

    # Step 1: Extract audio from cover video
    extract_audio(cover_video_path, extracted_audio_path)

    # Step 2: Embed the extracted audio into the stego video
    embed_audio_with_ffmpeg(output_video_path_noaudio, extracted_audio_path, final_output_video_path)

    print("Embedding complete. Stego video saved as 'stego_video_with_audio.mp4'.")

if __name__ == '__main__':
    main()
