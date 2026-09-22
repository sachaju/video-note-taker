import json
import os
import numpy as np 
import faiss
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
import streamlit as st
api_key = os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

# Load the embedding model once (small, fast, runs locally on CPU)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def load_transcript(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_index(transcript):
    # Each segment becomes one "document" we can retrieve later
    texts = [seg["text"] for seg in transcript]

    # Turn every segment into an embedding vector
    embeddings = embedder.encode(texts)

    # FAISS needs float32 numpy arrays specifically
    embeddings = np.array(embeddings).astype("float32")

    # Create a FAISS index that searches by similarity (L2 distance)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    return index, texts

def retrieve_relevant_segments(question, index, texts, transcript, top_k=3):
    # Embed the question the same way we embedded the transcript
    question_embedding = embedder.encode([question]).astype("float32")

    # Search the index for the top_k closest segments
    distances, indices = index.search(question_embedding, top_k)

    # Pull back the actual text + timestamp for each match
    results = []
    for idx in indices[0]:
        results.append(transcript[idx])
    return results


def answer_question(question, relevant_segments, full_summary):
    context = "\n".join(
        f"[{seg['start']:.0f}s] {seg['text']}" for seg in relevant_segments
    )

    prompt = f"""You are answering a question about a video, for someone who hasn't watched it.

Here is a general summary of the entire video, for overall context:
{full_summary}

Here are specific transcript excerpts that may be relevant to the question:
{context}

Question: {question}

Use the summary for general/overview questions, and the specific excerpts for precise details, timestamps, or quotes.
Use only names, pronouns, and facts exactly as they appear in the summary or excerpts above — do not infer or guess details (such as gender, identity, or relationships) that aren't explicitly stated.
If neither source answers the question, say so honestly."""
    
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    path = input("Paste path to your _transcript.json file: ")
    transcript = load_transcript(path)

    # Load the summary generated in Module 3
    summary_path = path.replace("_transcript.json", "_notes.txt")
    with open(summary_path, "r", encoding="utf-8") as f:
        full_summary = f.read()

    print("Building search index...")
    index, texts = build_index(transcript)
    print("Ready! Ask questions (type 'quit' to exit).\n")

    while True:
        question = input("Your question: ")
        if question.lower() == "quit":
            break
        relevant_segments = retrieve_relevant_segments(question, index, texts, transcript)
        answer = answer_question(question, relevant_segments, full_summary)
        print(f"\n{answer}\n")
    