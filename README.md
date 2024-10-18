# Speakify: Visual and Audio Reading Assistant

This project is a Visual and Audio Reading Assistant developed as an undergraduate project at the Department of Electrical & Computer Engineering, University of Peloponnese for the course "Digital Sound and Image Processing." The project was performed by Tsikelis G., under the supervision of Associate Prof. Athanasios Koutras.

## Description

Speakify is an accessible tool designed to assist users in reading and understanding text through visual and audio formats. The application allows users to open and read various file types, describe images using AI, convert text to speech, and customize audio playback settings. It provides support for multiple languages and gender-specific voice options.

### Key Features:
1. **File Reading:** Supports reading of text files, PDFs, and upcoming support for EPUB files.
2. **Image Description:** Utilizes a machine learning model for image captioning, with translation to the user's preferred language.
3. **Text-to-Speech Conversion:** Converts text to speech using Google Cloud's Text-to-Speech API, allowing customization of voice settings such as gender, speed, pitch, and volume.
4. **Audio Playback:** Includes audio playback controls with play, pause, resume, and reset functionality.
5. **Language Support:** Offers multilingual support for English, Greek, German, French, and Spanish.

## Features

- **Multi-format support for reading text files and PDFs**
- **AI-powered image description with real-time translation**
- **Customizable text-to-speech settings**
- **User-friendly graphical interface with `tkinter`**
- **Context menu for easy text manipulation (cut, copy, paste)**

## Requirements

To run this project, the following dependencies must be installed:

- Python 3.7 or higher
- `tkinter` for the graphical user interface (usually included with Python)
- `PyPDF2` for reading PDF files
- `google-cloud-texttospeech` and `google-cloud-vision` for cloud-based text-to-speech and image processing
- `transformers` for the AI image description model
- `pygame` for audio playback
- `pillow` for image handling

You will also need to set up Google Cloud credentials for the Text-to-Speech and Vision APIs.

## Setup Instructions

1. **Install Python Dependencies:**
   ```
   pip install tkinter PyPDF2 google-cloud-texttospeech google-cloud-vision transformers pygame pillow
   ```

2. **Configure Google Cloud Credentials:**
   - Replace the placeholder `GOOGLE_APPLICATION_CREDENTIALS` with the path to your Google Cloud JSON credentials file.

3. **Run the Application:**
   ```
   python visualreader.py
   ```

   - The graphical user interface will open, allowing you to interact with the application's features.

## Usage Notes

- Make sure to configure the Google Cloud credentials correctly.
- The image description feature requires an internet connection for AI processing.
- Audio playback options (play, pause, resume) will be enabled after text-to-speech conversion.

## License

This project is intended for educational purposes and may not be used for commercial applications without proper licensing.
