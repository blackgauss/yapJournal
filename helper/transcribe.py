from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import whisper
import os

def preprocess_audio(input_file, output_file="processed_audio.wav", silence_threshold=-50.0, chunk_size=10):
    """
    Preprocess audio by:
    1. Trimming silence
    2. Converting to mono
    3. Downsampling to 16kHz
    4. Exporting the processed audio

    :param input_file: Path to the input audio file
    :param output_file: Path to save the processed audio file
    :param silence_threshold: Silence threshold in dB
    :param chunk_size: Size of chunks for silence detection (in ms)
    :return: Path to the processed audio file
    """
    try:
        # Load the audio file
        audio = AudioSegment.from_file(input_file)

        # Step 1: Trim silence
        print("Trimming silence...")
        nonsilent_ranges = detect_nonsilent(audio, min_silence_len=500, silence_thresh=silence_threshold)
        if nonsilent_ranges:
            start_trim = nonsilent_ranges[0][0]
            end_trim = nonsilent_ranges[-1][1]
            audio = audio[start_trim:end_trim]
            print(f"Audio trimmed to non-silent range: {start_trim}ms to {end_trim}ms")
        else:
            print("No significant non-silent range found. Skipping silence trimming.")

        # Step 2: Convert to mono
        print("Converting to mono...")
        audio = audio.set_channels(1)

        # Step 3: Downsample to 16kHz
        print("Downsampling to 16kHz...")
        audio = audio.set_frame_rate(16000)

        # Step 4: Export processed audio
        audio.export(output_file, format="wav")
        print(f"Audio processed and saved to {output_file}")

        return output_file
    except Exception as e:
        print(f"Error during preprocessing: {e}")
        return None

def transcribe_audio(file_path):
    """
    Transcribe an audio file using OpenAI Whisper.
    :param file_path: Path to the audio file.
    :return: Transcription text.
    """
    try:
        # Load Whisper model (use a smaller model for faster transcription)
        print("Loading Whisper model...")
        model = whisper.load_model("base")

        # Transcribe the audio file
        print("Transcribing audio...")
        result = model.transcribe(file_path)

        # Return the transcription text
        transcription = result.get("text", "")
        print("Transcription completed.")
        return transcription
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

def preprocess_and_transcribe(input_file):
    """
    Preprocess an audio file and then transcribe it.
    :param input_file: Path to the input audio file.
    :return: Transcription text.
    """
    try:
        # Step 1: Preprocess the audio file
        processed_file = preprocess_audio(input_file)

        if not processed_file:
            print("Audio preprocessing failed.")
            return None

        # Step 2: Transcribe the processed audio file
        transcription = transcribe_audio(processed_file)
        return transcription
    except Exception as e:
        print(f"Error during preprocess and transcribe: {e}")
        return None


# Example usage
if __name__ == "__main__":
    # Input audio file
    input_audio = "example.wav"  # Replace with your input audio file

    # Process and transcribe the audio
    transcription = preprocess_and_transcribe(input_audio)

    if transcription:
        print("Final Transcription:")
        print(transcription)
    else:
        print("Failed to transcribe the audio.")
