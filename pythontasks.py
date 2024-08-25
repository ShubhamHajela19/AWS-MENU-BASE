import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from twilio.rest import Client
import pywhatkit as pwk
import time
import logging
import requests
import base64
import openai
from gtts import gTTS
import os
import geocoder
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Twilio credentials
account_sid = "AC63e5054effe628a6584434ba5ae2a039"
auth_token = "ac2e7259134c3e289f01a433330aec18"
client = Client(account_sid, auth_token)

# Email sender details
sender_email = "charchitchouhan789@gmail.com"
email_password = "jlfwkqqucyzpdfdd"

# Endpoint to send an email
@app.route('/send_email', methods=['POST'])
def send_email():
    data = request.json
    receiver_email = data.get('email')
    subject = data.get('subject')
    body = data.get('message')

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, email_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        logging.info(f"Email sent to {receiver_email}")
        return jsonify({"status": "success", "message": "Email sent successfully!"})
    except Exception as e:
        logging.error(f"Failed to send email. Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        server.quit()

# Endpoint to send SMS using Twilio
@app.route('/send_sms', methods=['POST'])
def send_sms():
    data = request.json
    recipient_no = data.get('phone')
    message_body = data.get('message')

    try:
        message = client.messages.create(
            from_="+12086035252",  # Twilio phone number
            to=recipient_no,
            body=message_body
        )
        logging.info(f"SMS sent to {recipient_no}")
        return jsonify({"status": "success", "message": "SMS sent successfully!"})
    except Exception as e:
        logging.error(f"Failed to send SMS. Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint to scrape Google search results
@app.route('/scrape_google', methods=['POST'])
def scrape_google():
    data = request.json
    query = data.get('query')
    api_key = "YOUR_SERP_API_KEY"  # Replace with your SerpAPI key

    try:
        url = f"https://serpapi.com/search.json?engine=google&q={query}&api_key={api_key}"
        response = requests.get(url)
        search_results = response.json().get('organic_results', [])[:5]

        results = [{"title": result.get("title"), "link": result.get("link")} for result in search_results]
        return jsonify({"status": "success", "results": results})
    except Exception as e:
        logging.error(f"Failed to scrape Google. Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint to get geo coordinates
@app.route('/get_geo', methods=['POST'])
def get_geo():
    try:
        g = geocoder.ip('me')
        coordinates = g.latlng
        return jsonify({"status": "success", "coordinates": coordinates})
    except Exception as e:
        logging.error(f"Failed to get geo coordinates. Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint for text-to-audio conversion
@app.route('/text_to_audio', methods=['POST'])
def text_to_audio():
    data = request.json
    text = data.get('text')

    try:
        tts = gTTS(text=text, lang='en')
        audio_file = "output.mp3"
        tts.save(audio_file)
        return send_file(audio_file, as_attachment=True)
    except Exception as e:
        logging.error(f"Failed to convert text to audio. Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint to control laptop volume
@app.route('/control_volume', methods=['POST'])
def control_volume():
    data = request.json
    volume_level = data.get('volume')

    try:
        volume_level = int(volume_level)
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        # Set volume level
        volume.SetMasterVolumeLevelScalar(volume_level / 100.0, None)
        return jsonify({"status": "success", "message": "Volume set successfully!"})
    except Exception as e:
        logging.error(f"Failed to set volume. Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint to send bulk emails
@app.route('/send_bulk_email', methods=['POST'])
def send_bulk_email():
    data = request.json
    emails = data.get('emails').split(',')
    subject = data.get('subject')
    message_body = data.get('message')

    for email in emails:
        try:
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = email.strip()
            message["Subject"] = subject
            message.attach(MIMEText(message_body, "plain"))

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, email_password)
            server.sendmail(sender_email, email, message.as_string())
            logging.info(f"Bulk email sent to {email}")
        except Exception as e:
            logging.error(f"Failed to send email to {email}. Error: {str(e)}")
            continue
        finally:
            server.quit()

    return jsonify({"status": "success", "message": "Bulk emails sent successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
