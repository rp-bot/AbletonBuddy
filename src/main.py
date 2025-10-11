"""
Ableton Pal - CLI chat interface with Marvin orchestrator agent.
"""
import marvin
from src.agents import create_orchestrator_agent


def main():
    """
    Main CLI chat interface with the orchestrator agent.
    """
    print("🎵 Welcome to Ableton Pal!")
    print("Chat with the orchestrator agent. Type 'quit' or 'exit' to end the session.")
    print("-" * 50)

    # Create the orchestrator agent
    orchestrator = create_orchestrator_agent()

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
                # Get response from orchestrator
                response = orchestrator.say(user_input, thread=thread)
                print(f"\nOrchestrator: {response}")

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
