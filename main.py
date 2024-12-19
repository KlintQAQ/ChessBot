import sys
from cli import main as cli_main
from gui import main as gui_main

def display_interface_menu():
    """
    Display the main menu for choosing the interface.
    """
    print("\n" + "="*40)
    print("         Welcome to ChessBot!")
    print("="*40)
    print("Select an interface to start playing:")
    print("1. Command-Line Interface (CLI)")
    print("2. Graphical User Interface (GUI)")
    print("3. Exit")
    print("="*40)
    print("Enter the number of your choice and press Enter.")

def main():
    """
    Entry point for ChessBot. Lets the user pick an interface.
    """
    while True:
        display_interface_menu()
        choice = input("Your choice: ").strip()

        if choice == "1":
            print("\nStarting the CLI version of ChessBot...\n")
            cli_main()  # Launch the CLI
        elif choice == "2":
            print("\nAttempting to start the GUI version of ChessBot...")
            try:
                gui_main()  # Launch the GUI
            except ImportError:
                print("\nGUI not available. Please ensure all GUI dependencies are installed.\n")
        elif choice == "3":
            print("\nExiting ChessBot. Thanks for playing!")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.\n")

if __name__ == "__main__":
    main()
