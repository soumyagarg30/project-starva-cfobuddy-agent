import time
from datetime import datetime


CHAKRAS = [
	{
		"name": "Root",
		"color": "Red",
		"focus": "Safety and grounding",
		"affirmation": "I am safe. I am supported.",
		"breath_seconds": 4,
	},
	{
		"name": "Sacral",
		"color": "Orange",
		"focus": "Creativity and flow",
		"affirmation": "I create with joy.",
		"breath_seconds": 4,
	},
	{
		"name": "Solar Plexus",
		"color": "Yellow",
		"focus": "Confidence and willpower",
		"affirmation": "I trust my inner strength.",
		"breath_seconds": 5,
	},
	{
		"name": "Heart",
		"color": "Green",
		"focus": "Love and compassion",
		"affirmation": "I give and receive love freely.",
		"breath_seconds": 5,
	},
	{
		"name": "Throat",
		"color": "Blue",
		"focus": "Truth and expression",
		"affirmation": "My voice is clear and true.",
		"breath_seconds": 4,
	},
	{
		"name": "Third Eye",
		"color": "Indigo",
		"focus": "Insight and intuition",
		"affirmation": "I trust my inner wisdom.",
		"breath_seconds": 4,
	},
	{
		"name": "Crown",
		"color": "Violet",
		"focus": "Connection and awareness",
		"affirmation": "I am connected to higher guidance.",
		"breath_seconds": 6,
	},
]


def name_line(chakra: dict) -> str:
	return f"{chakra['name']} Chakra ({chakra['color']})"


def guided_breath(cycles: int, inhale: int = 4, exhale: int = 4) -> None:
	for i in range(1, cycles + 1):
		print(f"  Cycle {i}: Inhale for {inhale}s...")
		time.sleep(inhale)
		print(f"           Exhale for {exhale}s...")
		time.sleep(exhale)


def run_session(seconds_per_chakra: int = 30) -> None:
	print("\nChakra Healing Session")
	print("----------------------")
	print("Press Ctrl+C anytime to stop.\n")

	started_at = datetime.now()
	try:
		for chakra in CHAKRAS:
			print(f"\n{name_line(chakra)}")
			print(f"Focus: {chakra['focus']}")
			print(f"Affirmation: {chakra['affirmation']}\n")

			cycle_duration = chakra["breath_seconds"] * 2
			cycles = max(1, seconds_per_chakra // cycle_duration)
			guided_breath(
				cycles,
				inhale=chakra["breath_seconds"],
				exhale=chakra["breath_seconds"],
			)

			print("  Sit in stillness for 5 seconds...")
			time.sleep(5)

		ended_at = datetime.now()
		print("\nSession complete.")
		print(f"Started: {started_at.strftime('%Y-%m-%d %H:%M:%S')}")
		print(f"Ended:   {ended_at.strftime('%Y-%m-%d %H:%M:%S')}")
		print("Take a moment to drink water and journal how you feel.\n")

	except KeyboardInterrupt:
		print("\n\nSession paused by user. Be gentle with yourself.\n")


if __name__ == "__main__":
	run_session(seconds_per_chakra=30)
