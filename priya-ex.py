from flask import Flask, jsonify, request
from flask_cors import CORS  # To handle CORS
import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import smtplib
import requests
import random
import time

app = Flask(__name__)
CORS(app)

# Initialize text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def speak(audio):
    """Convert text to speech."""
    engine.say(audio)
    engine.runAndWait()

def wishMe():
    """Greets the user based on the time of day."""
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        return "Good Morning!"
    elif 12 <= hour < 18:
        return "Good Afternoon!"
    else:
        return "Good Evening!"

def takeCommand():
    """Listens to user voice input and returns it as a string."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
        return query.lower()
    except sr.UnknownValueError:
        print("Could not understand audio. Please say that again.")
        return "none"
    except sr.RequestError:
        print("Could not request results. Check your internet connection.")
        return "none"

def sendEmail(to, content):
    """Sends an email. Replace with valid credentials for actual use."""
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login('your-email@gmail.com', 'your-password')  # Replace with actual credentials
        server.sendmail('your-email@gmail.com', to, content)
        server.close()
        return "Email has been sent successfully!"
    except Exception as e:
        print(e)
        return "Sorry, I was unable to send the email."

def getWeather(city):
    """Fetches current weather of a given city."""
    api_key = "your_openweathermap_api_key"  # Get an API key from OpenWeatherMap
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    response = requests.get(url).json()
    
    if response.get("main"):
        temp = response["main"]["temp"]
        description = response["weather"][0]["description"]
        return f"The temperature in {city} is {temp} degrees Celsius with {description}."
    else:
        return "Sorry, I couldn't fetch the weather. Please check the city name."

def getNews():
    """Fetches the latest news headlines."""
    api_key = "your_newsapi_key"  # Get an API key from NewsAPI
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
    
    response = requests.get(url).json()
    
    if response["status"] == "ok":
        headlines = []
        for i, article in enumerate(response["articles"][:5]):
            headlines.append(f"News {i+1}: {article['title']}")
        return headlines
    else:
        return "Sorry, I couldn't fetch the news."

def tellJoke():
    """Tells a random joke."""
    jokes = [
        #"Why don't scientists trust atoms? Because they make up everything!",
        #"What did one ocean say to the other ocean? Nothing, they just waved!",
        #"Why don't skeletons fight each other? Because they don't have the guts!"
        "Alefiya Maa Taarif Nai Karo Ahad Ni"
        # "AAKIB Bhai Yaha Dhyan Dedo"
    ]
    return random.choice(jokes)

def setReminder(reminder, delay):
    """Sets a reminder after a time delay (in seconds)."""
    time.sleep(delay)
    return f"Reminder: {reminder}"

@app.route('/voice-command', methods=['POST'])
def voice_command():
    query = request.json.get('command', '').lower()

    if 'wikipedia' in query:
        query = query.replace("wikipedia", "")
        try:
            results = wikipedia.summary(query, sentences=2)
            return jsonify({"reply": f"According to Wikipedia: {results}"})
        except wikipedia.exceptions.DisambiguationError:
            return jsonify({"reply": "Multiple results found. Please be more specific."})
        except wikipedia.exceptions.PageError:
            return jsonify({"reply": "No matching page found."})

    elif 'open youtube' in query:
        webbrowser.open("https://www.youtube.com")
        return jsonify({"reply": "Opening YouTube."})

    elif 'weather' in query:
        speak("Which city?")
        city = takeCommand()
        if city != "none":
            weather_info = getWeather(city)
            return jsonify({"reply": weather_info})

    elif 'news' in query:
        news = getNews()
        return jsonify({"reply": news})

    elif 'tell me a joke' in query or 'joke' in query:
        joke = tellJoke()
        return jsonify({"reply": joke})

    elif 'set reminder' in query:
        return jsonify({"reply": "What should I remind you about?"})

    elif 'send email' in query:
        # Mock email functionality
        return jsonify({"reply": "Email functionality is not implemented yet."})

    else:
        return jsonify({"reply": "I did not understand that. Please repeat."})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
