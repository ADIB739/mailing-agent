from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType
from langchain.schema import SystemMessage
import os
from dotenv import load_dotenv
from gmail_tool import send_email_tool
from search_tool import web_search_tool

load_dotenv()

def run_agent(user_input):
    llm = ChatGroq(
        temperature=0,
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    system_message = SystemMessage(content="""
You are a helpful assistant that can send emails and search the web for information.

**When users ask to send emails:**
- Use send_email_tool with format: "to=email@domain.com; subject=Subject; body=Email content"

**When users ask for information/questions:**
- Use web_search_tool to find current information
- Summarize the search results in a helpful way

**Tools available:**
1. send_email_tool: For sending emails
2. web_search_tool: For searching web information

**Examples:**
- "Send email to john@example.com about meeting" → Use send_email_tool
- "What's the weather in New York?" → Use web_search_tool
- "Tell me about AI trends" → Use web_search_tool
- "Send reminder email to team@company.com" → Use send_email_tool

Always choose the appropriate tool based on the user's request.
""")

    tools = [send_email_tool, web_search_tool]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        max_iterations=3,
        early_stopping_method="generate",
        system_message=system_message
    )

    try:
        response = agent.invoke({"input": user_input})
        print("\n✅ Agent completed!")
        return response
    except Exception as e:
        print(f"❌ Error: {e}")
        return None