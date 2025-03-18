from dotenv import load_dotenv
import streamlit as st
import os
import PyPDF2 as pdf
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Set your API Key
os.environ['GOOGLE_API_KEY'] = "AIzaSyCgswykmyaEWSVElC6K13zAGdKafgamCGM"  # Replace with your API key

# Configure the Google Generative AI API
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

# Function to call Gemini API and get the response
def get_gemini_response(prompt, content):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(f"{prompt}\n\n{content}")
    return response.text

# Function to extract text from the uploaded PDF file
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page_obj = reader.pages[page]
        text += page_obj.extract_text()
    return text

# Streamlit App Interface

st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

# Input fields for job description and file upload
input_text = st.text_area("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

# Display success message once the file is uploaded
if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

# Submit buttons for the actions
submit1 = st.button("Tell Me About the Resume")
submit3 = st.button("Percentage Match")

# Input prompts for the Gemini API
input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
Your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
the job description. First, the output should come as a percentage, then keywords missing, and last final thoughts.
"""

# Handle button actions
if submit1:
    if uploaded_file is not None and input_text:
        pdf_content = input_pdf_text(uploaded_file)
        response = get_gemini_response(input_prompt1, pdf_content)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload the resume and provide the job description")

elif submit3:
    if uploaded_file is not None and input_text:
        pdf_content = input_pdf_text(uploaded_file)
        response = get_gemini_response(input_prompt3, pdf_content)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.write("Please upload the resume and provide the job description")
