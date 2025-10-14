"""
Ableton Pal - CLI chat interface with Marvin orchestrator agent.
"""
import marvin
from agents import classify_user_input, extract_user_request, remove_ambiguity, is_ambiguous_input, handle_ambiguous_input, create_and_execute_tasks
from marvin.engine.llm import UserMessage, AgentMessage

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
            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                print("\n👋 Goodbye! Thanks for using Ableton Pal!")
                break

            # Skip empty inputs
            if not user_input:
                continue

            try:
                thread.add_messages(
                    [UserMessage(content=user_input)]
                )
                # Remove ambiguity from user input first
                disambiguated_input = remove_ambiguity(user_input, thread)

                # Check if the input is still ambiguous and needs clarification
                if is_ambiguous_input(disambiguated_input):
                    # Handle ambiguous input by asking user for clarification
                    clarification_message = handle_ambiguous_input(disambiguated_input)
                    print(f"\n🤔 {clarification_message}")
                    continue  # Skip processing and wait for user's next input
                
                # Classify the user input
                api_categories = classify_user_input(disambiguated_input, thread)
                user_requests = extract_user_request(disambiguated_input, api_categories, thread)

                # Create and execute tasks
                create_and_execute_tasks(user_requests)

                print(f"\nUser Requests: {user_requests}")

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
