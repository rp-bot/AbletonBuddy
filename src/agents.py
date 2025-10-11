"""
Marvin agent definitions for the Ableton Pal system.
"""
import marvin
from typing import List

# Import tools for future use
from src.tools.osc.song_tools import query_ableton, control_ableton, test_connection


def create_orchestrator_agent() -> marvin.Agent:
    """
    Create the orchestrator agent that coordinates user requests and delegates to specialized agents.
    """
    return marvin.Agent(
        name="Orchestrator",
        instructions="""
        You are the Orchestrator agent for Ableton Pal, a system that helps users interact with Ableton Live.
        
        Your role is to:
        1. Understand user requests and determine what they want to do
        2. Coordinate with specialized agents when needed
        3. Provide helpful responses about music production and Ableton Live
        4. Guide users on how to use the system effectively
        
        You can help with:
        - General questions about music production
        - Ableton Live workflow guidance
        - Understanding what the system can do
        - Coordinating with specialized agents for specific tasks
        
        Be friendly, helpful, and knowledgeable about music production and Ableton Live.
        If a user asks about controlling Ableton Live directly, let them know that functionality
        will be available through the Song Agent in future versions.
        """,
        description="Coordinates user requests and delegates to specialized agents for Ableton Live control"
    )


def create_song_agent() -> marvin.Agent:
    """
    Create the song agent that handles Ableton Live control via OSC tools.
    This is a skeleton for future implementation.
    """
    return marvin.Agent(
        name="Song Agent",
        instructions="""
        You are the Song Agent for Ableton Pal, specialized in controlling Ableton Live.
        
        Your role is to:
        1. Execute Ableton Live commands via OSC
        2. Query Ableton Live session information
        3. Help users with specific Ableton Live operations
        4. Provide feedback on Ableton Live state and operations
        
        Available tools:
        - query_ableton: Get information about the current session
        - control_ableton: Execute commands in Ableton Live
        - test_connection: Verify connection to Ableton Live
        
        Always check connection status before attempting operations.
        Provide clear feedback about what operations were performed.
        """,
        description="Handles Ableton Live control via OSC tools",
        tools=[query_ableton, control_ableton, test_connection]
    )


def get_available_agents() -> List[marvin.Agent]:
    """
    Get a list of all available agents in the system.
    """
    return [
        create_orchestrator_agent(),
        create_song_agent()
    ]
