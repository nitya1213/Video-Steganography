import cv2
import numpy as np
import pywt
from Crypto.Cipher import AES

print("OpenCV version:", cv2.__version__)
print("NumPy version:", np.__version__)
print("PyWavelets version:", pywt.__version__)

try:
    cipher = AES.new(b'16bytekey16bytek', AES.MODE_ECB)
    print("AES Encryption: Working")
except Exception as e:
    print("AES Encryption Error:", e)
