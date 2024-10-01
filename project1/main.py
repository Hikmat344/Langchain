import os
from constants import openai_key
from langchain.llms import OpenAI
import streamlit as st
from langchain.schema import HumanMessage, SystemMessage , AIMessage
from langchain.chat_models import ChatOpenAI

from langchain import PromptTemplate
from langchain.chains import LLMChain # responsible for executing every prompt template
from langchain.chains import SequentialChain # to combine multiple prompt templates, simplsesenquential chain problem is that it only give the last prompt output


from langchain.memory import ConversationBufferMemory # to memorise the conversation of llm


os.environ["OPENAI_API_KEY"]=openai_key

st.set_page_config(page_title="Symptoms Analysis Chatbot")
st.header("Symptoms Analysis Chatbot")

input_text = st.text_input("search the topic here")

# initialize llm from openai
llm = OpenAI(temperature = 0.8) # temperature to give hoe much controll llm to give good outputs

# if input_text:
#     st.write(llm(input_text))

#___________Promt template _________________

first_input_prompt=PromptTemplate(
    input_variables=['name'],
    template = "tell me about{name}"
)

#____________________ Memory   _____________

person_memory = ConversationBufferMemory(input_key='name' , memory_key='chat_history')
dob_memory = ConversationBufferMemory(input_key='person' , memory_key='chat_history')
descr_memory = ConversationBufferMemory(input_key='dob' , memory_key='description_history')

#now to execute every promt template we need llm chain , so we will create llm chain for every single prompt template

chain = LLMChain(llm=llm , prompt=first_input_prompt, verbose=True , output_key='person' , memory=person_memory)

#_____________to make multiple prompt templates  _____________

second_input_prompt=PromptTemplate(
    input_variables=['person'],
    template = "when the {person} was born"
)

# now llm chain to run this prompt template
chain2 = LLMChain(llm=llm , prompt=second_input_prompt, verbose=True , output_key='dob' , memory=dob_memory)

# to combine the all prompt templates

parent_chain = SequentialChain(chains=[chain , chain2], input_variables=['name'] , output_variables=['person','dob'], verbose=True)

#to run this prompt template

if input_text:
    st.write(parent_chain({'name':input_text})) #instead .run, use key value

    with st.expendor('person Name'): 
        st.info(person_memory.buffer) # to show memories after output
