import json
from .agent_tools import load_data
from .cash_flow import getcash_health_signal
from .fullfillment import get_fullfilement_signal
from .unit_economics import get_unit_econ_signal


def render_signal_board():
    data = load_data()
    cash = data.get("cash", {"cash_in_storage": 800000, "monthly_usage": 180000})
    zones = data.get("zones", [
        {"zone": "Zone A", "packing_delay_minutes": 2.4, "congestion": "LOW", "queue_depth": 8},
        {"zone": "Zone B", "packing_delay_minutes": 5.5, "congestion": "MEDIUM", "queue_depth": 12},
    ])
    orders = data.get("orders", [])

    board = {
        "cash": getcash_health_signal(cash["cash_in_storage"], cash["monthly_usage"]),
        "fulfillment": get_fullfilement_signal(zones),
        "unit_economics": get_unit_econ_signal(orders),
    }
    return board


def print_signal_board(board):
    print("\n=== CFOBuddy Signal Board ===")
    for name, signal in board.items():
        print(f"\n{name.upper()}: {signal['label']} ({signal['status']})")
        print(f"  {signal['message']}")
        if "months_left" in signal:
            print(f"  Months left: {signal['months_left']:.1f}")
        if "cm2_positive_pct" in signal:
            print(f"  CM2 positive orders: {signal['cm2_positive_pct']}%")
        if "avg_delay" in signal:
            print(f"  Avg delay: {signal['avg_delay']} min")
    print("============================\n")
