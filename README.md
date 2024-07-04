# Gemini Wrapper Application

This application provides a simple interface for interacting with Google's Gemini generative AI model. It allows you to send messages and receive responses from the model, and provides the ability to manage prompts.

## Features

* **Chat Interface:** Send messages to the Gemini model and receive responses in a chat-like format.
* **Prompt Management:** Create, edit, and delete custom prompts to guide the model's responses.
* **History:** Keep track of your conversation history with the model.
* **Thread-Based Response Handling:**  The application uses threading to handle response generation, ensuring a smoother user experience. 

## Requirements

* Python 3.6 or higher
* tkinter library
* google-generativeai library
* dotenv library
* PIL (Pillow) library

## Installation

1. **Install dependencies:**
   ```bash
   pip install tkinter google-generativeai dotenv Pillow
   ```

2. **Create a .env file** in the same directory as the script. This file should contain your Google Generative AI API key in the following format:
   ```
   key=YOUR_API_KEY
   ```
   You can obtain your API key from the [Google Cloud console](https://console.cloud.google.com/).

## Usage

1. Run the `main.py` script:
   ```bash
   python main.py
   ```

2. A window will appear with a chat interface.

3. Type your message in the entry field and press enter or click the "Send" button.

4. The Gemini model will respond to your message in the chat window.

## Prompts

* **Managing Prompts:**
    * Click the "Prompts" menu item.
    * Select "Manage Prompts" to open a separate window for managing prompts.
    * In the prompt management window:
        * **Add Prompt:** Create a new prompt with a name and text.
        * **Edit Prompt:** Modify the text of an existing prompt.
        * **Delete Prompt:** Remove a prompt.
* **Using Prompts:**
    * Click the "Select Prompt" menu item to choose a prompt from the dropdown list.
    * The selected prompt will be used as a prefix for your messages when sending them to the Gemini model.

## Notes

* The `prompts.json` file stores your custom prompts. It will be created if it doesn't exist.
* The application uses the "gemini-1.5-flash" model by default. You can modify the `model_name` variable in the `main.py` script to use a different model.
* The `history` feature remembers the last 10 messages.
* The response handling is asynchronous, so the application may not always be able to provide instant responses. 
