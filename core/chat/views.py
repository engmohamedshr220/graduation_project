# views.py

import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import google.generativeai as googleai
from .models import ChatMessage, Chat
from .serializers import ChatMessageSerializer
from uuid import uuid4
from drf_spectacular.utils import extend_schema, OpenApiExample , OpenApiResponse, OpenApiRequest
class AskGoogleAPIView(APIView):
    
    @extend_schema(
        request=ChatMessageSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiResponse,
                description= 'Success',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={
                            'answer': 'The capital of France is Paris.'
                        },
                    ),
                ],
                    
                
                ),
            400:OpenApiResponse(
                response=OpenApiResponse,
                description= 'Bad Request',
                examples=[
                    OpenApiExample(
                        'Bad Request',
                        value={
                            'error' : 'message are required'
                        },
                        
                    ),
                ],
                    
                
                ),
        },
    )
    
    
    def post(self, request):
        message = request.data.get('message')
        chat_id = request.data.get('chat_id')

        if not message :
            return Response({'error': 'message and chat_id are required'}, status=status.HTTP_400_BAD_REQUEST)

        if not chat_id:
            # Create a new chat if chat_id is not provided
            chat = Chat.objects.create( title="Chat with Gemini")
            chat_id = chat.id
        try:
            # Load chat history
            chat_messages = ChatMessage.objects.filter(chat_id=chat_id).order_by("timestamp")
            history = [
                {"role": "model" if msg.is_ai else "user", "parts": [msg.message]}
                for msg in chat_messages
            ]

            # Add current message
            history.append({"role": "user", "parts": [message]})

            # Call Gemini API
            reply = self.get_gemini_response(history, message)

            # Save user message and AI reply
            ChatMessage.objects.create(chat_id_id=chat_id, message=message, is_ai=False)
            ChatMessage.objects.create(chat_id_id=chat_id, message=reply, is_ai=True)

            return Response({
                            'answer': reply,
                            "chat_id": chat_id,
                            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': 'Failed to get response from Gemini API',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def get_gemini_response(history, message):
        googleai.configure(api_key=settings.GOOGLE_API_KEY)
        model = googleai.GenerativeModel(model_name="gemini-2.0-flash")
        chat = model.start_chat(history=history)
        response = chat.send_message(message)
        return response.text
