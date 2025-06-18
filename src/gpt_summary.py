import os
import re
from dotenv import load_dotenv
import base64
from openai import OpenAI
from groq import Groq
load_dotenv()
from src.config import SUMMARY_PROMPT

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def create_gpt_summary(text, images_path):
    """
    Create a summary of the given text using the Gemini model.
    
    Args:
        text (str): Text containing image tags to summarize
        
    Returns:
        str: Generated summary from Gemini model
    """
    # Create content list from text
    contents = create_content_list(text, images_path)
    # Add the prompt as the first element in contents list
    contents.insert(0, SUMMARY_PROMPT)
    
    response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[{
                "role": "user",
                "content": contents,
            }
        ],
    temperature=0,
    )
    return response.choices[0].message.content

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def create_content_list(text, images_path):
    """
    Parse text containing image tags and create a list of content elements
    following the specified schema for text and image_url.

    Args:
        text (str): Text containing image tags in the format <ImageN src="path">

    Returns:
        list: List of dictionaries, each representing a text or image part.
              Example: [{"type": "text", "text": "..."}, {"type": "text", "text": "Image 1: "}, {"type": "image_url", "image_url": {"url": "..."}}]
    """
    contents = []
    # Pattern to match image tags with numbers and capture the number and path
    pattern = r'<Image(\d+) src="([^"]+)">'

    # Find all image tags in the text
    matches = list(re.finditer(pattern, text))

    # If no images found, return the text as a single item in the schema
    if not matches:
        if text.strip():
            contents.append({"type": "text", "text": text.strip()})
        return contents

    # Process text segments and images in order
    last_end = 0
    for match in matches:
        # Add text segment before this image (if any)
        text_segment = text[last_end:match.start()]
        if text_segment.strip():
            contents.append({"type": "text", "text": text_segment.strip()})

        # Get image number and path from the match
        image_number = match.group(1)
        image_path = match.group(2)

        filename = os.path.basename(image_path)
                    
        full_path = os.path.join(images_path, filename)
        base64_image = encode_image_to_base64(full_path)
        # Add the image number text before the image data
        contents.append({"type": "text", "text": f"Image {image_number}: "})

        # Add the image using the image_url schema
        contents.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})

        last_end = match.end()

    # Add any remaining text after the last image
    if last_end < len(text) and text[last_end:].strip():
        contents.append({"type": "text", "text": text[last_end:].strip()})

    return contents

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

def read_img(image_path):
    with open(image_path, "rb") as f:
        local_file_img_bytes = f.read()
    return local_file_img_bytes
 





text = """
Support kit for watches (white/black/brown) [235A28/235A29/235A30] EN



# Support kit for watches (white/black/brown) [235A28/235A29/235A30] EN



<Image5 src="/static/images/1536558/643721ca-7781-4b89-8227-b351913338e3.png">

A set of watch supports helps to shape the straps and bracelets for more natural look. The set is available in three color versions. Each set includes 3 pieces of one color in three sizes- S, M, L.


**Features**



* Anti-scratch coating
* 3 pcs
* 3 sizes


**Compatibility**



* ALPHASHOT MICRO [SKU 235H1]
* ALPHASHOT MICRO v2 [SKU 235H2]


**Package contents**



Package contents depend on the set you purchase. One set contains **3 pieces** in **three sizes** in **one color**.



* Support kit for watches for Alphashot MICRO - white [SKU 235A28] -3 pieces, S, M, L
* Support kit for watches for Alphashot MICRO - black [SKU 235A29] -3 pieces, S, M, L
* Support kit for watches for Alphashot MICRO - brown [SKU 235A30] -3 pieces, S, M, L


**Assembly & use instructions**



Depending on the circumference of the watch, select the size of the support and attach it.



<Image6 src="/static/images/1536558/79e619e0-7de0-4190-8e7b-75a7f5a68a95.png">


<Image7 src="/static/images/1536558/d7c5ab4e-2df0-47c6-882f-b0ba2dd3a500.png">

"""



# Example usage
if __name__ == "__main__":
    # Example response:
    # Okay, here's the list of objects present in both images:
    # ...
    # for i in create_content_list(text):
    #     print(i[:100])
    # contents = []
    # dir = "app/static/images/1237880"
    # for filename in os.listdir(dir):
    #     contents.append(Part.from_bytes(data=read_img(os.path.join(dir, filename)), mime_type="image/png"))
    print(create_gpt_summary(text))
    # contents.append(
    #     "Describe the process depicted with the images. "
    # )
    # response = client.models.generate_content(
    #     model="gemini-2.0-flash-001",
    #     contents=contents,
    # )
    # print(response.text)
