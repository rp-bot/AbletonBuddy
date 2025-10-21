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
from utils.message_formatter import (
    filter_messages_for_display,
    get_conversation_summary,
)

# Import config to enable database persistence (imported for side effects)
import config  # noqa: F401


def get_or_create_thread() -> marvin.Thread:
    """
    Prompt user to resume an existing thread or create a new one.

    Returns:
        marvin.Thread: The selected or newly created thread
    """
    print("\n🔍 Thread Options:")
    print("1. Start a new conversation")
    print("2. Resume an existing conversation")

    choice = input("\nEnter your choice (1 or 2, default: 1): ").strip()

    if choice == "2":
        thread_id = input("Enter thread ID to resume: ").strip()
        if thread_id:
            try:
                thread = marvin.Thread(id=thread_id)
                messages = thread.get_messages()

                if messages:
                    print(f"\n✅ Resumed thread: {thread_id}")
                    print(
                        f"📝 Conversation summary: {get_conversation_summary(messages)}"
                    )
                    print(f"💬 Total messages: {len(messages)}")

                    # Show recent conversation
                    print("\n📜 Recent conversation:")
                    filtered = filter_messages_for_display(
                        messages[-6:]
                    )  # Last 3 exchanges
                    for msg in filtered:
                        role_emoji = "🎹" if msg["role"] == "user" else "🎵"
                        print(
                            f"  {role_emoji} {msg['role'].title()}: {msg['content'][:80]}..."
                        )

                    return thread
                else:
                    print(
                        f"⚠️  Thread {thread_id} exists but has no messages. Starting fresh with this thread."
                    )
                    return thread
            except Exception as e:
                print(f"❌ Could not load thread: {e}")
                print("Creating a new thread instead.")

    # Create new thread
    thread = marvin.Thread()
    print(f"\n✅ Created new thread: {thread.id}")
    print("💡 Tip: Save this ID to resume this conversation later!")

    return thread


def main():
    """
    Main CLI chat interface with the orchestrator agent.
    """
    print("🎵 Welcome to Ableton Pal!")
    print("Chat with the orchestrator agent. Type 'quit' or 'exit' to end the session.")
    print("-" * 50)

    # Get or create a thread for conversation context (with resumption support)
    thread = get_or_create_thread()
    print("-" * 50)

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

                thread.add_messages(
                    [
                        AgentMessage(
                            content=f"Disambiguation Agent: {disambiguated_input}"
                        )
                    ]
                )

                # Check if the input is still ambiguous and needs clarification
                if is_ambiguous_input(disambiguated_input):
                    # Handle ambiguous input by asking user for clarification
                    clarification_message = handle_ambiguous_input(disambiguated_input)
                    thread.add_messages(
                        [
                            AgentMessage(
                                content=f"Summarization Agent: {clarification_message}"
                            )
                        ]
                    )
                    continue  # Skip processing and wait for user's next input

                # Classify the user input
                api_categories = classify_user_input(disambiguated_input)
                thread.add_messages(
                    [AgentMessage(content=f"Classification Agent: {api_categories}")]
                )
                user_requests = extract_user_request(
                    disambiguated_input, api_categories
                )
                thread.add_messages(
                    [AgentMessage(content=f"Extraction Agent: {user_requests}")]
                )
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
                        thread.add_messages(
                            [
                                AgentMessage(
                                    content=f"Task Successful:\n-{task.id}\n-{task.name}\n-{task.result}\n-{task.tools}\n-{task.state.value}"
                                )
                            ]
                        )
                    elif task.is_skipped:
                        task_results["skipped"].append(task)
                        thread.add_messages(
                            [
                                AgentMessage(
                                    content=f"Task Skipped:\n-{task.id}\n-{task.name}\n-{task.result}\n-{task.tools}\n-{task.state.value}"
                                )
                            ]
                        )
                    elif task.is_failed:
                        task_results["failed"].append(task)
                        thread.add_messages(
                            [
                                AgentMessage(
                                    content=f"Task Failed:\n-{task.id}\n-{task.name}\n-{task.result}\n-{task.tools}\n-{task.state.value}"
                                )
                            ]
                        )
                    task_results["total"] += 1
                # Summarize and display results to user
                summarized_results = summarize_thread(thread)
                thread.add_messages(
                    [AgentMessage(content=f"Summarization Agent: {summarized_results}")]
                )

                # Display only the clean summary to the user
                print(f"\n🎵 Assistant: {summarized_results}")

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
