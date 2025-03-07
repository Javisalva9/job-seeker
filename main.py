from config import Miguel, Javi
import argparse
from worknomads import getWorkNomads

def get_user():
    parser = argparse.ArgumentParser(description="Select a user for scraping.")
    parser.add_argument("--miguel", action="store_true", help="Run the script for Miguel")
    parser.add_argument("--javi", action="store_true", help="Run the script for Javi")
    args = parser.parse_args()
    if args.miguel:
        return Miguel
    elif args.javi:
        return Javi
    else:
        parser.error("❌ You must specify --miguel or --javi")

def main():
    user = get_user()
    workNomadsJobs = getWorkNomads(user)
    print(workNomadsJobs)  # Variable available for further management

if __name__ == "__main__":
    main()
