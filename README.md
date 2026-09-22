# 🎥 Video Note Taker

Turn long videos, lectures, and meetings into structured notes — automatically.

## What it does

* Paste a YouTube URL
* Get a timestamped transcript
* Generate a structured summary
* Extract decisions and action items
* Ask questions about the content through a RAG-based Q&A interface
* Get answers grounded in the actual transcript, with relevant timestamps

## How it works

1. **Ingestion** — `yt-dlp` downloads the audio and `ffmpeg` converts it to 16kHz mono WAV
2. **Speech-to-text** — `faster-whisper` (int8 quantized, CPU) transcribes the audio with timestamps
3. **Summarization** — the transcript is chunked and summarized using an LLM through the Groq API (`openai/gpt-oss-20b`)
4. **Action item extraction** — a separate LLM pass extracts decisions, tasks, and action items
5. **RAG Q&A** — transcript segments are embedded with `sentence-transformers` and indexed with `FAISS`; questions retrieve relevant segments and the summary, then an LLM generates an answer grounded in that context
6. **UI** — the application is served through Streamlit

## Tech stack

Python · faster-whisper · Groq API · sentence-transformers · FAISS · Streamlit · yt-dlp · ffmpeg

The project is designed to run with free-tier services; no paid API is required for the default setup.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/sachaju/video-note-taker.git
cd video-note-taker
```

### 2. Create and activate a virtual environment

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Then install the Python dependencies:

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

On Windows, you can install FFmpeg with:

```bash
winget install ffmpeg
```

Make sure `ffmpeg` is available in your PATH.

### 4. Configure the Groq API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_api_key_here
```

Get an API key from [Groq Console](https://console.groq.com/).

**Do not commit your `.env` file.** It is already excluded through `.gitignore`.

### 5. Run the application

```bash
streamlit run scripts/app.py
```

Then open the local Streamlit URL shown in the terminal.

## Project structure

```text
video-note-taker/
│
├── scripts/
│   ├── app.py              # Streamlit interface
│   ├── download_audio.py   # YouTube audio download
│   ├── transcribe.py       # Speech-to-text
│   ├── summarize.py        # Transcript summarization
│   ├── ask.py              # RAG-based Q&A
│   └── listmodels.py       # Groq model inspection
│
├── .streamlit/
│   └── config.toml
│
├── requirements.txt
├── .gitignore
└── README.md
```

## RAG pipeline

The Q&A system follows a retrieval-augmented generation workflow:

```text
Transcript
    ↓
Chunking
    ↓
Sentence embeddings
    ↓
FAISS vector index
    ↓
Semantic retrieval
    ↓
Relevant transcript segments
    +
Summary
    ↓
LLM
    ↓
Grounded answer + timestamps
```

The goal is to keep answers grounded in the source material rather than relying only on the model's general knowledge.

## Limitations

* Transcription quality depends on audio quality, accents, background noise, and the speech-to-text model.
* Long videos require more processing time because transcription runs locally.
* RAG answers are limited by the quality of the retrieved transcript segments.
* YouTube availability and extraction behavior may change over time.
* The application currently focuses on YouTube-based video ingestion.

## Future improvements

* Deploy the application publicly with Streamlit
* Add support for uploaded audio/video files
* Improve retrieval with reranking
* Add multilingual support
* Add persistent vector storage
* Add evaluation metrics for transcription, retrieval, and answer quality

## License

This project is for educational and portfolio purposes.
