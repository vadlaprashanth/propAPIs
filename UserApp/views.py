from django.shortcuts import render
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User, Post
from .serializers import UserSerializer, PostSerializer
from django.conf import settings


CACHE_TTL = getattr(settings, 'CACHE_TTL',DEFAULT_TIMEOUT)


@api_view(['POST'])
def create_user(request):
    try:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            if User.objects.filter(email=email).exists():
                return Response({
                'success': False,
                'message': 'User with the same email already exists',
                'data': None,
                'status': status.HTTP_409_CONFLICT
            })
        user = serializer.save()

        # Cache the user data
        cache_key = f'user:{user.id}'
        cache.set(cache_key, user)

        return Response({
        'success': True,
        'message': 'User Created successfully',
        'data': serializer.data,
        'status':status.HTTP_201_CREATED
        })
    except Exception as e:
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_user(request, user_id):
     
    #Getting From Cache
    cache_key = f'user:{user_id}'
    user = cache.get(cache_key)
    if user is not None:
        serializer = UserSerializer(user)
        return Response({
            'success': True,
            'message': 'User data retrieved from cache',
            'data': serializer.data
        })

    #Getting from DB    
    try:
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user)
        cache.set('my_cache_key', serializer)
        return Response({
        'success': True,
        'message': 'User details retrieved',
        'data': serializer.data,
        'status':status.HTTP_201_CREATED
        })
    except Exception as e:
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
def update_user(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'User Updated successfully',
                'data': serializer.data,
                'status':status.HTTP_201_CREATED
                })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User does not exist',
            'data': None
        })

    user.delete()

    # Remove the cached user data
    cache_key = f'user:{user_id}'
    cache.delete(cache_key)

    return Response({
        'success': True,
        'message': 'User deleted successfully',
        'data': None
    })


@api_view(['POST'])
def create_post(request):
    try:
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save()

            # Cache the post data
            cache_key = f'post:{post.id}'
            cache.set(cache_key, post)

            return Response({
                'success': True,
                'message': 'User Posted successfully',
                'data': serializer.data,
                'status':status.HTTP_201_CREATED
                })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def post_detail(request, post_id):

     # Check if the post data is cached
    cache_key = f'post:{post_id}'
    post = cache.get(cache_key)
    if post is not None:
        serializer = PostSerializer(post)
        return Response({
            'success': True,
            'message': 'Post data retrieved from cache',
            'data': serializer.data
        })
    
    # From DB
    try:
        post = get_object_or_404(Post, id=post_id)
        if request.method == 'GET':
            serializer = PostSerializer(post)
            return Response(serializer.data)
        elif request.method == 'PUT' or request.method == 'PATCH':
            serializer = PostSerializer(post, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                        'success': True,
                        'message': 'User Post Updated successfully',
                        'data': serializer.data,
                        'status':status.HTTP_201_CREATED
                        })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            post.delete()
            return Response({
                    'success': True,
                    'message': 'Post Deleted Successfully',
                    'status':status.HTTP_204_NO_CONTENT
                })
    except Exception as e:
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def post_list(request):
    try:
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
