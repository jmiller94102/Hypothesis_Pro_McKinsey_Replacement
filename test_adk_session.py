"""
Test script to interact with the strategic consultant agent via ADK.
This will create a session trace visible in the ADK dev UI.
"""
from strategic_consultant_agent import root_agent

# Create a session with a strategic question
user_input = "Should we scale deployment of our Computer Vision Fall Detection system in Senior Living facilities?"

print(f"Testing agent with question: {user_input}\n")
print("=" * 80)

try:
    # Run the agent with the user input
    result = root_agent.run(user_input=user_input)

    print("\n" + "=" * 80)
    print("AGENT RESPONSE:")
    print("=" * 80)
    print(result)
    print("\n" + "=" * 80)
    print("\nSession created! Check the ADK dev UI at http://localhost:3002/dev-ui/")
    print("=" * 80)

except Exception as e:
    print(f"\nError running agent: {e}")
    import traceback
    traceback.print_exc()
