# import os
# from django.conf import settings
# from django.http import StreamingHttpResponse
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import Conversation
# from .serializers import ConversationSerializer
# import openai
# from langchain.chains import ConversationChain
# from langchain.memory import ConversationBufferMemory
# from langchain.chat_models import ChatOpenAI
# from asgiref.sync import sync_to_async
# import asyncio
#
# # OpenAI API 키 설정
# openai.api_key = os.getenv("OPENAI_API_KEY")
#
# class ChatView(APIView):
#     memory = ConversationBufferMemory()
#     chain = ConversationChain(llm=ChatOpenAI(temperature=0.7), memory=memory)
#
#     async def sse_stream(self, user_input):
#         response = ""
#         async for chunk in self.chain.run_stream(user_input):
#             response += chunk
#             yield f"data: {chunk}\n\n"
#         # 대화 내용을 데이터베이스에 저장
#         await sync_to_async(Conversation.objects.create)(user_input=user_input, bot_response=response)
#
#     def post(self, request):
#         user_input = request.data.get('message', '')
#
#         if not user_input:
#             return Response({"error": "Please provide a message."}, status=status.HTTP_400_BAD_REQUEST)
#
#         response = StreamingHttpResponse(self.sse_stream(user_input), content_type='text/event-stream')
#         return response
#
# # class SummaryView(APIView):
# # OpenAI API 키 설정
# # openai.api_key = os.getenv("OPENAI_API_KEY")
#
# class SummaryView(APIView):
#     def get(self, request):
#         conversations = Conversation.objects.all()
#         conversation_texts = [f"User: {conv.user_input}\nBot: {conv.bot_response}" for conv in conversations]
#         conversation_history = "\n\n".join(conversation_texts)
#
#         # 대화 내용을 요약
#         summary = (ChatOpenAI(temperature=0.7)
#                    .run(f"Summarize the following conversation:\n{conversation_history}"))
#
#         return Response({"summary": summary})
#
