from ss_exporter import get_article, get_manual
from src.tag_and_markdown import tag_and_markdown 
from src.create_docs import load_documents
from src.pinecone_ops import send_docs_to_pinecone, remove_article_pinecone
from src.utils import is_software
from src.config import TARGET_IMAGES_PATH
from src.convert_images import convert_images_to_webp
import os
import shutil


# Global variable to track the current article being processed
current_article_id = None
output_folder = "temp"

def article_workflow(article_id, site_id):
    try:
        # Fetch the article
        result = fetch_article(article_id, site_id, output_folder="temp")
    except Exception as e:
        print(f"Error fetching article {article_id}: {str(e)}")
        remove_temp_folder(article_id)
        return False
    try:
        process_article(article_id, site_id, result)
    except Exception as e:
        print(f"Error processing article {article_id}: {str(e)}")
        return False
    finally:
        remove_temp_folder(article_id)

def manual_workflow(manual_id, site_id):
    try:
        # Fetch the manual
        result = fetch_manual(manual_id, site_id, output_folder="temp")
    except Exception as e:
        print(f"Error fetching manual {manual_id}: {str(e)}")
        remove_temp_folder(manual_id)
        return False
    try:
        process_manual(site_id, result)
    except Exception as e:
        print(f"Error processing manual {manual_id}: {str(e)}")
        return False
    finally:
        remove_temp_folder(manual_id)



def fetch_manual(manual_id, site_id, output_folder="temp"):
    print(f"Fetching manual {manual_id} from site {site_id}...")
    result = get_manual("orbitvu", "dev@orbitvu.com", os.environ.get("SCREENSTEPS_API_KEY"),
                        str(site_id), str(manual_id), output_folder=output_folder)
    if not result:
        print(f"Failed to fetch manual {manual_id}.")
        remove_temp_folder(manual_id)
        return False
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        man_dir_path = os.path.join(current_dir, f"{output_folder}/{manual_id}/")
        return man_dir_path

def fetch_article(article_id, site_id, output_folder="temp"):

    print(f"Fetching article {article_id} from site {site_id}...")
    result = get_article("orbitvu", "dev@orbitvu.com", os.environ.get("SCREENSTEPS_API_KEY"), 
                        str(site_id), str(article_id), output_folder=output_folder)
    if not result:
        print(f"Failed to fetch article {article_id}.")
        remove_temp_folder(article_id)
        return False
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        article_dir_path = os.path.join(current_dir, f"{output_folder}/{article_id}")
        return article_dir_path

def process_manual(site_id, man_dir_path):
    """Process all articles in a manual folder."""
    # Get the manual_id from the path
    manual_id = os.path.basename(os.path.normpath(man_dir_path))
    
    try:
        for folder in os.listdir(man_dir_path):
            folder_path = os.path.join(man_dir_path, folder)
            if os.path.isdir(folder_path):
                # Get the article_id from the folder name
                article_id = folder
                print(f"Processing article path {folder_path}")
                # Call the process_article function with the appropriate parameters
                process_article(article_id, site_id, folder_path, debug=True)
        return True
    except Exception as e:
        print(f"Error processing manual: {str(e)}")
        return False
    finally:
        # This part was missing - we need to clean up the manual folder too
        if manual_id:
            remove_temp_folder(manual_id)

def process_article(article_id, site_id, article_dir_path, debug=False):
    """Process an article, creating vectorstore entries."""
    global current_article_id
    current_article_id = article_id
    
    try:
        html_file_path = os.path.join(article_dir_path, f"{article_id}.html")
        
        if not os.path.exists(html_file_path):
            print(f"HTML file not found at {html_file_path}")
            return False

        
        print(f"Converting HTML to markdown and tagging content...")
        tag_and_markdown(html_file_path)

        if debug:
            print(f"Debug mode is ON. Skipping document loading and vectorstore operations for article {article_id}.")
            return True

        isSoftware = is_software(article_id, article_dir_path)
        print(f"Loading documents for article {article_id}...")
        docs = load_documents(article_id, article_dir_path, software=isSoftware)

        if not docs:
            print("No documents were loaded. Processing failed.")
            return False
        
        print(f"Removing existing records for article {article_id} from vectorstore...")
        if not remove_article_pinecone(article_id, software=isSoftware, article_dir=article_dir_path):
            print("Failed to remove existing records from vectorstore.")
            return False
        
        print(f"Sending new documents to vectorstore...")
        result = send_docs_to_pinecone(docs, article_id, software=isSoftware)

        images_path = os.path.join(article_dir_path, "images")
        convert_images_to_webp(images_path, os.path.join(TARGET_IMAGES_PATH, f"{article_id}"))

        if result:
            print(f"Successfully processed article {article_id}.")
            return True
        else:
            print("Failed to send documents to vectorstore.")
            return False
            
    except Exception as e:
        print(f"Error processing article: {str(e)}")
        return False
    finally:
        # Clean up temporary files whether successful or not
        remove_temp_folder(article_id)

def remove_temp_folder(article_id=None):
    """Remove the temporary folder for an article if it exists."""
    if article_id is None and current_article_id is None:
        return
        
    folder_to_remove = article_id if article_id else current_article_id
    current_dir = os.path.dirname(os.path.abspath(__file__))
    temp_folder_path = os.path.join(current_dir, f"{output_folder}/{folder_to_remove}")
    
    if os.path.exists(temp_folder_path):
        try:
            print(f"Cleaning up temporary files for article {folder_to_remove}...")
            shutil.rmtree(temp_folder_path)
            print(f"Temporary files removed.")
        except Exception as e:
            print(f"Warning: Failed to remove temporary folder: {str(e)}")


if __name__ == "__main__":
    # The correct approach would be:
    manual_id = "66870"  # The manual ID as a string
    site_id = 17219      # The site ID (use appropriate value, 17606 for software)
    
    # Use the manual workflow that handles cleanup properly
    manual_workflow(manual_id, site_id)