import os
from langchain.schema import HumanMessage
from dotenv import load_dotenv
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_teddynote.messages import stream_response
from langchain_community.chat_models.openai import ChatOpenAI
from opensearchpy import OpenSearch
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

load_dotenv()

# OpenAI API 키 설정
openai_api_key = os.getenv('OPENAI_API_KEY')
# 환경 변수에서 값 가져오기
opensearch_id = os.getenv('OPENSEARCH_ID')
opensearch_password = os.getenv('OPENSEARCH_PASSWORD')
opensearch_url = os.getenv('OPENSEARCH_URL')

# 인증 정보 설정
opensearch_auth = (opensearch_id, opensearch_password)

# 객체 생성
llm = ChatOpenAI(
    api_key=openai_api_key,
    temperature=0.1,  # 창의성 (0.0 ~ 2.0)
    model_name="gpt-4o",  # 모델명
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)

# LangChain 및 OpenAI 설정
# chat = ChatOpenAI(temperature=1, streaming=True, callbacks=[StreamingStdOutCallbackHandler()])
# 프롬프트 템플릿 설정
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="주어진 Context를 보고 답변해주세요. 질문과 관계없는 내용은 포함하지 마세요.\n\nContext: {context}\n\nQuestion: {question}"
)

# LLMChain 설정
llm_chain = LLMChain(llm=llm, prompt=prompt_template)

opensearch_client = OpenSearch(hosts=[opensearch_url], http_auth=opensearch_auth)

# 인덱스 이름 설정 (소문자로)
index_name = 'langchain_rag_test'

# 질문을 통해 OpenSearch에서 문서 검색
def search_documents(query):
    search_body = {
        "query": {
            "match": {
                "content": query
            }
        }
    }
    response = opensearch_client.search(index=index_name, body={"query": {"match_all": {}}})
    hits = response['hits']['hits']
    return [hit['_source']['text'] for hit in hits]

# async def sse_stream(chat_message):
#     async def message_generator():
#         async for chunk in chat.stream_message(chat_message):
#             yield f"data: {chunk}\n\n"
#     return message_generator()
#
# def create_chat_message(user_message):
#     return [HumanMessage(content=user_message)]


answer = llm.stream("대한민국의 아름다운 관광지 10곳과 주소를 알려주세요!")
stream_response(answer)