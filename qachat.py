from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from lime.lime_text import LimeTextExplainer
import numpy as np

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=google_api_key)
model = genai.GenerativeModel("gemini-pro") 

chat = model.start_chat(history=[])

def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    return response


def explain_response(text):
    explainer = LimeTextExplainer()

    def predict_proba(texts):
   
        vocabulary = set(' '.join(texts).split())
  
        word_to_index = {word: idx for idx, word in enumerate(vocabulary)}
       
        one_hot_vectors = np.zeros((len(texts), len(vocabulary)))
    
        for i, text in enumerate(texts):
            for word in text.split():
                if word in word_to_index:
                    one_hot_vectors[i, word_to_index[word]] = 1
        return one_hot_vectors

  
    explanation = explainer.explain_instance(text, classifier_fn=predict_proba)
    return explanation


st.set_page_config(page_title="Q&A Demo")


st.header("LLM based chatbot - An explainable AI project")


input_question = st.text_input("Input: ", key="input")


submit_button = st.button("Ask the question")


if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []


if submit_button and input_question:

    response = get_gemini_response(input_question)
  
 
    st.session_state['chat_history'].append(("You", input_question))
    

    st.subheader("The Response is")
    for chunk in response:
        st.write(chunk.text)
        st.session_state['chat_history'].append(("Bot", chunk.text))
        

    st.subheader("Explanation")
    lime_explanation = explain_response(response.text)
    

    st.subheader("Feature Importance for Response:")
    for feature, importance in lime_explanation.as_list():
        st.write(f"{feature}: {importance}")


    explanation_html = lime_explanation.as_html()
    st.subheader("Explanation Visualization for Response:")
    st.components.v1.html(explanation_html)
    

st.subheader("The Chat History is")
for role, text in st.session_state['chat_history']:
    st.write(f"{role}: {text}")
