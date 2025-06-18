import os
import time

from pinecone import ServerlessSpec
from pinecone.grpc import PineconeGRPC

from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

# from config import HOSTS
from src.utils import get_manual_title, get_chapter_title
from src.config import HOSTS

pc = PineconeGRPC(api_key=os.environ.get("PINECONE_API_KEY"))
langchain_embed_model = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=os.environ.get("OPENAI_API_KEY"))


def remove_article_pinecone(article_id, software=False, article_dir=None):
    try:
        if software:
            namespace = get_manual_title(article_id, article_dir).strip()
            index_name = HOSTS[1][1]
            index = create_index(index_name=index_name)
        else:
            namespace = get_chapter_title(article_id, article_dir)
            index_name = HOSTS[0][1]
            index = create_index(index_name=index_name)

        removal_l = []
        for ids in index.list(namespace=namespace):
            for id in ids: removal_l.append(id) if id.startswith(f"{article_id}") else None

        if not removal_l:
            print(f"No existing records found for article_id: {article_id} in namespace: {namespace} in index: {index_name}")
            return True
        index.delete(
        ids=removal_l,
        namespace=namespace
    )
        print(f"Removed IDs for article_id: {article_id} from namespace: {namespace} in index: {index_name}")
        return True
    except Exception as e:
        print(f"Error removing article {article_id} from Pinecone: {e}")
        return False

def send_docs_to_pinecone(documents, article_id, software=False):

    if not documents:
        print("No documents to process.")
        return
    
    if software:
        manual_title = get_manual_title(article_id)
        namespace = manual_title.strip()
        index_name = HOSTS[1][1] 
        index_host = HOSTS[1][0]  
        create_index(index_name=index_name)
    else:
        chapter_title = get_chapter_title(article_id)
        namespace = chapter_title
        index_name = HOSTS[0][1]
        index_host = HOSTS[0][0]
        create_index(index_name=index_name)
    print(f"Using index: {index_name} in namespace: {namespace} at host: {index_host}")

    vectorstore_from_docs = PineconeVectorStore.from_documents(
        documents,
        ids=[f"{article_id}-{i}" for i in range(len(documents))],
        index_name=index_name,
        embedding=langchain_embed_model,
        namespace=namespace
    )
    print(f"Uploaded {len(documents)} documents to namespace: {namespace} in Pinecone index: {index_name}")
    return vectorstore_from_docs


def create_index(index_name, dimension=1536, metric="cosine"):
    # Remove pc initialization since it's global
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)
    return pc.Index(index_name)


if __name__ == "__main__":
    # Example usage
   remove_article_pinecone("972433")
    # Example of sending documents to Pinecone
    # send_docs_to_pinecone(documents, article_id, software=False)