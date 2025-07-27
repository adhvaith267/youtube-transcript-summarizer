# YT Summarizer ✨

A sleek, modern web application for fetching YouTube video transcripts and generating high-quality summaries using the Google Gemini API. The frontend is built with Tailwind CSS for a beautiful, responsive dark-mode interface.

![image](https://user-images.githubusercontent.com/12345/your-screenshot.png) <!-- It's recommended to add a screenshot of your beautiful UI here! -->

## Features

-   **Stunning Dark-Mode UI:** A modern, visually appealing interface built with Tailwind CSS.
-   **Gemini-Powered Summaries:** Leverages the powerful `gemini-1.5-flash` model for fast and accurate summaries.
-   **Multi-Language Support:** Summarize transcripts in English, German, French, Spanish, Japanese, Korean, or the original language of the transcript.
-   **Real-time Streaming:** Summaries are streamed to the UI word-by-word as they are generated.
-   **Efficient Transcript Fetching:** Uses `yt-dlp` to efficiently find all available transcripts for a video.

## Technology Stack

-   **Backend:** Python, Flask
-   **AI:** Google Gemini API (`google-generativeai`)
-   **Frontend:** HTML, Tailwind CSS, vanilla JavaScript
-   **Dependencies:** `yt-dlp`, `python-dotenv`

## Setup and Installation

Follow these steps to get the project running on your local machine.

### 1. Prerequisites

-   Python 3.11+
-   A [Google Gemini API Key](https://makersuite.google.com/app/apikey)

### 2. Get Your API Key

1.  Go to **[Google AI Studio](https://makersuite.google.com/app/apikey)**.
2.  Sign in and click "**Create API key in new project**".
3.  Copy the generated key.

### 3. Clone the Project

```bash
# Clone this repository
git clone https://github.com/your-username/yt-summarizer.git
cd yt-summarizer
```

### 4. Set Up the Environment

Using a virtual environment is strongly recommended to keep project dependencies isolated.

```bash
# Create a virtual environment
python -m venv venv

# Activate the environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 5. Install Dependencies

Install the required Python packages using pip.

```bash
pip install -r requirements.txt
```

### 6. Configure Your API Key

Create a `.env` file in the root of the project. This file will hold your secret API key.

```
GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

Replace `YOUR_API_KEY_HERE` with the key you obtained from Google AI Studio. The app is configured to load this key automatically.

### 7. Run the Application

Once everything is set up, you can start the Flask server.

```bash
python app.py
```

The application will be running at **http://122.0.0.1:5000**. Open this URL in your browser to use the app.

---

This README should now accurately reflect the project in its current, visually updated state. Let me know if you need any other adjustments to it. 