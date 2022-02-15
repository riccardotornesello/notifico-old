from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import *
from .serializers import *


class MessageList(APIView):
    serializer_class = MessageSerializer

    def post(self, request, format=None):
        serializer = MessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        project = Project.objects.filter(
            api_key=serializer.validated_data['token']).first()
        if not project:
            return Response({
                "token": [
                    "Invalid token."
                ]
            }, status=status.HTTP_401_UNAUTHORIZED)

        channels = Channel.objects.filter(project=project)
        for channel in channels:
            message = gen_message(
                serializer.validated_data['text'], LOG_LEVEL.INFO, f'New message from {project.name}')
            channel.send(message)
        return Response({'status': 'success', 'details': {'channels_count': len(channels)}}, status=status.HTTP_201_CREATED)
