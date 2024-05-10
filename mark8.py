import tkinter as tk
from tkinter import ttk
import customtkinter
import webbrowser
import os
from tkinter import filedialog
import PyPDF2
import nltk
import subprocess
import win32com.client
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pyttsx3
import speech_recognition as sr
import threading
import asyncio
from collections import defaultdict
import pickle
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForQuestionAnswering, pipeline
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Set the appearance mode and color theme
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

class DariusAI(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("DariusAI")
        self.geometry("800x600")
        self.resizable(False, False)

        # Create frames
        self.sidebar_frame = customtkinter.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="both")

        self.content_frame = customtkinter.CTkFrame(self)
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Sidebar
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="DariusAI", font=("Arial", 20))
        self.logo_label.pack(pady=20, padx=10)

        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Learn from File", command=self.learn_from_file)
        self.sidebar_button_1.pack(pady=10, padx=10, fill="x")

        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="Perform Calculations", command=self.perform_calculations_prompt)
        self.sidebar_button_2.pack(pady=10, padx=10, fill="x")

        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, text="Search Web", command=self.search_on_web_prompt)
        self.sidebar_button_3.pack(pady=10, padx=10, fill="x")

        self.sidebar_button_4 = customtkinter.CTkButton(self.sidebar_frame, text="Open Item", command=self.open_windows_item_prompt)
        self.sidebar_button_4.pack(pady=10, padx=10, fill="x")

        # Content
        self.content_label = customtkinter.CTkLabel(self.content_frame, text="Welcome to DariusAI!", font=("Arial", 16))
        self.content_label.pack(pady=20, padx=20)

        self.conversation_text = customtkinter.CTkTextbox(self.content_frame, width=600, height=400)
        self.conversation_text.pack(pady=20, padx=20)
        self.conversation_text.bind("<<TextModified>>", self.on_text_modified)
        self.update_ui = False

        self.input_entry = customtkinter.CTkEntry(self.content_frame, placeholder_text="Ask me anything...", width=500)
        self.input_entry.pack(pady=20, padx=20)
        self.input_entry.bind("<Return>", self.process_input)

        # Initialize AI components
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty("voices")
        self.engine.setProperty("voice", self.voices[1].id)  # Setting the voice to female
        self.shell = win32com.client.Dispatch("WScript.Shell")
        self.knowledge_base = defaultdict(str)

        # Initialize Speech Recognizer
        self.recognizer = sr.Recognizer()

        # Initialize Machine Learning Models
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        self.qa_model = AutoModelForQuestionAnswering.from_pretrained("deepset/roberta-base-squad2")
        self.qa_pipeline = pipeline("question-answering", model=self.qa_model, tokenizer=self.tokenizer)
        self.text_classifier = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)
        self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')

        # Initialize cache
        self.cache_dir = "cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        self.load_cache()

        # Set initial conversation text
        self.insert_text("DariusAI: Hello, I'm DariusAI, your personal assistant inspired by J.A.R.V.I.S. from Iron Man.\n")
        self.insert_text("DariusAI: You can give me voice commands, and I'll respond accordingly.\n")
        self.insert_text("DariusAI: Some of the things I can do include:\n")
        self.insert_text("DariusAI: - Learn from PDF files or scripts\n")
        self.insert_text("DariusAI: - Answer questions based on what I've learned\n")
        self.insert_text("DariusAI: - Perform calculations\n")
        self.insert_text("DariusAI: - Search the web\n")
        self.insert_text("DariusAI: - Open folders, files, and applications\n")
        self.insert_text("DariusAI: To stop me, just say 'stop'.\n")

    def load_cache(self):
        cache_file = os.path.join(self.cache_dir, "cache.pkl")
        if os.path.exists(cache_file):
            with open(cache_file, "rb") as f:
                self.knowledge_base = pickle.load(f)

    def save_cache(self):
        cache_file = os.path.join(self.cache_dir, "cache.pkl")
        with open(cache_file, "wb") as f:
            pickle.dump(self.knowledge_base, f)

    def on_text_modified(self, event=None):
        self.update_ui = True

    def insert_text(self, text):
        self.conversation_text.insert("end", text)
        if self.update_ui:
            self.conversation_text.update_idletasks()
            self.update_ui = False

    def speak(self, speech_text):
        threading.Thread(target=self._speak, args=(speech_text,)).start()

    def _speak(self, speech_text):
        self.engine.say(speech_text)
        self.engine.runAndWait()

    def listen(self):
        threading.Thread(target=self._listen).start()

    def _listen(self):
        with sr.Microphone() as source:
            print("Listening...")
            self.insert_text("DariusAI: Listening...\n")
            audio = self.recognizer.listen(source)

        try:
            query = self.recognizer.recognize_google(audio)
            print(f"User said: {query}\n")
            self.insert_text(f"User: {query}\n")

            # Process the query
            self.respond(query)
        except Exception as e:
            self.insert_text(f"Speech recognition error: {e}\n")
        finally:
            # Release the audio data
            del audio

    def process_input(self, event=None):
        query = self.input_entry.get()
        self.input_entry.delete(0, "end")
        self.insert_text(f"User: {query}\n")
        self.respond(query)

    def respond(self, query):
        query = query.lower()
        if query.startswith("learn from") or query.startswith("teach me"):
            self.learn_from_file()
        elif "stop" in query:
            self.stop()
        elif "perform calculations" in query:
            self.perform_calculations(query.split("perform calculations")[1].strip())
        elif "search on web" in query:
            asyncio.create_task(self._search_on_web(query.split("search on web")[1].strip()))
        elif "open" in query:
            self.open_windows_item(query.split("open")[1].strip())
        else:
            self.answer_query(query)
            self.speak(f"You said: {query}")

    def learn_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf"), ("Text Files", "*.txt")])
        if file_path:
            self.process_file(file_path)

    def process_file(self, file_path):
        file_name = os.path.basename(file_path)
        self.speak(f"Opening the file {file_name}.")
        self.open_file(file_path)
        self.speak("Do you want me to read the file aloud or silently?")  
        answer = self.listen() 
        if answer and answer.lower() in ['aloud', 'silently']:
            self.speak(f"Okay, I will read the file {answer}.")
            self.read_file(file_path, answer)
            self.speak("I have finished reading the file. Summarizing what I learned.")
            summary = self.summarize_file(file_path)
            self.knowledge_base[file_name] = summary
            self.save_cache()
            self.insert_text(f"DariusAI: I have learned from the file '{file_name}'. You can now ask me questions related to the content.\n")

    def open_file(self, file_path):
        try:
            os.startfile(file_path)
            print(f"File {file_path.split('/')[-1]} opened successfully.")
        except Exception as e:
            self.speak(f"Error opening file: {e}")

    def read_file(self, file_path, mode):
        try:
            with open(file_path, 'rb') as file:
                if mode == 'aloud':
                    print(f"Reading file {file_path.split('/')[-1]} aloud.")
                else:
                    print(f"Reading file {file_path.split('/')[-1]} silently.")
        except Exception as e:
            self.speak(f"Error reading file: {e}")
        finally:
            # Release the file handle 
            del file  

    def summarize_file(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                if file_path.endswith('.pdf'):
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ''
                    for page in range(len(pdf_reader.pages)):
                        text += pdf_reader.pages[page].extract_text()
                else:
                    text = file.read().decode('utf-8')

            # Check if summary is already cached
            if file_path in self.knowledge_base:
                summary = self.knowledge_base[file_path]
            else:
                from nltk.corpus import stopwords
                from nltk.tokenize import word_tokenize, sent_tokenize
                import heapq

                stop_words = set(stopwords.words('english'))

                word_frequencies = {}
                for word in word_tokenize(text):
                    if word not in stop_words:
                        if word not in word_frequencies.keys():
                            word_frequencies[word] = 1
                        else:
                            word_frequencies[word] += 1

                maximum_frequencies = max(word_frequencies.values())

                for word in word_frequencies.keys():
                    word_frequencies[word] = word_frequencies[word] / maximum_frequencies

                sentence_scores = {}
                for sent in sent_tokenize(text):
                    for word in word_tokenize(sent.lower()):
                        if word in word_frequencies.keys():
                            if sent not in sentence_scores.keys():
                                sentence_scores[sent] = word_frequencies[word]
                            else:
                                sentence_scores[sent] += word_frequencies[word]

                summary_sentences = heapq.nlargest(7, sentence_scores, key=sentence_scores.get)
                summary = ' '.join(summary_sentences)
                print(f"Summary for file {file_path.split('/')[-1]}:")
                print(summary)
                self.knowledge_base[file_path] = summary
                self.save_cache()

            return summary
        except Exception as e:
            self.speak(f"Error summarizing file: {e}")
            return ""

    def answer_query(self, query):
        # Use question-answering pipeline
        context = " ".join(self.knowledge_base.values())
        result = self.qa_pipeline(question=query, context=context)

        if result['score'] >= 0.5:
            self.speak(f"Based on my knowledge, here is my answer: {result['answer']}")
            self.insert_text(f"DariusAI: {result['answer']}\n")
        else:
            # Compute semantic similarity using sentence transformers
            query_embedding = self.sentence_transformer.encode([query])[0]
            knowledge_embeddings = [self.sentence_transformer.encode([text])[0] for text in self.knowledge_base.values()]
            similarities = [cosine_similarity([query_embedding], [knowledge_embedding])[0][0] for knowledge_embedding in knowledge_embeddings]

            if max(similarities) > 0.5:
                most_relevant_text = self.knowledge_base.values()[np.argmax(similarities)]
                self.speak(f"Based on my knowledge, here is the most relevant information: {most_relevant_text}")
                self.insert_text(f"DariusAI: {most_relevant_text}\n")
            else:
                self.speak("Sorry, I don't have enough information to answer your query.")
                self.insert_text("DariusAI: Sorry, I don't have enough information to answer your query.\n")

        # Update knowledge base with user feedback
        self.speak("Was my answer helpful? Please respond with 'yes' or 'no'.")
        feedback = self.listen().lower()
        if feedback == "yes":
            self.speak("Great! I'm glad I could help.")
        elif feedback == "no":
            self.speak("I'm sorry my answer wasn't helpful. Please provide the correct information, and I'll update my knowledge.")
        
            correct_info = self.listen()
            self.knowledge_base[f"user_feedback_{len(self.knowledge_base)}"] = correct_info
            self.save_cache()
            self.speak("Thank you for the feedback. I've updated my knowledge with the correct information.")

    def stop(self):
        self.speak("Stopping the AI. Goodbye!")
        self.destroy()

    def perform_calculations_prompt(self):
        self.speak("Please enter the expression you want me to calculate.")   
        
        expression = self.listen()
        if expression:
            self.perform_calculations(expression)

    def perform_calculations(self, expression):
        try:
            result = eval(expression)
            self.speak(f"The result of {expression} is {result}")
            self.insert_text(f"DariusAI: The result of {expression} is {result}\n")
        except Exception as e:
            self.speak(f"Error performing calculations: {e}")
            self.insert_text(f"DariusAI: Error performing calculations: {e}\n")

    def search_on_web_prompt(self):
        self.speak("Please enter the query you want me to search on the web.") 
        query = self.listen().lower()
        if query:
            asyncio.create_task(self._search_on_web(query))

    async def _search_on_web(self, query):
        self.speak(f"Searching the web for: {query}")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        self.insert_text(f"DariusAI: Searching the web for: {query}\n")
    
    def open_windows_item_prompt(self):
        self.speak("Please specify the item you want me to open.") 
        item = self.listen().lower()
        if item: 
            self.open_windows_item(item) 

def open_windows_item(self, item):
    try:
        if item.lower() == "calculator":
            self.shell.Run("calc.exe")
            self.speak("Opening calculator.")
            self.insert_text("DariusAI: Opening calculator.\n")
        elif item.lower() == "notepad":
            self.shell.Run("notepad.exe")
            self.speak("Opening notepad.")
            self.insert_text("DariusAI: Opening notepad.\n")
        elif item.lower().startswith("folder"):
            folder_path = os.path.join(os.path.expanduser("~"), "Desktop", item.split("folder")[1].strip())
            self.shell.Run(f"explorer.exe {folder_path}")
            self.speak(f"Opening folder: {folder_path}")
            self.insert_text(f"DariusAI: Opening folder: {folder_path}\n")
        elif item.lower().endswith(".pdf") or item.lower().endswith(".txt") or item.lower().endswith(".docx"):
            file_path = os.path.join(os.path.expanduser("~"), "Desktop", item)
            os.startfile(file_path)
            self.speak(f"Opening file: {file_path}")
            self.insert_text(f"DariusAI: Opening file: {file_path}\n")
        else:
            self.speak(f"Sorry, I couldn't open {item}. Please specify a valid item.")
            self.insert_text(f"DariusAI: Sorry, I couldn't open {item}. Please specify a valid item.\n")
    except Exception as e:
        self.speak(f"Error opening {item}: {e}")
        self.insert_text(f"DariusAI: Error opening {item}: {e}\n")        
        
if __name__ == "__main__":
    app = DariusAI()
    app.mainloop()