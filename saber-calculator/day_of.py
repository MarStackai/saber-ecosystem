import os
from datetime import date
from langchain_openai import OpenAI
from langchain_core.tools import tool

# Updated import to resolve the deprecation warning
from langchain_community.agent_toolkits.load_tools import load_tools

# New imports for the modern way of creating agents
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor

# --- Environment variable setup (make sure your keys are loaded!) ---
# from dotenv import load_dotenv
# load_dotenv()
# os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
# os.environ['SERPAPI_API_KEY'] = os.getenv('SERPAPI_API_KEY')
# -----------------------------------------------------------------------

# --- Step 1: Define our custom tool (This stays the same) ---
@tool
def get_current_date() -> str:
    """
    Use this tool to get the current date. This tool has no inputs.
    Call this tool whenever a question about the current date or day is asked.
    """
    return date.today().isoformat()

# --- Step 2: Initialize the LLM and Tools (This is the same) ---
print("Initializing LLM and loading tools...")
llm = OpenAI(temperature=0)
tools = [
    load_tools(["serpapi"], llm=llm)[0], # We load the tool and take the first element
    get_current_date
]

# --- Step 3: The NEW way to create an agent ---
print("Creating modern agent...")

# First, pull a standard prompt template from the LangChain Hub
# This prompt is specifically designed for this type of "ReAct" agent
prompt = hub.pull("hwchase17/react")

# Next, create the agent by combining the LLM, the tools, and the prompt
agent = create_react_agent(llm, tools, prompt)

# Finally, create the AgentExecutor that will run the agent
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# --- Step 4: Run the Agent Executor ---
print("Agent is ready! Asking a question...")
question = "What day of the week is it today?"

# We use `invoke` with the modern executor
response = agent_executor.invoke({"input": question})

print("\n--- Final Answer ---")
# The final answer is now in the 'output' key of the response dictionary
print(response['output'])