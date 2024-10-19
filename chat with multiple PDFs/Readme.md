2. Activate the Virtual Environment
On macOS/Linux:

bash
Copy code
source venv/bin/activate
On Windows:

bash
Copy code
venv\Scripts\activate
3. Install the Required Dependencies
Once the environment is activated, install the necessary packages using:

bash
Copy code
pip install -r requirements.txt
4. Set Up the .env File
Create a .env file in the root directory of the project and add your OpenAI API key like this:

bash
Copy code
OPENAI_API_KEY=your_openai_key_here
5. Run the Streamlit App
You can now run the Streamlit app with the following command:

bash
Copy code
streamlit run app.py
Live Demonstration
You can check out the live version of the application here.
