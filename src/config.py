"""
Configuration module for the Orbitvu RAG Project.
Contains shared constants and configuration settings.
"""
import os
TARGET_IMAGES_PATH = "/Users/zofiabochenek/Desktop/cli_updater/temp/images"

# Pinecone host configuration
HOSTS = [
    (
        "https://orbitvu-hardware-index-gxhha0v.svc.aped-4627-b74a.pinecone.io", 
        "orbitvu-hardware-index"
    ), 
    (
        "https://orbitvu-software-index-gxhha0v.svc.aped-4627-b74a.pinecone.io",
        "orbitvu-software-index"
    )
]

SUMMARY_PROMPT = {"type": "text", "text": '''You are a bot preparing chunks for a RAG database. Based on the provided text and images from the Orbitvu user manual:

1. Create a concise summary of the process or processes shown in the excerpt.
2. Describe the images in the context of the process, ensuring the descriptions align with the number and order of images in the text.
3. Avoid any introductory or concluding phrases like "Here is the summary" or "Ok, let's begin."
4. Focus solely on the content relevant to embedding in a retrieval database. Exclude any unnecessary information.
5. If images show compliance statements, simply state: "The device meets required standards and regulations."

Ensure the summary captures the essence of the process and integrates the images meaningfully into the context.
Images are numbered sequentially (Image 1:, Image 2:, etc.) based on their order of appearance in the original article.
====================================================================='''}

