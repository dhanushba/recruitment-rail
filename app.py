from dotenv import load_dotenv
import streamlit as st
import os
import PyPDF2 as pdf
import google.generativeai as genai
import concurrent.futures
import pandas as pd

# Load environment variables
load_dotenv()

# Set API Key
os.environ['GOOGLE_API_KEY'] = ""  # Replace with your API key

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

def get_gemini_response(prompt, content):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(f"{prompt}\n\n{content}")
    return response.text.strip()

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text() or ""
    return text

def process_resume(file, job_desc, prompt):
    resume_text = input_pdf_text(file)
    response = get_gemini_response(prompt, f"Job Description: {job_desc}\nResume: {resume_text}")
    return file.name, response

# Streamlit UI
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

job_desc = st.text_area("Job Description:", key="input")
uploaded_files = st.file_uploader("Upload Resumes (PDF, multiple)", type=["pdf"], accept_multiple_files=True)

submit1 = st.button("Tell Me About the Resumes")
submit3 = st.button("Percentage Match")

table_data = []

input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resumes against the job description. 
Please share your professional evaluation on whether the candidates' profiles align with the role. 
Highlight the strengths and weaknesses of each applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
Your task is to evaluate each resume against the provided job description. Give me a structured output in the format:

Match Percentage: X%
Keywords Matching: keyword1, keyword2, ...
Keywords Lacking: keyword1, keyword2, ...
Final Thoughts: <Your final thoughts>
"""

if submit1 and uploaded_files and job_desc:
    with st.spinner("Processing resumes..."):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(lambda file: process_resume(file, job_desc, input_prompt1), uploaded_files))
        
        for file_name, response in results:
            table_data.append([file_name, response])
        
        df = pd.DataFrame(table_data, columns=["Resume", "Evaluation Report"])
        st.dataframe(df)

elif submit3 and uploaded_files and job_desc:
    with st.spinner("Processing resumes..."):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(lambda file: process_resume(file, job_desc, input_prompt3), uploaded_files))
        
        for file_name, response in results:
            try:
                match_percentage = "N/A"
                keywords_matching = "N/A"
                keywords_lacking = "N/A"
                final_thoughts = "N/A"
                
                for line in response.split("\n"):
                    if "Match Percentage:" in line:
                        match_percentage = line.split(":")[1].strip()
                    elif "Keywords Matching:" in line:
                        keywords_matching = line.split(":")[1].strip()
                    elif "Keywords Lacking:" in line:
                        keywords_lacking = line.split(":")[1].strip()
                    elif "Final Thoughts:" in line:
                        final_thoughts = line.split(":")[1].strip()
                
                table_data.append([file_name, match_percentage, keywords_matching, keywords_lacking])
            except Exception as e:
                st.error(f"Error processing {file_name}: {str(e)}")
        
        df = pd.DataFrame(table_data, columns=["Resume", "Match %", "Keywords Matching", "Keywords Lacking"])
        st.dataframe(df)
        
        # Download report
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Report", data=csv, file_name="ATS_Report.csv", mime="text/csv")
else:
    st.warning("Please upload resumes and provide a job description.")
