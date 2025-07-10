import streamlit as st
from chatbot_langchain import ask_question
from main_pipeline import process_url
from suggestion_engine import suggest_questions

st.set_page_config(page_title="Universal Web KG Chatbot")

st.title("🌐 Universal Web KG Chatbot")

url = st.text_input("Enter a website URL to analyze:", "")
if st.button("Process URL"):
    with st.spinner(f"Processing {url}..."):
        process_url(url)
    st.success("Knowledge Graph updated!")

question = st.text_input("Ask a question based on the website:")
if st.button("Ask"):
    if question:
        answer = ask_question(question)
        st.markdown("#### 💬 Answer:")
        st.write(answer)

if st.button("Suggest Questions"):
    suggestions = suggest_questions()
    st.markdown("#### 🤖 Suggested Questions:")
    for s in suggestions:
        st.write("- " + s)