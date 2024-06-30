import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import google.generativeai as genai
import os
from dotenv import load_dotenv
import threading
import queue

# Load API key from .env file
load_dotenv()
api_key = os.getenv("key")
if not api_key:
    raise ValueError("API key not found. Please ensure you have a .env file with a key 'key'.")

# Configure Google Generative AI
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini Wrapper Application")

        self.history = []

        self.chat_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_window.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)

        # Frame to hold the entry and send button
        self.entry_frame = tk.Frame(root)
        self.entry_frame.pack(padx=20, pady=5, fill=tk.X, expand=True)

        self.message_entry = tk.Entry(self.entry_frame, width=50)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.message_entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.entry_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

        # Queue for communication between threads
        self.response_queue = queue.Queue()

    def send_message(self, event=None):
        question = self.message_entry.get()
        if not question.strip():
            messagebox.showwarning("Empty message", "Please enter a message.")
            return

        self.add_message_to_chat("You", question)
        self.message_entry.delete(0, tk.END)

        # Start a new thread to generate response
        threading.Thread(target=self.generate_response, args=(question,), daemon=True).start()

    def generate_response(self, question):
        try:
            message = f"you are assistant names camile, your job is to answer my question :{question}, these are our previous question answer chat history all the paragraphs are replaied by you{self.history}"
            response = model.generate_content([message])
            response_text = response.text.strip()

            self.response_queue.put(response_text)
        
        except Exception as e:
            self.response_queue.put(f"Error: {str(e)}")

    def process_response_queue(self):
        while True:
            try:
                response_text = self.response_queue.get_nowait()
                if response_text.startswith("Error:"):
                    messagebox.showerror("Error", response_text)
                else:
                    self.add_message_to_chat("AI", response_text)
                    if len(self.history) >= 10:
                        self.history.pop(0)
            
            except queue.Empty:
                break

        # Schedule next check
        self.root.after(100, self.process_response_queue)

    def add_message_to_chat(self, sender, message):
        self.chat_window.config(state=tk.NORMAL)
        self.chat_window.insert(tk.END, f"{sender}: {message}\n")

        # Add checkbox
        check_var = tk.BooleanVar()
        checkbox = ttk.Checkbutton(self.chat_window, variable=check_var, command=lambda: self.toggle_history(message, check_var))
        self.chat_window.window_create(tk.END, window=checkbox)
        self.chat_window.insert(tk.END, "\n")

        self.chat_window.config(state=tk.DISABLED)
        self.chat_window.yview(tk.END)

    def toggle_history(self, message, check_var):
        if check_var.get():
            self.history.append(message)
        else:
            self.history.remove(message)
        print(f"Updated history: {self.history}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.geometry("500x400")
    root.after(100, app.process_response_queue)
    root.mainloop()
