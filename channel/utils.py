import urllib.request
import openai
import json
import logging
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_huggingface import HuggingFaceEmbeddings
from opensearchpy import OpenSearch
from dotenv import load_dotenv
import os
from . import Prompts
import copy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

#--------------------------------------------------------------------------------------------------------------#
def text_to_speach(text):
    load_dotenv()
    client_id = os.getenv("CLOVA_CLIENT_ID")
    client_secret = os.getenv("CLOVA_CLIENT_SECRET")
    encText = urllib.parse.quote(text)
    data = f"speaker=nminsang&volume=0&speed=0&pitch=0&format=mp3&text={encText}"
    url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
    request_obj = urllib.request.Request(url)
    request_obj.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
    request_obj.add_header("X-NCP-APIGW-API-KEY", client_secret)
    response = urllib.request.urlopen(request_obj, data=data.encode('utf-8'))
    rescode = response.getcode()

    if rescode == 200:
        return response.read(), None
    else:
        return None, rescode

#--------------------------------------------------------------------------------------------------------------#

opensearch_id = os.getenv('OPENSEARCH_ID')
opensearch_password = os.getenv('OPENSEARCH_PASSWORD')
opensearch_url = os.getenv('OPENSEARCH_URL')

embed_model = HuggingFaceEmbeddings(model_name="jhgan/ko-sroberta-multitask")
# 인증 정보 설정
opensearch_auth = (opensearch_id, opensearch_password)

# OpenSearch 클라이언트를 초기화
client = OpenSearch(hosts=[opensearch_url], http_auth=opensearch_auth)

index_name = 'law'

vector_db = OpenSearchVectorSearch(
    opensearch_url=opensearch_url,
    index_name=index_name,
    embedding_function=embed_model,
    http_auth=opensearch_auth,
    use_ssl=True,
    verify_certs=False,  # SSL 검증을 비활성화
    ssl_show_warn=False
)

#--------------------------------------------------------------------------------------------------------------#
channel_memories = {}
# Langchain 메모리 설정
def get_or_create_memory(channel_id):
    if channel_id not in channel_memories:
        channel_memories[channel_id] = ConversationBufferMemory()
    return channel_memories[channel_id]

#--------------------------------------------------------------------------------------------------------------#

def filter_and_remove_score_opensearch_vector_score(res, cutoff_score=0.006, variance=0.95):
    if not res:
        print("검색 결과가 없습니다.")
        return []
    else:
        highest_score = max(score for doc, score in res)
        print('highest_score : ', highest_score)
        if highest_score < cutoff_score:
            return []
        lower_bound = highest_score * variance
        print('lower_bound : ', lower_bound)
        res = [doc for doc, score in res if score >= lower_bound]
        return res

def get_similar_docs(query, k=3, fetch_k=300, score=True):
    if score:
        pre_similar_doc = (vector_db.similarity_search_with_score(
            query,
            k=k,
            fetch_k=fetch_k,
            search_type="approximate_search",
            space_type="l2",
            vector_field="vector_field"
        ))
        print('pre_similar_doc : ', pre_similar_doc)
        similar_docs = filter_and_remove_score_opensearch_vector_score(pre_similar_doc)
        print('similar_docs : ', similar_docs)
    else:
        similar_docs = vector_db.similarity_search(
            query,
            k=k,
            search_type="approximate_search",
            space_type="l2",
            vector_field="vector_field"
        )

    # 중복 제거
    unique_docs = []
    seen_texts = set()
    for doc in similar_docs:
        if doc.page_content not in seen_texts:
            unique_docs.append(doc)
            seen_texts.add(doc.page_content)

    similar_docs_copy = copy.deepcopy(unique_docs)
    return similar_docs_copy

#--------------------------------------------------------------------------------------------------------------#
# def search_documents(query):
#     search_body = {
#         "query": {
#             "match": {
#                 "content": query
#             }
#         }
#     }
#     response = client.search(index=index_name, body=search_body)
#     hits = response['hits']['hits']
#     return [hit['_source']['text'] for hit in hits]

#--------------------------------------------------------------------------------------------------------------#
def stream_gpt_response(prompt):
    client = openai.OpenAI()
    stream = client.chat.completions.create(
        # model="gpt-3.5-turbo",
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content
#--------------------------------------------------------------------------------------------------------------#


def generate_initial_response_stream(channel_id, message):
    memory = get_or_create_memory(channel_id)

    # Search OpenSearch for relevant documents
    search_results = get_similar_docs(message)
    print(search_results)
    context = " ".join([doc.page_content for doc in search_results])

    # Define the prompt template
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template=Prompts.PROMPT_DIRECT_FINAL
    )

    # Create the prompt
    prompt = prompt_template.format(context=context, question=message)

    # Generate and stream the response
    response_stream = stream_gpt_response(prompt)

    # Save the conversation to memory
    full_response = ''
    for chunk in response_stream:
        full_response += chunk
        yield f"data: {chunk}\n\n"

    logger.info(f"Final response: {full_response}")
    memory.save_context({"input": message}, {"output": full_response})


def generate_followup_response_stream(channel_id, message):
    memory = get_or_create_memory(channel_id)

    # Retrieve previous conversation history
    history = memory.load_memory_variables({})["history"]

    # Search OpenSearch for relevant documents
    search_results = get_similar_docs(message)
    print(search_results)
    context = " ".join([doc.page_content for doc in search_results])

    # Define the prompt template for the follow-up response
    prompt_template = PromptTemplate(
        input_variables=["context", "history", "question"],
        template=Prompts.PROMPT_FINAL  # Assuming you have a final prompt template
    )

    # Create the prompt
    prompt = prompt_template.format(context=context, history=history, question=message)

    # Generate and stream the response
    response_stream = stream_gpt_response(prompt)

    # Save the conversation to memory
    full_response = ''
    for chunk in response_stream:
        full_response += chunk
        yield f"data: {chunk}\n\n"

    logger.info(f"Final response: {full_response}")
    memory.save_context({"input": message}, {"output": full_response})
