import json
import os

def is_software(article_id, article_dir=None):
    if get_manual_title(article_id, article_dir) == "Device manuals":
        return False
    elif get_manual_title(article_id, article_dir) == "Knowledge base and FAQ":
        return False
    else:
        return True

def get_meta_man_title(manual_id, manual_dir):
    """
    Load and return the metadata for a given manual ID.
    
    Args:
        manual_id (str): The ID of the manual.
        manual_dir (str): Directory path where the manual is stored.
    
    Returns:
        dict: The manual metadata as a dictionary or None if the file doesn't exist.
    """
    json_file_path = os.path.join(manual_dir, f"{manual_id}.json")
    
    if not os.path.exists(json_file_path):
        print(f"Metadata file for manual {manual_id} does not exist at {json_file_path}.")
        return None
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_metadata(article_id, article_dir=None):
    """
    Load and return the metadata for a given article ID.
    
    Args:
        article_id (str): The ID of the article.
        article_dir (str, optional): Directory path where the article is stored.
                                     If None, uses default temp directory.
    
    Returns:
        dict: The article metadata as a dictionary or None if the file doesn't exist.
    """
    if article_dir:
        json_file_path = os.path.join(article_dir, f"{article_id}.json")
    else:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_file_path = os.path.join(current_dir, f"temp/{article_id}/{article_id}.json")
    
    if not os.path.exists(json_file_path):
        print(f"Metadata file for article {article_id} does not exist at {json_file_path}.")
        return None
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_site_title(article_id, article_dir=None):
    """
    Get the site title for a given article ID.
    
    Args:
        article_id (str): The ID of the article.
        article_dir (str, optional): Directory path where the article is stored.
    
    Returns:
        str: The site title or None if not found.
    """
    metadata = get_metadata(article_id, article_dir)
    if metadata and 'site' in metadata and 'title' in metadata['site']:
        return metadata['site']['title']
    return None

def get_manual_title(article_id, article_dir=None):
    """
    Get the manual title for a given article ID.
    
    Args:
        article_id (str): The ID of the article.
        article_dir (str, optional): Directory path where the article is stored.
    
    Returns:
        str: The manual title or None if not found.
    """
    metadata = get_metadata(article_id, article_dir)
    if metadata and 'manual' in metadata and 'title' in metadata['manual']:
        return metadata['manual']['title']
    return None

def get_chapter_title(article_id, article_dir=None):
    """
    Get the chapter title for a given article ID.
    
    Args:
        article_id (str): The ID of the article.
        article_dir (str, optional): Directory path where the article is stored.
    
    Returns:
        str: The chapter title or None if not found.
    """
    metadata = get_metadata(article_id, article_dir)
    if metadata and 'chapter' in metadata and 'title' in metadata['chapter']:
        return metadata['chapter']['title']
    return None

def get_article_title(article_id, article_dir=None):
    """
    Get the article title for a given article ID.
    
    Args:
        article_id (str): The ID of the article.
        article_dir (str, optional): Directory path where the article is stored.
    
    Returns:
        str: The article title or None if not found.
    """
    metadata = get_metadata(article_id, article_dir)
    if metadata and 'article' in metadata and 'title' in metadata['article']:
        return metadata['article']['title']
    return None

def get_site_id(article_id, article_dir=None):
    """
    Get the site ID for a given article ID.
    
    Args:
        article_id (str): The ID of the article.
        article_dir (str, optional): Directory path where the article is stored.
    
    Returns:
        str: The site ID or None if not found.
    """
    metadata = get_metadata(article_id, article_dir)
    if metadata and 'site' in metadata and 'id' in metadata['site']:
        return metadata['site']['id']
    return None

def get_manual_id(article_id, article_dir=None):
    """
    Get the manual ID for a given article ID.
    
    Args:
        article_id (str): The ID of the article.
        article_dir (str, optional): Directory path where the article is stored.
    
    Returns:
        int or str: The manual ID or None if not found.
    """
    metadata = get_metadata(article_id, article_dir)
    if metadata and 'manual' in metadata and 'id' in metadata['manual']:
        return metadata['manual']['id']
    return None

def get_chapter_id(article_id, article_dir=None):
    """
    Get the chapter ID for a given article ID.
    
    Args:
        article_id (str): The ID of the article.
        article_dir (str, optional): Directory path where the article is stored.
    
    Returns:
        int or str: The chapter ID or None if not found.
    """
    metadata = get_metadata(article_id, article_dir)
    if metadata and 'chapter' in metadata and 'id' in metadata['chapter']:
        return metadata['chapter']['id']
    return None

if __name__ == "__main__":
    # Example usage
    article_id = "1885604"
    print("Site Title:", get_site_title(article_id))
    print("Manual Title:", get_manual_title(article_id))
    print("Chapter Title:", get_chapter_title(article_id))
    print("Article Title:", get_article_title(article_id))
    print("Site ID:", get_site_id(article_id))
    print("Manual ID:", get_manual_id(article_id))
    print("Chapter ID:", get_chapter_id(article_id))