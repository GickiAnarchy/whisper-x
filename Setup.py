# Install whisperx
!pip install git+https://github.com/m-bain/whisperx.git -qqq
# Install torch with CUDA for GPU acceleration (often already installed, but good to ensure)
!pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 -qqq



from google.colab import files
uploaded = files.upload()
audio_file_path = list(uploaded.keys())[0] # Assumes one file uploaded
print(f"Uploaded file: {audio_file_path}")
