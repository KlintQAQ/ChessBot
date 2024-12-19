from cli.game_loop import play_human_vs_ai, play_ai_vs_ai


def main():
    """
    Main entry point for the CLI interface.
    """
    while True:
        print("\n=== ChessBot CLI ===")
        print("1. Human vs AI")
        print("2. AI vs AI")
        print("3. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            play_human_vs_ai()
        elif choice == "2":
            play_ai_vs_ai()
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")