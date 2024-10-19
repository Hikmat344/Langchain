# PDF Chatbot with Multiple Resume Comparison

This project is a Streamlit-based chatbot that allows users to upload multiple PDF resumes and compare them against a job description to determine the best match. It uses OpenAI's API to analyze the resumes and provide relevant insights.

## Features
- Upload multiple PDF resumes
- Chatbot functionality to answer queries based on resume content
- Compare resumes against a job description

## How to Run the Project

Follow these steps to set up and run the project locally.

### 1. Create a Virtual Environment

First, create a virtual environment to isolate your project's dependencies:

```bash
python -m venv venv
```

### 2. Activate the Virtual Environment
- On macOS/Linux:

```bash
source venv/bin/activate
```
- On Windows:

``` bash
venv\Scripts\activate
```
## 3. Install the Required Dependencies
- Once the environment is activated, install the necessary packages using:

```bash
pip install -r requirements.txt
```
## 4. Set Up the .env File
- Create a .env file in the root directory of the project and add your OpenAI API key like this:

```bash
OPENAI_API_KEY=your_openai_key_here
```
## 5. Run the Streamlit App
- You can now run the Streamlit app with the following command:

```bash
streamlit run app.py
```
## Live Demo
You can check out the live version of the application here.
