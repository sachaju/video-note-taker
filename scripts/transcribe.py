from faster_whisper import WhisperModel
import json
import os

def transcribe_audio(audio_path, output_folder="data"):
    # Load the model: "small" size, running on CPU, int8 quantization for speed
    model = WhisperModel("small", device="cpu", compute_type="int8")

    # Run transcription — returns a generator of segments + metadata info
    segments, info = model.transcribe(audio_path, beam_size=5)

    print(f"Detected language: {info.language} (confidence: {info.language_probability:.2f})")

    # Convert segments into a simple list of dictionaries we can save as JSON
    transcript = []
    for segment in segments:
        transcript.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip()
        })
        print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")

    # Save to a JSON file
    filename = os.path.splitext(os.path.basename(audio_path))[0]
    output_path = f"{output_folder}/{filename}_transcript.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transcript, f, indent=2, ensure_ascii=False)

    print(f"\nSaved transcript to {output_path}")
    return transcript, output_path

if __name__ == "__main__":
    audio_file = input("Paste the path to your .wav file (e.g. data/yourfile.wav): ")
    transcribe_audio(audio_file)
    