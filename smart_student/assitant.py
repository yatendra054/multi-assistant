import validators
from langchain_groq import ChatGroq
from langchain_community.utilities import ArxivAPIWrapper,WikipediaAPIWrapper,SerpAPIWrapper
from langchain_community.tools import ArxivQueryRun,WikipediaQueryRun
from langchain.agents import initialize_agent,AgentType,AgentExecutor
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_community.document_loaders.url import UnstructuredURLLoader
import os
import requests
import json
from pathlib import Path
import re

from dotenv import load_dotenv
load_dotenv()


def handle_llm_model(request,api_key):
    context={}
    
    BASE_DIR = Path(__file__).resolve().parent.parent.parent  
    env_path = BASE_DIR / ".env"
    load_dotenv(dotenv_path=env_path)

    if not api_key:
        context["output"] = "PLEASE SET YOUR GROQ API KEY." 
        return context
    else:
        if request.method=="POST":
            llm=ChatGroq(groq_api_key=api_key,model="Deepseek-R1-Distill-Llama-70b")
            query_type=request.POST.get("query_type")
            if query_type=="search":
                query=request.POST.get("query")
                try:
                    axiv=ArxivQueryRun(api_wrapper=ArxivAPIWrapper(top_k_results=1,doc_content_chars_max=300))
                    wiki=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=1,doc_content_chars_max=300))
                    
                    search = Tool(
                        name="SerpAPI",
                        func=SerpAPIWrapper().run,
                        description="Search the web using SerpAPI"
                    )
                    
                    tools=[axiv,wiki,search]
                    
                    agent=initialize_agent(tools=tools,llm=llm,agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION)
                    
                    agent_response=AgentExecutor.from_agent_and_tools(agent=agent.agent,tools=tools ,handle_parsing_errors=True)
    
                    
                    chat_history = request.session.get("chat_history", [])
                    full_prompt = f"{chat_history}\nUser: {query}\nAssistant:"

                    result = agent_response.run(full_prompt)

                    chat_history.append((query, result))
                    
                    request.session["chat_history"] = chat_history

                    context["output"] = result

                except Exception as e:
                    context["output"]=f"Error {str(e)}"
            elif query_type == "summary":
                def get_video_id(url):
                    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
                    match = re.search(pattern, url)
                    if match:
                        return match.group(1)
                    return None

                def extract_transcript_details(youtube_video_url):
                    try:
                        video_id = get_video_id(youtube_video_url)
                        transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi'])
                        transcript = " ".join([i["text"] for i in transcript_text])
                        return transcript
                    except Exception as e:
                        raise e

                def generate_groq_content(transcript_text, prompt):
                    llm_model = ChatGroq(groq_api_key=api_key, model="Gemma2-9b-it")
                    response = llm_model.invoke(prompt + transcript_text)
                    return response.content

                url = request.POST.get("url")

                prompt = """You are a YouTube video summarizer. You will be taking the transcript text
                and summarizing the entire video and providing the important summary in points
                within 300 words. Please provide the summary of the text given here:  """

                if not validators.url(url):
                    context["output"] = "Invalid URL"
                    return context

                try:
                    summary = None

                    if "youtube.com" in url or "youtu.be" in url:
                        transcript_text = extract_transcript_details(url)
                        if transcript_text:
                            summary = generate_groq_content(transcript_text, prompt)
                        else:
                            context["output"] = "Could not extract transcript."
                            return context
                    else:
                        loader = UnstructuredURLLoader(
                            urls=[url],
                            ssl_verify=False,
                            headers={
                                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
                            }
                        )
                        doc = loader.load()

                        prompt_template = PromptTemplate(
                            template="""
                                Provide a summary of the following content up to 300 words in detail.
                                Content: {text}
                            """,
                            input_variables=["text"]
                        )

                        llm_model = ChatGroq(groq_api_key=api_key, model="Gemma2-9b-it")
                        chain = load_summarize_chain(llm_model, chain_type="stuff", prompt=prompt_template)
                        summary = chain.run(doc)

                    if summary:
                        chat_history = request.session.get("chat_history", [])
                        chat_history.append((url, summary))
                        request.session["chat_history"] = chat_history

                        context["output"] = summary
                        context["chat_history"] = chat_history

                except Exception as e:
                    context["output"] = f"Error: {str(e)}"

            else:
                prompt_response=request.POST.get("code-query")
                
                try:
                    chat_history = request.session.get("chat_history", [])
                   
                    history_prompt = "\n".join([
                        f"User: {q}\nAssistant: {a}" for q, a in chat_history
                    ])
                    
                    full_prompt = f"{history_prompt}\nUser: {prompt_response}\nAssistant:"

                
                    message = llm.invoke(full_prompt)
                    message_content = message.content.strip()

                  
                    chat_history.append((prompt_response, message_content))
                    request.session["chat_history"] = chat_history

                    formatted_history = "\n\n".join([
                        f"User: {q}\nAssistant: {a}" for q, a in chat_history
                    ])
                    context["output"] = message_content
                    context["chat_history_display"] = formatted_history
                           
                except Exception as e:
                    context["output"]=f"Error:{str(e)}"
                    
            
    return context        
                