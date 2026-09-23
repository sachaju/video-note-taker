import streamlit as st
import sys
import os
import glob

sys.path.append("scripts")

from download_audio import download_audio
from transcribe import transcribe_audio
from summarize import chunk_transcript, summarize_chunk, extract_action_items
from ask import build_index, retrieve_relevant_segments, answer_question, embedder

with st.sidebar:
    st.header("About")
    st.write(
        "This tool downloads a video's audio, transcribes it with Whisper, "
        "summarizes it with an LLM, extracts action items, and lets you ask "
        "questions grounded in the actual content."
    )
    st.divider()
    st.caption("Built with faster-whisper, Groq, FAISS, and Streamlit — all free tools.")

st.set_page_config(page_title="Video Note Taker", page_icon="🎥", layout="wide")
st.markdown("# 🎥 Video Note Taker")
st.markdown("##### Turn long videos and lectures into structured notes, action items, and searchable Q&A — free and open source.")
st.divider()

# --- Session state setup ---
if "transcript" not in st.session_state:
    st.session_state.transcript = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "actions" not in st.session_state:
    st.session_state.actions = None
if "index" not in st.session_state:
    st.session_state.index = None

def find_latest_wav(folder="data"):
    files = glob.glob(f"{folder}/*.wav")
    return max(files, key=os.path.getctime)

def clear_previous_data(folder="data"):
    for f in glob.glob(f"{folder}/*"):
        os.remove(f)

# --- Input section ---
input_mode = st.radio("Input type", ["YouTube URL", "Upload audio/video file"], horizontal=True)

youtube_url = None
uploaded_file = None

if input_mode == "YouTube URL":
    youtube_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
else:
    uploaded_file = st.file_uploader("Upload a file", type=["mp3", "wav", "mp4", "m4a"])

run_button = st.button("Process Video")

# --- Processing ---
if run_button and (youtube_url or uploaded_file):
    clear_previous_data()

    if youtube_url:
        with st.spinner("Downloading audio..."):
            download_audio(youtube_url)
            audio_path = find_latest_wav()
    else:
        with st.spinner("Saving uploaded file..."):
            audio_path = f"data/{uploaded_file.name}"
            with open(audio_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

    with st.spinner("Transcribing (this can take a minute)..."):
        transcript, transcript_path = transcribe_audio(audio_path)
        st.session_state.transcript = transcript
    os.remove(audio_path)

    with st.spinner("Summarizing..."):
        chunks = chunk_transcript(transcript)
        summaries, actions = [], []
        for chunk in chunks:
            summaries.append(summarize_chunk(chunk))
            actions.append(extract_action_items(chunk))
        st.session_state.summary = "\n\n".join(summaries)
        st.session_state.actions = "\n\n".join(actions)

    with st.spinner("Building Q&A index..."):
        index, texts = build_index(transcript)
        st.session_state.index = index

    st.success("Done!")

# --- Results section ---
if st.session_state.transcript:
    tab1, tab2, tab3 = st.tabs(["📝 Summary", "✅ Action Items", "❓ Ask a Question"])

    with tab1:
        st.markdown(st.session_state.summary)

    with tab2:
        st.markdown(st.session_state.actions)

    with tab3:
        question = st.text_input("Your question")
        if st.button("Ask") and question:
            relevant = retrieve_relevant_segments(
                question, st.session_state.index, None, st.session_state.transcript
            )
            answer = answer_question(question, relevant, st.session_state.summary)
            st.write(answer)