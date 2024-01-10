from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Task
from .serializers import TaskSerializer, UserRegistrationSerializer, LoginSerializer
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication 
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated  
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from graphene_django.views import GraphQLView
from .schema import schema
from django.contrib.auth import authenticate, login, logout

from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

@api_view(['GET', 'POST'])
# @authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def task_list(request):
    if request.method == 'GET':
        tasks = Task.objects.filter(user=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def task_detail(request, pk):
    try:
        task = Task.objects.get(pk=pk, user=request.user)
    except Task.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@csrf_exempt  # Note: csrf_exempt is used for development purposes, consider removing it in production
@api_view(['POST'])
def user_registration(request):
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            
            user = serializer.save()

            
            token, created = Token.objects.get_or_create(user=user)

           
            response_data = {
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'message': 'Registration successful',  # Add a success message if needed
            }

            
            return Response(response_data, status=status.HTTP_201_CREATED)

        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
@csrf_exempt
@require_POST
def custom_login(request):
    serializer = LoginSerializer(data=request.POST)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            token, _ = AuthToken.objects.create(user)
            return JsonResponse({'token': token, 'user_id': user.id, 'username': user.username})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid data provided'}, status=400)

@api_view(['POST'])
def custom_logout(request):
    logout(request)
    return JsonResponse({'message': 'Logout successful'})



# myapp/views.py

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def graphql_view(request):
    return GraphQLView.as_view(schema=schema, graphiql=True)(request)

