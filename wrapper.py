import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, simpledialog, Menu, filedialog
import google.generativeai as genai
import os
from dotenv import load_dotenv
import threading
import queue
import json
from PIL import Image, ImageTk

# Load API key from .env file
load_dotenv()
api_key = os.getenv("key")
if not api_key:
    raise ValueError("API key not found. Please ensure you have a .env file with a key 'key'.")

# Configure Google Generative AI
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Load prompts from JSON file
def load_prompts():
    if os.path.exists("prompts.json"):
        with open("prompts.json", "r") as file:
            return json.load(file)
    return {}

# Save prompts to JSON file
def save_prompts(prompts):
    with open("prompts.json", "w") as file:
        json.dump(prompts, file, indent=4)

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini Wrapper Application")
        self.root.configure(borderwidth=1, relief="flat")

        # Frame for the main content
        self.content_frame = tk.Frame(root, bd=1, relief="flat")
        self.content_frame.pack(padx=1, pady=1, fill=tk.BOTH, expand=True)

        self.history = []
        self.prompts = load_prompts()

        self.chat_window = scrolledtext.ScrolledText(self.content_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_window.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)

        # Frame to hold the entry and send button
        self.entry_frame = tk.Frame(self.content_frame)
        self.entry_frame.pack(padx=20, pady=5, fill=tk.X, expand=False)

        self.message_entry = tk.Entry(self.entry_frame, width=50)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.message_entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.entry_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

        # Menu
        self.menu = Menu(root)
        root.config(menu=self.menu)

        self.prompt_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Prompts", menu=self.prompt_menu)
        self.prompt_menu.add_command(label="Manage Prompts", command=self.open_prompt_window)

        # Dropdown for selecting a prompt
        self.selected_prompt = tk.StringVar()
        self.selected_prompt.set("None")
        self.prompt_combobox_menu = Menu(self.menu, tearoff=0)
        self.update_prompt_combobox()
        self.menu.add_cascade(label="Select Prompt", menu=self.prompt_combobox_menu)

        # Queue for communication between threads
        self.response_queue = queue.Queue()

        # Process the response queue periodically
        self.root.after(100, self.process_response_queue)

    def send_message(self, event=None):
        question = self.message_entry.get()
        if not question.strip():
            messagebox.showwarning("Empty message", "Please enter a message.")
            return

        # Check for the "@clear" command
        if question.strip() == "@clear":
            self.clear_chat()
            self.message_entry.delete(0, tk.END)
            return
        
        # Check for the "@save" command
        if question.strip() == "@save":
            self.save_chat_history()
            self.message_entry.delete(0, tk.END)
            return
        
        # Check for the "@load" command
        if question.strip() == "@load":
            self.load_chat_history()
            self.message_entry.delete(0, tk.END)
            return

        selected_prompt = self.selected_prompt.get()
        temp_message = self.prompts.get(selected_prompt, " ") if selected_prompt != "None" else " "
        self.add_message_to_chat("You", question)
        self.message_entry.delete(0, tk.END)

        # Change window border color to green
        self.root.configure(borderwidth=1, relief="flat", bg="green")

        # Start a new thread to generate response
        threading.Thread(target=self.generate_response, args=(temp_message, question,), daemon=True).start()

    def generate_response(self, temp_message, question):
        try:
            message = temp_message + f"you are Camile, your job is to answer my question: {question}. These are our previous question-answer chat history all the paragraphs are replied by you: {self.history}"
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
                    # Change window border color back to default
                    self.root.configure(borderwidth=1, relief="flat", bg="#36454F")
                    break  # Exit the loop after processing one response
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

    def clear_chat(self):
        self.history.clear()
        self.chat_window.config(state=tk.NORMAL)
        self.chat_window.delete(1.0, tk.END)
        self.chat_window.config(state=tk.DISABLED)

    def save_chat_history(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                for message in self.chat_window.get("1.0", tk.END).strip().split("\n"):
                    file.write(message + "\n")
            messagebox.showinfo("Success", "Chat history saved successfully.")

    def load_chat_history(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                self.clear_chat()
                for line in file:
                    line = line.strip()
                    if ": " in line:
                        sender, message = line.split(": ", 1)
                        self.add_message_to_chat(sender, message)
                    else:
                        # Handle unrecognized lines as messages without a sender specified
                        print("detected unknow +-")
            messagebox.showinfo("Success", "Chat history loaded successfully.")



    def open_prompt_window(self):
        prompt_window = tk.Toplevel(self.root)
        prompt_window.title("Manage Prompts")
        prompt_window.geometry("400x300")

        # Listbox to display prompts
        self.prompt_listbox = tk.Listbox(prompt_window)
        self.prompt_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.update_prompt_listbox()

        # Buttons to manage prompts
        button_frame = tk.Frame(prompt_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        add_button = tk.Button(button_frame, text="Add", command=self.add_prompt)
        add_button.pack(side=tk.LEFT, padx=5)

        edit_button = tk.Button(button_frame, text="Edit", command=self.edit_prompt)
        edit_button.pack(side=tk.LEFT, padx=5)

        delete_button = tk.Button(button_frame, text="Delete", command=self.delete_prompt)
        delete_button.pack(side=tk.LEFT, padx=5)

    def update_prompt_listbox(self):
        self.prompt_listbox.delete(0, tk.END)
        for prompt_name in self.prompts:
            self.prompt_listbox.insert(tk.END, prompt_name)

    def update_prompt_combobox(self):
        self.prompt_combobox_menu.delete(0, tk.END)
        self.prompt_combobox_menu.add_radiobutton(label="None", variable=self.selected_prompt, value="None")
        for prompt_name in self.prompts.keys():
            self.prompt_combobox_menu.add_radiobutton(label=prompt_name, variable=self.selected_prompt, value=prompt_name)

    def add_prompt(self):
        prompt_name = simpledialog.askstring("Prompt Name", "Enter the name of the prompt:")
        if prompt_name:
            prompt_text = simpledialog.askstring("Prompt Text", "Enter the text for the prompt:")
            if prompt_text:
                self.prompts[prompt_name] = prompt_text
                save_prompts(self.prompts)
                self.update_prompt_listbox()
                self.update_prompt_combobox()

    def edit_prompt(self):
        selected_prompt = self.prompt_listbox.get(tk.ACTIVE)
        if selected_prompt:
            new_prompt_text = simpledialog.askstring("Edit Prompt", f"Edit the text for '{selected_prompt}':", initialvalue=self.prompts[selected_prompt])
            if new_prompt_text:
                self.prompts[selected_prompt] = new_prompt_text
                save_prompts(self.prompts)
                self.update_prompt_listbox()
                self.update_prompt_combobox()

    def delete_prompt(self):
        selected_prompt = self.prompt_listbox.get(tk.ACTIVE)
        if selected_prompt:
            del self.prompts[selected_prompt]
            save_prompts(self.prompts)
            self.update_prompt_listbox()
            self.update_prompt_combobox()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.geometry("500x400")
    root.mainloop()
