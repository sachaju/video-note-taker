# 🎥 Video Note Taker

Turn long videos, lectures, and meetings into structured notes — automatically.

## What it does

* Paste a YouTube URL **or upload an audio/video file**
* Get a timestamped transcript
* Generate a structured summary
* Extract decisions and action items
* Ask questions about the content through a RAG-based Q&A interface
* Get answers grounded in the actual transcript, with relevant timestamps

> **⚠️ YouTube note:** YouTube's anti-bot and access restrictions can sometimes prevent automated downloads. If a YouTube URL cannot be processed, you can download the video/audio yourself and use the **Upload audio/video file** option instead.

## How it works

1. **Ingestion** — YouTube URLs are processed with `yt-dlp`, while uploaded audio/video files can be processed directly. `ffmpeg` converts audio to 16kHz mono WAV when needed.
2. **Speech-to-text** — `faster-whisper` (int8 quantized, CPU) transcribes the audio with timestamps.
3. **Summarization** — The transcript is chunked and summarized using an LLM through the Groq API (`openai/gpt-oss-20b`).
4. **Action item extraction** — A separate LLM pass extracts decisions, tasks, and action items.
5. **RAG Q&A** — Transcript segments are embedded with `sentence-transformers` and indexed with `FAISS`; questions retrieve relevant segments and the summary, then an LLM generates an answer grounded in that context.
6. **UI** — The application is served through Streamlit.

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

## Using the application

The application supports two input methods:

### YouTube URL

Paste a public YouTube URL into the application and start processing.

YouTube extraction depends on YouTube's current access and anti-bot policies. Because these policies can change, a YouTube URL may occasionally fail even when the video is publicly accessible.

### Audio/video upload

If YouTube extraction does not work, you can upload the media file directly.

Supported file types currently include:

* MP3
* WAV
* MP4
* M4A

The uploaded file is processed locally for transcription.

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
* YouTube may temporarily block automated requests or require additional verification.
* Direct file uploads provide an alternative when YouTube extraction is unavailable.
* The application currently processes uploaded media locally and does not provide persistent storage for uploaded files.

## Future improvements

* Deploy the application publicly with Streamlit
* Improve YouTube ingestion reliability
* Improve retrieval with reranking
* Add multilingual support
* Add persistent vector storage
* Add evaluation metrics for transcription, retrieval, and answer quality
* Add support for more audio/video formats
* Improve error handling and user feedback during processing

## License

This project is for educational and portfolio purposes.

