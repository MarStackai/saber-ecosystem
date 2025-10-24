import os
from langchain_openai import OpenAI
from langchain.agents import load_tools, initialize_agent, AgentType

# --- This part is only needed if you haven't set environment variables ---
# from dotenv import load_dotenv
# load_dotenv() 
#
# # Securely load API keys from a .env file
# # Make sure you have a .env file in the same directory with:
# # OPENAI_API_KEY="your_openai_key_here"
# # SERPAPI_API_KEY="your_serpapi_key_here"
# os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
# os.environ['SERPAPI_API_KEY'] = os.getenv('SERPAPI_API_KEY')
# -----------------------------------------------------------------------


# 1. Initialize the LLM
# This is the "brain" of our agent. We're using a model from OpenAI.
# The `temperature` parameter controls creativity. 0 means it will be very factual.
print("Initializing LLM...")
llm = OpenAI(temperature=0)

# 2. Load the Tools
# Tools are the functions the agent can use.
# `serpapi` is for web searches.
# `llm-math` is a special tool that uses the LLM itself to do math.
print("Loading tools...")
tools = load_tools(["serpapi", "llm-math"], llm=llm)

# 3. Initialize the Agent
# We are putting the LLM and the tools together to create the agent.
# `AgentType.ZERO_SHOT_REACT_DESCRIPTION` is a standard agent type.
# "REACT" stands for "Reasoning and Acting". It's a reliable way for the agent
# to think through a problem step-by-step.
# `verbose=True` means the agent will print out its thought process.
print("Initializing Agent...")
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 4. Run the Agent
# Now we can ask our agent questions!
print("Agent is ready! Asking a question...")
question = "First, find the name and age of the current CEO of Google. Once you have their age, calculate that number raised to the power of 0.5."
response = agent.run(question)

print("\n--- Final Answer ---")
print(response)