from dotenv import load_dotenv
load_dotenv()

import json
import datetime
import uuid

from agentbackend import build_agent

from signals.dashboard import (
    render_signal_board,
    print_signal_board
)

from langchain_core.messages import (
    HumanMessage,
    AIMessage
)

# =========================================================
# MAIN
# =========================================================

def main():

    # =====================================================
    # BUILD AGENT
    # =====================================================

    agent = build_agent()

    # =====================================================
    # THREAD ID
    # =====================================================

    # unique conversation session
    thread_id = str(uuid.uuid4())

    # =====================================================
    # CONVERSATION MEMORY
    # =====================================================

    conversation_history = []

    # =====================================================
    # INITIAL DASHBOARD
    # =====================================================

    signal_board = render_signal_board()

    print_signal_board(signal_board)

    print("\n🧠 CFOBuddy Agent — Type 'exit' to quit\n")

    # =====================================================
    # LOGGING
    # =====================================================

    with open("conversation.log", "a") as log_file:

        log_file.write(
            f"\n--- New Session: "
            f"{datetime.datetime.now()} ---\n"
        )

        log_file.write(
            f"Thread ID: {thread_id}\n\n"
        )

        log_file.write("Signal Board:\n")

        log_file.write(
            json.dumps(
                signal_board,
                indent=2
            ) + "\n\n"
        )

        # =================================================
        # CHAT LOOP
        # =================================================

        while True:

            user_input = input("You: ").strip()

            # =============================================
            # EMPTY INPUT
            # =============================================

            if not user_input:

                print(
                    "Please enter a valid message.\n"
                )

                continue

            # =============================================
            # EXIT
            # =============================================

            if user_input.lower() in [
                "exit",
                "quit",
                "bye"
            ]:

                print("\n👋 Exiting CFOBuddy...\n")

                log_file.write(
                    "Session ended.\n"
                )

                break

            # =============================================
            # SAVE USER MESSAGE
            # =============================================

            conversation_history.append(
                HumanMessage(
                    content=user_input
                )
            )

            log_file.write(
                f"You: {user_input}\n"
            )

            try:

                # =========================================
                # AGENT INVOCATION
                # =========================================

                result = agent.invoke({

                    "messages": conversation_history,

                    "config": {
                        "configurable": {
                            "thread_id": thread_id
                        }
                    }
                })

                # =========================================
                # RESPONSE EXTRACTION
                # =========================================

                response = (
                    result["messages"][-1]
                    .content
                    .strip()
                )

                # =========================================
                # FALLBACK EMPTY RESPONSE
                # =========================================

                if not response:

                    response = (
                        "I could not generate "
                        "a response right now."
                    )

                # =========================================
                # PRINT RESPONSE
                # =========================================

                print(
                    f"\nCFOBuddy: {response}\n"
                )

                # =========================================
                # SAVE AI RESPONSE
                # =========================================

                conversation_history.append(
                    AIMessage(
                        content=response
                    )
                )

                # =========================================
                # LOG RESPONSE
                # =========================================

                log_file.write(
                    f"CFOBuddy: {response}\n\n"
                )

                # =========================================
                # FLUSH LOGS
                # =========================================

                log_file.flush()

            except KeyboardInterrupt:

                print(
                    "\n\n⚠ Interrupted by user.\n"
                )

                log_file.write(
                    "Session interrupted.\n"
                )

                break

            except Exception as e:

                error_message = (
                    f"Unexpected Error: {e}"
                )

                print(f"\n❌ {error_message}\n")

                log_file.write(
                    f"{error_message}\n\n"
                )

                log_file.flush()


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()