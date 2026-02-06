import os
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Summarizer
async def summarize_text(text, query):
    """
    Summarizes raw text to extract facts relevant to the query.
    """
    system_prompt = """
    # Role
    You are an expert text summarizer. 
    
    # Task
    You will receive a large text and a specific user query. Your goal is to generate a summary that answers the query using ONLY the provided text.

    # Guidelines
    1. **Relevance:** Focus strictly on facts and details relevant to the user's query.
    2. **Conciseness:** Keep the summary concise and to the point.
    3. **Length:** Ensure the total length is under 300 words.
    4. **Formatting:** Use a mix of paragraphs for context and bullet points for listing facts/features.
    5. **Flow:** Maintain the logical flow of the original article.
    6. **Cleanliness:** Completely remove ads, navigation menus, fluff, and irrelevant content.
    7. **Grounding:** Do NOT add any external knowledge or extra content. Summarize only what is provided in the text.
    """
    
    user_message = f"""
    USER QUERY: {query}
    
    RAW TEXT:
    {text[:15000]}
    """

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3
        )
        content = response.choices[0].message.content
        return content.strip() if content else "No response generated."
    except Exception as e:
        return f"Error summarizing: {e}"

# Unified Content Generator
async def generate_content(user_query, context_data=None, history=[]):
    """
    Generates a response using the LLM. 
    If context_data is provided, it acts as a research assistant using that data.
    If context_data is None, it acts as a standard helpful assistant.
    """
    if context_data:
        system_prompt = """
        # Role
        You are a helpful and skilled Research Assistant.

        # Task
        Your task is to provide a comprehensive answer to the user's query based ONLY on the provided search results.

        # Instructions
        - **Tone:** Be professional but conversational. Write naturally, as if  explaining the topic to a smart friend. Avoid robotic language or repetitive phrases.
        
        - **Format:** Structure your answer as a clean, readable article. Use Markdown Headers (##) to separate distinct topics and clear paragraphs for explanations. Use bullet points only when listing facts or steps.
        
        - **Accuracy:** Ground your answer strictly in the provided text. Do not make up information.
        
        - **Context:** If the conversation history provides context (like answering "Who is he?"), use it.
        
        - **Irrelevance:** If the provided search results do not contain the answer, state clearly that you couldn't find specific information.
        """
        final_user_content = f"USER QUESTION: {user_query}\n\nRESEARCH DATA:\n{context_data}"
        
        temperature = 0.3
    else:
        print(" Chatting directly to llm")
        system_prompt = """You are a helpful AI assistant."""
        final_user_content = user_query
        temperature = 1.0

    messages_payload = [{"role": "system", "content": system_prompt}]
    for msg in history:
        # We access .role and .content because 'msg' is a Pydantic object
        messages_payload.append({"role": msg.role, "content": msg.content})

    # Add the Current User Message (The "New" turn)
    messages_payload.append({"role": "user", "content": final_user_content})


    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_payload, #type: ignore
            temperature=temperature
        )
        content = response.choices[0].message.content
        return content.strip() if content else "No response generated."
        
    except Exception as e:
        return f"Error: {e}"

# Router Decision Maker
async def decide_search_status(query):
    print(" Deciding if search is needed...")
    
    system_prompt = """
    # Role
    You are an intelligent query router.

    # Task
    Classify the incoming user query into one of two categories based on whether it requires external information.

    # Instructions
    - **SEARCH:** Choose this for questions about current events, breaking news, weather, dynamic facts, or technical documentation (e.g., "GTA 6 release date", "Stock price of Apple", "Latest Python version").
    - **NO_SEARCH:** Choose this for greetings, established general knowledge, creative writing, coding help, or philosophical questions (e.g., "Hello", "Write a poem", "What is the capital of France?").
    - **Output:** Reply ONLY with the word 'SEARCH' or 'NO_SEARCH'. Do not provide explanations or extra text.
    """    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.0 
        )
        content = response.choices[0].message.content
        if content is None:
            return "NO_SEARCH"
        decision = content.strip().upper()
        
        # Safety check: if LLM talks too much, force a decision
        if "SEARCH" in decision and "NO" not in decision:
            return "SEARCH"
        return "NO_SEARCH"
        
    except Exception as e:
        print(f"Router Error: {e}")
        return "NO_SEARCH" 
    
    
    