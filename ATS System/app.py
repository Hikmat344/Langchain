from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import pdf2image
import google.generativeai as genai
import io
import base64
import fitz
import re

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, pdf_content, prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([input, pdf_content[0], prompt])
        return response.text
    except Exception as e:
        st.error(f"Error in generating response: {str(e)}")
        return ""

def input_pdf_setup(uploaded_pdf):
    try:
        if uploaded_pdf is not None:
            doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")

            # Convert the first page to an image (0-indexed)
            first_page = doc.load_page(0)
            pix = first_page.get_pixmap()

            # Convert pixmap to bytes
            img_byte_arr = io.BytesIO()
            img_byte_arr.write(pix.tobytes("jpeg"))
            img_byte_arr.seek(0)  # Go to the start of the byte stream

            # Encode the image to base64
            pdf_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr.read()).decode()  # Encode to base64
                }
            ]
            return pdf_parts
        else:
            raise FileNotFoundError("No file uploaded")
    except Exception as e:
        st.error(f"Error processing PDF file: {str(e)}")
        return []

def extract_percentage(response):
    try:
        match = re.search(r'(\d+(\.\d+)?)%', response)
        if match:
            return float(match.group(1))
        return 0.0
    except Exception as e:
        st.error(f"Error extracting percentage: {str(e)}")
        return 0.0

#-------------- Streamlit App -----------------

st.set_page_config(page_title="ATS System")

with st.sidebar:
    field = st.text_input("Enter your job field")

    # Upload multiple resumes
    uploaded_files = st.file_uploader("Upload Resumes (multiple)", type=["pdf"], accept_multiple_files=True)

    if uploaded_files:
        st.toast(f"{len(uploaded_files)} files uploaded successfully!", icon="✅")

    submit1 = st.button("Tell me about the resumes")
    submit4 = st.button("How much is the percentage match?")

st.header("ATS System - Resume Evaluation")

input_text = st.text_area("Job Description:", key="input")

input_prompt1 = f"""
You are an experienced Technical Human Resource Manager and an expert in {field}, your task is to review the provided resume  against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt4 = f"""
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of {field} and ATS functionality, 
your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
the job description. First, the output should come as percentage, then keywords missing, and last final thoughts.
"""

comparison_results = []

if submit1 or submit4:
    if uploaded_files:
        if not input_text:
            st.error("Please! provide the job description")
        if not field:
            st.error("Please! Enter your field of job")
        for uploaded_file in uploaded_files:
            pdf_content = input_pdf_setup(uploaded_file)

            if pdf_content:  # Only proceed if PDF content is valid
                if submit1:
                    response = get_gemini_response(input_prompt1, pdf_content, input_text)
                elif submit4:
                    response = get_gemini_response(input_prompt4, pdf_content, input_text)

                if response:
                    comparison_results.append({
                        "file_name": uploaded_file.name,
                        "response": response
                    })

        if comparison_results:
            for result in comparison_results:
                st.markdown(
                    f"""
                    <div style="background-color:#f0f0f0; padding: 15px; border-radius: 8px; margin-top: 20px;">
                        <h3>{result['file_name']}</h3>
                        <p>{result['response']}</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

            if submit4:
                try:
                    best_match = max(
                        comparison_results, 
                        key=lambda x: extract_percentage(x['response'])
                    )
                    st.markdown(
                        f"""
                        <div style="background-color: #d3f8d3; padding: 15px; border-radius: 8px; margin-top: 20px; color: black;">
                            <h3><strong>Best Match:</strong> {best_match['file_name']}</h3>
                            <p>{best_match['response']}</p>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                except ValueError:
                    st.error("Could not extract a valid percentage match.")
        else:
            st.write("No valid responses generated.")
    else:
        st.write("Please upload at least one resume.")
