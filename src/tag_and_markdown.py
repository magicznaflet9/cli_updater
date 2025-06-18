from bs4 import BeautifulSoup
import os
from tqdm import tqdm
from markdownify import markdownify

def tag_and_markdown(html_file_path, output_file_path=None, debug=False):
    try:
        add_tags(html_file_path)
        html_to_markdown(html_file_path, html_file_path.replace('.html', '.md'))
    except Exception as e:
        print(f"Error tag and markdown for {html_file_path}: {str(e)}")
        return f"Error: {str(e)}"

def html_to_markdown(file_path, output_file):
    try: 
        with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

        markdown_content = markdownify(html_content, heading_style="ATX", strip="a", escape_underscores=False)

        # # Save to a file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        print(f"Markdown content has been saved to {output_file}")

        return "Sucess"
    
    except Exception as e:

        print(f"Error with markdown conversion: {str(e)}")
        return f"Error: {str(e)}"


def extract_filename(src):
    # Split at .png, .jpg or .gif and take the first part, then add the extension back
    if '.png' in src:
        base = src.split('.png')[0]
        extension = '.png'
    elif '.PNG' in src:
        base = src.split('.PNG')[0]
        extension = '.PNG'
    elif '.jpg' in src:
        base = src.split('.jpg')[0]
        extension = '.jpg'
    elif '.JPG' in src:
        base = src.split('.JPG')[0]
        extension ='.JPG'
    elif '.jpeg' in src:
        base = src.split('.jpeg')[0]
        extension ='.jpeg'
    elif '.gif' in src:
        base = src.split('.gif')[0]
        extension = '.gif'
    else:
        # no recognized extension
        base = src
        extension = ''
        print("No recognized extension")
    return base + extension

def add_tags(html_file_path, output_file_path=None, debug=False):
    # Read the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Create BeautifulSoup object
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all img tags
    img_tags = soup.find_all('img')
    
    # Replace each img tag with text
    progress_caption = tqdm(img_tags, desc=f"Replacing images with tags in article: {os.path.basename(html_file_path)}", unit="image", colour='cyan', leave=False)

    
    article_id = os.path.basename(html_file_path).split('.')[0]

    n = 1
    for img in img_tags:
        src = img.get('src', '')
        image_name = extract_filename(os.path.basename(src))
        image_path = os.path.join(article_id, image_name)
        if debug==True:
            continue
        
        # Create a new tag instead of raw text replacement
        new_tag = f'<Image{n} src="/static/images/{image_path}">'
        
        # Replace the img tag with the new tag
        img.replace_with(new_tag)
        progress_caption.update(1)
        n += 1
    # If no output path specified, modify the original file
    if output_file_path is None:
        output_file_path = html_file_path

    # Write the modified HTML to file
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))

    progress_caption.close()
    return

