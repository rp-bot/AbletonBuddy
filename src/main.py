"""
Ableton Pal - CLI chat interface with Marvin orchestrator agent.
"""

import marvin
from agents import (
    classify_user_input,
    extract_user_request,
    remove_ambiguity,
    is_ambiguous_input,
    handle_ambiguous_input,
    create_and_execute_tasks,
    summarize_thread,
)
from marvin.engine.llm import UserMessage, AgentMessage
import json


def main():
    """
    Main CLI chat interface with the orchestrator agent.
    """
    print("🎵 Welcome to Ableton Pal!")
    print("Chat with the orchestrator agent. Type 'quit' or 'exit' to end the session.")
    print("-" * 50)

    # Create the orchestrator agent
    # orchestrator = create_orchestrator_agent()

    # Create a thread for conversation context
    thread = marvin.Thread()

    try:
        while True:
            # Get user input
            user_input = input("\nYou: ").strip()

            # Check for exit commands
            if user_input.lower() in ["quit", "exit", "bye", "goodbye"]:
                print("\n👋 Goodbye! Thanks for using Ableton Pal!")
                break

            # Skip empty inputs
            if not user_input:
                continue

            try:
                thread.add_messages([UserMessage(content=user_input)])
                # Remove ambiguity from user input first
                disambiguated_input = remove_ambiguity(user_input)

                thread.add_messages([AgentMessage(content=f"Disambiguation Agent: {disambiguated_input}")])

                # Check if the input is still ambiguous and needs clarification
                if is_ambiguous_input(disambiguated_input):
                    # Handle ambiguous input by asking user for clarification
                    clarification_message = handle_ambiguous_input(disambiguated_input)
                    thread.add_messages([AgentMessage(content=clarification_message)])
                    continue  # Skip processing and wait for user's next input

                # Classify the user input
                api_categories = classify_user_input(disambiguated_input)
                thread.add_messages([AgentMessage(content=f"Classification Agent: {api_categories}")])
                user_requests = extract_user_request(
                    disambiguated_input, api_categories
                )
                thread.add_messages([AgentMessage(content=f"Extraction Agent: {user_requests}")])
                # Create and execute tasks
                tasks = create_and_execute_tasks(user_requests, thread)
                task_results = {
                    "successful": [],
                    "failed": [],
                    "skipped": [],
                    "total": 0,
                }
                # Execute all tasks
                for task in tasks:
                    task.run()
                    if task.is_complete:
                        
                        task_results["successful"].append(task)
                        thread.add_messages([AgentMessage(content=f"Task Successful: {task.id}\n{task.name}\n{task.result}\n{task.state}")])
                    elif task.is_skipped:
                        task_results["skipped"].append(task)
                        thread.add_messages([AgentMessage(content=f"Task Skipped: {task.id}\n{task.name}\n{task.result}\n{task.state}")])
                    elif task.is_failed:
                        task_results["failed"].append(task)
                        thread.add_messages([AgentMessage(content=f"Task Failed: {task.id}\n{task.name}\n{task.result}\n{task.state}")])
                    task_results["total"] += 1
                # Add the task results to the thread    
                summarized_results = summarize_thread(thread)
                thread.add_messages([AgentMessage(content=f"Summarization Agent: {summarized_results}")])

                # output the thread messages to a json file
                with open("thread_messages.json", "w") as f:
                    thread_messages = thread.get_messages()
                    # Convert Message objects to dictionaries
                    serializable_messages = []
                    for msg in thread_messages:
                        # Extract content from the message parts
                        content = ""
                        if hasattr(msg.message, 'parts'):
                            for part in msg.message.parts:
                                if hasattr(part, 'content'):
                                    content += part.content + " "
                        
                        serializable_messages.append({
                            "id": str(msg.id),
                            "thread_id": msg.thread_id,
                            "created_at": msg.created_at.isoformat(),
                            "message_type": type(msg.message).__name__,
                            "content": content.strip()
                        })
                    json.dump(serializable_messages, f, indent=4)

            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again or type 'quit' to exit.")

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for using Ableton Pal!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please restart the application.")


if __name__ == "__main__":
    main()
