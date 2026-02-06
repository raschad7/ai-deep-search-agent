import asyncio # Import asyncio
from fastapi import APIRouter
from backend.api.schema import ChatRequest, ChatResponse
from backend.services.search_service import get_search_results
from backend.services.llm_service import generate_content, decide_search_status, summarize_text

chat_router = APIRouter()

@chat_router.post("/deep_searcher", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest): # Added 'async'
    user_input = request.query
    chat_history = request.history
    print(f"the topic or question is : {user_input}")

    # Decision maker (Added await)
    decision = await decide_search_status(user_input)
    
    response_text = ""
    
    if decision == "SEARCH":
        print("the system will route to Search...")
        # Note: get_search_results is still sync, which is fine for now
        raw_results = get_search_results(user_input)
        
        if raw_results:
            print(f" Found {len(raw_results)} sources. Summarizing in PARALLEL...")
            summarized_data = ""
            
            # START PARALLEL PROCESSING
            # Create a list of tasks
            tasks = []
            for res in raw_results:
                print(f" Queuing Source {res['source_id']} for summary...")
                # We pass the function call to the list, but don't await it yet
                tasks.append(summarize_text(res['content'], user_input))
            
            # Run all tasks at the same time
            summaries = await asyncio.gather(*tasks)
            # END PARALLEL PROCESSING 
            
            # Assemble the data
            for i, summary in enumerate(summaries):
                res = raw_results[i]
                print(f"\n--- SUMMARY FOR SOURCE {res['source_id']} ---\n{summary[:100]}...\n") # Print first 100 chars
                
                summarized_data += f"--- Source {res['source_id']} ({res['url']}) ---\n"
                summarized_data += f"{summary}\n\n"
            
            print(" Generating final answer...")
            # Added await
            response_text = await generate_content(
                user_input, 
                context_data=summarized_data, 
                history= chat_history)
            
        else:
            response_text = "I couldn't find any relevant results online."
    else:
        print("the system will route to normal llm...")
        # Added await
        response_text = await generate_content(user_input,history=chat_history)

    return ChatResponse(
        reply=response_text,
        router_decision=decision
    )