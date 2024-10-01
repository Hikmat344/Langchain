from langchain import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain

demo_template = '''I want tou to act as a medical specialist, and do symptoms analysis on given {symptoms} 
and then tell the user that what disease he/she have and also sugest the cure for it'''

prompt = PromptTemplate(
    input_variables=['symptoms'],
    template = demo_template
)

# prompt.format(symptoms='headchae, flew , cough') # to check the how format looks in our given prompt


llm = OpenAI(temperature = 0.7)
chain = LLMChain(llm = llm , prompt = prompt)

chain.run('headchae, flew , cough')