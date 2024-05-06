from dotenv import load_dotenv
import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import re

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def scrape_contact_info():
    try:
        response = requests.get("https://vit.ac.in/contactus", verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            contact_info = soup.find("div", class_="contact-detail-wrap")
            if contact_info:
                return contact_info.get_text(separator="\n", strip=True)
            else:
                return "Contact information not found."
        else:
            return None
    except Exception as e:
        print("Error:", e)
        return None

def get_gemini_response(question):
    model = genai.GenerativeModel("gemini-pro")
    chat = model.start_chat(history=[])
    response = chat.send_message(question, stream=True)
    response_text = ""
    for chunk in response:
        response_text += chunk.text + "\n"
    return response_text

def scrape_website(url):
    try:
        with requests.get(url, verify=False) as response:
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                return soup.get_text(separator="\n", strip=True)
            else:
                return None
    except Exception as e:
        print("Error:", e)
        return None

st.set_page_config(page_title="Chatbot")
st.title("LLM based Chatbot")

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

input_text = st.text_input("Input: ", key="input")
submit = st.button("Ask the question")

if submit and input_text:
    if "placements" in input_text.lower():
        pass
    elif "admissions" in input_text.lower():
        pass
    elif "overview of vit chennai" in input_text.lower():
        scraped_info = scrape_website("https://chennai.vit.ac.in/")
        st.subheader("Overview of VIT Chennai:")
        st.write(scraped_info)
        st.session_state['chat_history'].append(("Bot", "Here is the overview of VIT Chennai."))
    elif "tips for viteee learning" in input_text.lower():
        scraped_info = scrape_website("https://chennai.vit.ac.in/how-to-prepare-for-engineering-entrance-exam/")
        st.subheader("Tips for VITEEE Learning:")
        st.write(scraped_info)
        st.session_state['chat_history'].append(("Bot", "Here are some tips for VITEEE learning."))
    elif "vit bus routes" in input_text.lower():
        st.subheader("VIT Bus Routes:")
        st.write("You can find VIT bus routes [here](https://chennai.vit.ac.in/files/BUS%20ROUTE%20NEW%20LIST%202023-2024.pdf)")
        st.session_state['chat_history'].append(("Bot", "Here are the VIT bus routes."))
    elif "contact information" in input_text.lower():
        contact_info = scrape_contact_info()
        st.subheader("Contact Information:")
        st.write(contact_info)
        st.session_state['chat_history'].append(("Bot", "Here is the contact information."))
    elif "hostels" in input_text.lower():
        scraped_info = scrape_website("https://chennai.vit.ac.in/campus/hostels/")
        st.subheader("Hostel Information:")
        if scraped_info:
            hostels_list = scraped_info.split("\n")
            hostels_list = [hostel.strip() for hostel in hostels_list if hostel.strip()]
            st.write("\n".join([f"- {hostel}" for hostel in hostels_list]))
        else:
            st.write("Hostel information not found.")
        st.session_state['chat_history'].append(("Bot", "Here is the hostel information."))
    else:
        response = get_gemini_response(input_text)
        st.subheader("Bot's Response:")
        st.write(response)
        st.session_state['chat_history'].append(("You", input_text))
        st.session_state['chat_history'].append(("Bot", response))

st.subheader("Chat History:")
for role, text in st.session_state['chat_history']:
    if role == "Bot":
        st.text_area(role, text, disabled=True)
    else:
        st.text_area(role, text, disabled=False)
