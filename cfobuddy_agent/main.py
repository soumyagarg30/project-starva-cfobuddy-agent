from dotenv import load_dotenv
load_dotenv()

import datetime
import json

from agentbackend import build_agent
from signals.dashboard import render_signal_board, print_signal_board
from langchain_core.messages import HumanMessage, AIMessage


def main():
    agent = build_agent()
    conversation_history = []

    signal_board = render_signal_board()
    print_signal_board(signal_board)

    print("🧠 CFOBuddy Agent — Type 'exit' to quit\n")

    with open("conversation.log", "a") as log_file:
        log_file.write(
            f"\n--- New Session: {datetime.datetime.now()} ---\n"
        )
        log_file.write("Signal Board:\n")
        log_file.write(
            json.dumps(signal_board, indent=2) + "\n\n"
        )

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() == "exit":
                break

            log_file.write(f"You: {user_input}\n")

            conversation_history.append(
                HumanMessage(content=user_input)
            )

            try:
                result = agent.invoke({
                    "messages": conversation_history
                })

                response = result["messages"][-1].content

                print(f"\nCFOBuddy: {response}\n")

                log_file.write(f"CFOBuddy: {response}\n\n")

                conversation_history.append(
                    AIMessage(content=response)
                )

            except Exception as e:
                print(f"Error: {e}")
                log_file.write(f"Error: {e}\n\n")


if __name__ == "__main__":
    main()