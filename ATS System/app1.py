from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import pdf2image
import google.generativeai as genai
import io
import base64
import fitz 

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response=model.generate_content([input, pdf_content[0], prompt])
    return response.text

# now to convert the uploaded pdf file into img that gemini pro can understant it and process it
# def input_pdf_setup(uploaded_pdf):
#     if uploaded_pdf is not None:
#         images = pdf2image.convert_from_bytes(uploaded_pdf.read()) # convet pdf to image
#         first_page = images[0]

#         # t convert into bytes
#         img_byte_arr = io.BytesID()
#         first_page.save(img_byte_arr, format='JPEG')
#         img_byte_arr = img_byte_arr.getvalue()

#         pdf_parts = [ 
#             {
#                 "mime_type":"image/jpeg",
#                 "data": base64.b64encode(img_byte_arr).decode() # encode to base64

#             }
#         ]

#         return pdf_parts
#     else:
#         raise FileNotFoundError("File not Uploaded")

def input_pdf_setup(uploaded_pdf):
    if uploaded_pdf is not None:
        doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
        
        # Convert the first page to an image (0-indexed)
        first_page = doc.load_page(0)  
        pix = first_page.get_pixmap()  
        
        # Convert pixmap to bytes (no need to save the image)
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
        raise FileNotFoundError("File not Uploaded")



#-------------- streamlit app -----------------

#-------------- Streamlit App -----------------

st.set_page_config(page_title="ATS System")

# Sidebar: Upload Resume, File Upload Success, and Buttons for Prompts
with st.sidebar:
    
    field = st.text_input("Enter your job filed")

    uploaded_file = st.file_uploader("Upload your Resume", type=["pdf"])

    if uploaded_file is not None:
        st.toast("File uploaded successfully!", icon="✅")
        
    
    submit1 = st.button("Tell me about the resume")
    submit4 = st.button("How much is the percentage match?")

# Main Area: Job Description and Bot Response
st.header("ATS System - Resume Evaluation")

input_text = st.text_area("Job Description:", key="input")


# Define Prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager and an expert in {field}, your task is to review the provided resume  against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt4 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of {field} and ATS functionality, 
your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
the job description. First, the output should come as percentage, then keywords missing, and last final thoughts.
"""

# Handle button clicks and generate responses
if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt1, pdf_content, input_text)
        st.markdown(
            f"""
            <div style="background-color:#f0f0f0; padding: 15px; border-radius: 8px; margin-top: 20px;">
                <h3>Response:</h3>
                <p>{response}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.write("Please upload your Resume.")

if submit4:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt4, pdf_content, input_text)
        st.markdown(
            f"""
            <div style="background-color:#f0f0f0; padding: 15px; border-radius: 8px; margin-top: 20px;">
                <h3>Response:</h3>
                <p>{response}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.write("Please upload your Resume.")