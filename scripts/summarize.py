import json
import os
from dotenv import load_dotenv
from groq import Groq 

load_dotenv()  # reads the .env file and loads GROQ_API_KEY into the environment
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def load_transcript(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def chunk_transcript(transcript, chunk_minutes=10):
    # Groups segments into ~10-minute blocks based on their start time
    chunks = []
    current_chunk = []
    chunk_start = 0

    for segment in transcript:
        if segment["start"] - chunk_start >= chunk_minutes * 60 and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            chunk_start = segment["start"]
        current_chunk.append(segment)

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def summarize_chunk(chunk):
    # Turn the chunk's segments into one text block with timestamps included
    text_with_timestamps = "\n".join(
        f"[{seg['start']:.0f}s] {seg['text']}" for seg in chunk
    )

    prompt = f"""You are summarizing a section of a transcript. 
Below is the text with timestamps in seconds.

{text_with_timestamps}

Summarize the key points from this section. For each key point, include the approximate timestamp it occurred at.
Respond in plain text, a few bullet points."""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def extract_action_items(chunk):
    text_with_timestamps = "\n".join(
        f"[{seg['start']:.0f}s] {seg['text']}" for seg in chunk
    )

    prompt = f"""Below is a section of a transcript with timestamps in seconds.

{text_with_timestamps}

Extract any action items, decisions, or tasks mentioned — things someone said they will do, should do, or was assigned to do. 
Include who is responsible if stated, and the approximate timestamp.
If there are none, respond with exactly: "No action items found."
Respond in plain text, a few bullet points if any exist."""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def summarize_transcript(json_path):
    transcript = load_transcript(json_path)
    chunks = chunk_transcript(transcript)

    print(f"Transcript split into {len(chunks)} chunk(s).")


    chunk_summaries = []
    chunk_actions = []
    for i, chunk in enumerate(chunks):
        print(f"Summarizing chunk {i+1}/{len(chunks)}...")
        summary = summarize_chunk(chunk)
        chunk_summaries.append(summary)

        print(f"Extracting action items from chunk {i+1}/{len(chunks)}...")
        actions = extract_action_items(chunk)
        chunk_actions.append(actions)


    combined_summary = "\n\n".join(chunk_summaries)
    combined_actions = "\n\n".join(chunk_actions)

    final_output = f"=== SUMMARY ===\n\n{combined_summary}\n\n=== ACTION ITEMS ===\n\n{combined_actions}"

    print("\n" + final_output)
    combined = final_output  # so the save step below still works unchanged

    output_path = json_path.replace("_transcript.json", "_notes.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(combined)
    print(f"\nSaved to {output_path}")

if __name__ == "__main__":
    path = input("Paste path to your _transcript.json file: ")
    summarize_transcript(path)
    