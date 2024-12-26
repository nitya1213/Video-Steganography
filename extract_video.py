import cv2
import numpy as np
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def decrypt_frame_buffer(encrypted_data, key, iv, frame_shape):
    """
    Decrypts the encrypted frame buffer using AES decryption.

    Args:
        encrypted_data (bytes): Encrypted frame data.
        key (bytes): AES encryption key.
        iv (bytes): Initialization vector.
        frame_shape (tuple): Shape of the frames (height, width, channels).
    Returns:
        list: Decrypted video frames as numpy arrays.
    """
    cipher = AES.new(key, AES.MODE_CFB, iv=iv)
    decrypted_data = cipher.decrypt(encrypted_data)
    
    # Convert decrypted data back to frames
    frame_size = frame_shape[0] * frame_shape[1] * frame_shape[2]
    if len(decrypted_data) % frame_size != 0:
        raise ValueError(f"Decrypted data size ({len(decrypted_data)}) is not a multiple of frame size ({frame_size}).")
    
    frames = [
        np.frombuffer(decrypted_data[i:i + frame_size], dtype=np.uint8).reshape(frame_shape)
        for i in range(0, len(decrypted_data), frame_size)
    ]
    return frames

def extract_hidden_data(stego_frame, capacity):
    """
    Extracts binary data hidden in a frame.

    Args:
        stego_frame (numpy.ndarray): Stego video frame.
        capacity (int): The number of bits that can be extracted from the frame.
    Returns:
        np.ndarray: Extracted binary data as a numpy array.
    """
    flat_pixels = stego_frame[:, :, 0].flatten()  # Extract from blue channel (index 0)
    binary_data = flat_pixels[:capacity] & 1  # Get the LSBs
    return binary_data

def save_frames_as_video(frames, output_path, fps):
    """
    Saves extracted frames as a video file.

    Args:
        frames (list): List of numpy arrays representing video frames.
        output_path (str): Path to save the reconstructed video.
        fps (float): Frame rate for the output video.
    """
    height, width, _ = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for frame in frames:
        out.write(frame)
    
    out.release()

def main():
    # Paths
    stego_video_path = r'C:\Users\91945\OneDrive\Desktop\steg\final year pro\output\stego_video_with_audio.mp4'
    output_video_noaudio_path = r'C:\Users\91945\OneDrive\Desktop\steg\final year pro\output\extracted_video_noaudio.mp4'
    extracted_audio_path = r'C:\Users\91945\OneDrive\Desktop\steg\final year pro\output\extracted_audio.aac'
    final_output_path = r'C:\Users\91945\OneDrive\Desktop\steg\final year pro\output\extracted_video_with_audio.mp4'

    # Load the stego video
    stego_video = cv2.VideoCapture(stego_video_path)
    if not stego_video.isOpened():
        print("Error: Could not open stego video.")
        return

    # Get video properties
    fps = stego_video.get(cv2.CAP_PROP_FPS)
    frame_count = int(stego_video.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_height = int(stego_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_width = int(stego_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_shape = (frame_height, frame_width, 3)
    capacity_per_frame = frame_height * frame_width  # Bits per frame

    print(f"Video properties - FPS: {fps}, Frame count: {frame_count}, Frame shape: {frame_shape}")

    # Extract binary data from each frame
    binary_data = []
    for frame_idx in range(frame_count):
        ret, stego_frame = stego_video.read()
        if not ret:
            print(f"Error: Could not read frame {frame_idx}.")
            break
        print(f"Extracting data from frame {frame_idx}...")
        binary_data.extend(extract_hidden_data(stego_frame, capacity_per_frame))

    stego_video.release()
    print(f"Total binary data extracted: {len(binary_data)} bits.")

    # Convert binary data back to bytes
    encrypted_data = np.packbits(binary_data).tobytes()
    print(f"Encrypted data size: {len(encrypted_data)} bytes.")

    # Validate encrypted data size
    expected_encrypted_data_size = frame_count * capacity_per_frame // 8
    if len(encrypted_data) != expected_encrypted_data_size:
        print(f"Error: Encrypted data size mismatch. Expected: {expected_encrypted_data_size}, Got: {len(encrypted_data)}")
        return

    # Decrypt frames
    decryption_key = b'Sixteen byte key'
    iv = b'InitializationVe'
    try:
        decrypted_frames = decrypt_frame_buffer(encrypted_data, decryption_key, iv, frame_shape)
        print("Decryption successful.")
    except Exception as e:
        print(f"Error during decryption: {e}")
        return

    # Save frames as video
    try:
        save_frames_as_video(decrypted_frames, output_video_noaudio_path, fps)
        print(f"Frames saved to video: {output_video_noaudio_path}")
    except Exception as e:
        print(f"Error saving video: {e}")
        return

    # Extract and combine audio
    try:
        os.system(f"ffmpeg -y -i \"{stego_video_path}\" -q:a 0 -map a \"{extracted_audio_path}\"")
        os.system(f"ffmpeg -y -i \"{output_video_noaudio_path}\" -i \"{extracted_audio_path}\" -c:v copy -c:a aac -b:a 128k -map 0:v:0 -map 1:a:0 \"{final_output_path}\"")
        print(f"Extraction complete. Final video saved as: {final_output_path}")
    except Exception as e:
        print(f"Error during audio-video merging: {e}")
