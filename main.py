from workflows import article_workflow, manual_workflow
import os

def main():
    print("Orbitvu CLI Updater")
    print("===================")
    mode = ""
    while mode not in ["1", "2"]:
        print("Select mode:")
        print("1. Process Article")
        print("2. Process Manual")
        mode = input("Enter 1 or 2: ").strip()

    print("Orbitvu Support Site: 17219    Sun Site: 17606")
    site_id = input("Enter site ID: ").strip()
    if mode == "1":
        article_id = input("Enter article ID: ").strip()
        print(f"Processing article {article_id} from site {site_id}...")
        article_workflow(article_id, site_id)
    else:
        manual_id = input("Enter manual ID: ").strip()
        print(f"Processing manual {manual_id} from site {site_id}...")
        manual_workflow(manual_id, site_id)

if __name__ == "__main__":
    main()