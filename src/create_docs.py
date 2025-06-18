# Standard library imports
import os
import glob
import re

# Third-party imports
from tqdm import tqdm

# Langchain imports
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from src.utils import *
from src.gpt_summary import create_gpt_summary


# Initialize global variables*
langchain_embed_model = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=os.environ.get("OPENAI_API_KEY"))


def load_documents(article_id, article_dir_path, software=False):

    # Add a check at the beginning to handle None values
    md_file = os.path.join(article_dir_path, f"{article_id}.md")

    # try:
        # Read the markdown file
    if md_file is None or not os.path.exists(md_file):
        print("Error: No file provided to load_documents")
        return []

    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    documents = []
    text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("##", "Header 2")], strip_headers=False)

    article_title = get_article_title(article_id, article_dir_path)
    url_article_title = article_title.lower().strip().replace(" ", "-").replace("[", "-").replace("]", "-").replace("'", "-")
    chapter_title = get_chapter_title(article_id, article_dir_path)
    manual_title = get_manual_title(article_id, article_dir_path)

    if software:
        url = f"https://public.manuals.orbitvu.com/a/{article_id}-{url_article_title}".replace("--", "-")
    else:
        url = f"https://manuals.orbitvu.com/a/{article_id}-{url_article_title}".replace("--", "-")

    # Create base metadata dictionary
    metadata = {
        "original_text" : False,
        "article_id": article_id,
        "article_title": article_title,
        "chapter_title": chapter_title,
        "manual_title": manual_title,
        "section_title": False,
        "url": url,
    }
    
    # Process the document using our recursive function
    file_documents = create_documents(
        content=content,
        text_splitter=text_splitter,
        metadata=metadata,
        article_path=article_dir_path,
    )
    
    documents.extend(file_documents)
        
    # except Exception as e:
    #     # Print errors without progress bar
    #     print(f"Error loading {md_file}: {str(e)}")

    print(f"Successfully processed {len(documents)} total document chunks")
    return documents

def create_documents(content, text_splitter, metadata, recursion_depth=0, max_depth=4, article_path=None):
    documents = []
    base_url = metadata["url"]
    article_id = metadata["article_id"]

    images_path = os.path.join(article_path, "images")

    try:
        # Apply the text splitter
        md_chunks = text_splitter.split_text(content)
        
        # Create progress bar for chunks in this file
        chunk_progress = tqdm(
            total=len(md_chunks), 
            desc=f"Creating summaries for article {article_id} (depth={recursion_depth})", 
            unit="chunk",
            leave=False,
            colour="cyan"
        )
        
        for i, md_chunk in enumerate(md_chunks):
            # If section_title is False, try to see if there is a header if there isn't pass
            if not metadata["section_title"]:
                section_title = md_chunk.metadata.get('Header 2', False) if hasattr(md_chunk, 'metadata') else False
                if section_title:
                    metadata["section_title"] = section_title
                    metadata["url"] = base_url + f"#{section_title.lower().replace(' ', '-')}"
            
            # Create summary of the section
            page_content = md_chunk.page_content if hasattr(md_chunk, 'metadata') else md_chunk
            # Set the id
            if number_of_tags(page_content) > 10:
                summary = ""
            else:
                summary = create_gpt_summary(page_content, images_path)
                if len(summary) > 1000:
                    if len(summary) > 2000:
                        chunk_progress.write(f"\033[31m\nVery long summary: {len(summary)}\n\033[0m")
                    else:
                        chunk_progress.write(f"\033[33m\nLong summary: {len(summary)}\n\033[0m")
            
            # If summary creation failed, try splitting the content with a different approach
            if summary == "":
                
                if recursion_depth < max_depth:
                    # Try headers first (level 3 if we used level 2 before)
                    if recursion_depth == 0:
                        new_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("###", "Header 3")], strip_headers=False)
                    # Then use our custom image-aware splitter
                    elif recursion_depth == 3:
                        new_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
                    else:
                        new_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
                    
                    
                    # Store a local copy of metadata to avoid modifying the parent's metadata
                    local_metadata = metadata.copy()
                    
                    sub_documents = create_documents(
                        page_content, 
                        new_splitter, 
                        local_metadata, 
                        recursion_depth + 1,
                        max_depth,
                        article_path=article_path
                    )
                    
                    documents.extend(sub_documents)
                    chunk_progress.write(f"Recursion depth {recursion_depth+1} for large chunk in article {article_id} Successful")
                    
                else:
                    # At max depth, just use the content directly with minimal processing
                    print(f"\033[31mReached max recursion depth for chunk in article {article_id}, using simple chunk\033[0m")

                    # Create a simple document with the content
                    doc = Document(
                        page_content="This section contains technical content from the manual that is too complex to summarize.",
                        metadata=metadata.copy()
                    )
                    documents.append(doc)
                    # Reset metadata for next iteration
                    metadata["url"] = base_url
                    metadata["section_title"] = False
                    metadata["original_text"] = False
            else:
                 # Clean image descriptions to get just the image tags                
                metadata['original_text'] = page_content

                doc = Document(
                    page_content=summary,
                    metadata=metadata
                )
                documents.append(doc)

                # Reset metadata for next iteration
                metadata["url"] = base_url
                metadata["section_title"] = False
                metadata["original_text"] = False
            
            # Update chunk progress bar
            chunk_progress.update(1)
        
        # Close the chunk progress bar when done
        chunk_progress.close()
            
        return documents
        
    except Exception as e:
        # Print errors without master progress bar
        print(f"Error processing chunk in article {article_id} (depth={recursion_depth}): {str(e)}")
        return documents
    
def number_of_tags(text):
    """
    Count the number of <Image{n}> tags in the text.
    """
    # Updated regex to match the new pattern <Image{n} src="...">
    return len(re.findall(r'<Image\d+ src="[^"]+">', text))



if __name__ == "__main__":
    print(load_documents("1885604", software=False))