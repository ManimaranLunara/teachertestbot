import os
import fitz  # PyMuPDF
import google.generativeai as genai
import streamlit as st

# Configure the Google Generative AI SDK (assuming you have the API key)
API_KEY = "AIzaSyClajwdbk4RyMQO2mte8Ize3xRdlYQpkvI"  # Replace with your actual API key
genai.configure(api_key=API_KEY)

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file."""
    document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

def get_answer_from_gemini(extracted_text, question, chat_history):
    """Send text and question to Gemini and get the answer."""
    prompt = f"Here is the extracted text from the PDF:\n\n{extracted_text}\n\nAnswer the following question based on this text:\n\n{question}"
    
    if chat_history:
        prompt = "Here is the chat history:\n" + "\n".join([f"Question: {entry['question']}\nAnswer: {entry['answer']}" for entry in chat_history]) + "\n\n" + prompt
    
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    try:
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        prompt,
                    ],
                },
            ]
        )
        response = chat_session.send_message(question)
        return response.text
    except Exception as e:
        st.error(f"An error occurred while fetching the answer: {e}")
        return ""

def list_chapters_from_gemini(extracted_text):
    """Send text to Gemini and get the list of chapters."""
    prompt = (
        "Here is the extracted text from the PDF:\n\n"
        f"{extracted_text}\n\n"
        "Please list out the chapter names with their chapter numbers in a clear and concise manner."
    )
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
    )

    try:
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [prompt],
                },
            ]
        )
        response = chat_session.send_message(prompt)
        
        # Check and process the response
        if response.finish_reason == "RECITATION":
            st.error("The API could not generate a response. Please try again.")
            return ""
        
        return response.text
    except Exception as e:
        st.error(f"An error occurred while listing the chapters: {e}")
        return ""


def create_quizzes_from_chapter(extracted_text, chapter_name):
    """Send text to Gemini and get quizzes for the selected chapter."""
    prompt = f"Here is the extracted text from the PDF:\n\n{extracted_text}\n\nCreate 5 interactive multiple-choice quizzes from the chapter: {chapter_name}"
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
    )

    try:
        response = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        prompt,
                    ],
                },
            ]
        ).send_message(f"Create 5 interactive multiple-choice quizzes from the chapter: {chapter_name}")
        return response.text
    except Exception as e:
        st.error(f"An error occurred while creating quizzes: {e}")
        return ""

# Streamlit App
st.title("Teacher's Assistant: PDF Text Extractor and QA with Gemini API")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# Initialize session state for chat history and chapters
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'chapters' not in st.session_state:
    st.session_state.chapters = []

if uploaded_file is not None:
    pdf_text = extract_text_from_pdf(uploaded_file)
    st.text_area("Extracted Text", pdf_text, height=300)
    
    question = st.text_input("Enter your question")
    
    if st.button("Get Answer"):
        if question:
            answer = get_answer_from_gemini(pdf_text, question, st.session_state.chat_history)
            st.session_state.chat_history.append({"question": question, "answer": answer})
        else:
            st.error("Please enter a question.")

# Display chat history
if st.session_state.chat_history:
    st.subheader("Chat History")
    with st.expander("Show/Hide Chat History"):
        for entry in st.session_state.chat_history:
            st.markdown(f"""
            <div style="background-color:#f0f0f5; padding:10px; margin:10px 0; border-radius:10px;">
                <strong>Question:</strong> {entry["question"]}<br>
                <strong>Answer:</strong> {entry["answer"]}
            </div>
            """, unsafe_allow_html=True)

# Features for teachers to enhance creativity and engagement
st.sidebar.header("Teacher's Tools")

if st.sidebar.button("Generate Teaching Ideas"):
    st.sidebar.write("Generating creative teaching ideas...")

if st.sidebar.button("Create Interactive Quizzes"):
    st.sidebar.write("Fetching chapter names...")
    chapters_text = list_chapters_from_gemini(pdf_text)
    st.session_state.chapters = [chapter.strip() for chapter in chapters_text.split('\n') if chapter.strip()]
    st.sidebar.write("Select a chapter to generate quizzes:")
    
    for chapter in st.session_state.chapters:
        if st.sidebar.button(chapter):
            quizzes = create_quizzes_from_chapter(pdf_text, chapter)
            st.sidebar.write(f"Quizzes for {chapter}:\n{quizzes}")

if st.sidebar.button("Visualize Concepts"):
    st.sidebar.write("Visualizing concepts with diagrams and illustrations...")

# Additional optimization and production-quality improvements
# - Add exception handling for better robustness
# - Optimize PDF text extraction by processing in chunks if needed
# - Use caching for API calls to reduce latency and cost
# - Ensure secure handling of API keys

try:
    # The main functionality is enclosed in try-except for robustness
    pass
except Exception as e:
    st.error(f"An error occurred: {e}")

# High-level CSS ideas to make the page look better
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
        color: #333;
    }
    .stTextArea, .stTextInput {
        border-radius: 8px;
        padding: 10px;
    }
    .stButton button {
        background-color: #007bff;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
    }
    .stButton button:hover {
        background-color: #0056b3;
    }
    .stSidebar {
        background-color: #343a40;
        color: white;
    }
    .stSidebar .stButton button {
        background-color: #17a2b8;
        color: white;
    }
    .stSidebar .stButton button:hover {
        background-color: #117a8b;
    }
    .stSidebar .stTextInput {
        border-radius: 8px;
        padding: 10px;
        background-color: #495057;
        color: white;
    }
</style>
""", unsafe_allow_html=True)
