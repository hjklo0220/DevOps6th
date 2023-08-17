from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Topic, Post, TopicGroupUser
from .serializers import TopicSerializer, PostSerializer


@extend_schema(tags=["Topic"])
class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer

    @extend_schema(summary="새 토픽 생성")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=["get"], url_name="posts")
    def posts(self, request, *args, **kwargs):
        topic: Topic = self.get_object()
        if topic.is_private:
            qs = TopicGroupUser.objects.filter(
                group__lte=TopicGroupUser.GroupChoices.common,
                topic=topic,
                user=request.user,
            )
            if not qs.exists():
                return Response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    data="This user is not allowed to write a post on this topic",
                )
        posts = topic.posts
        serializer = PostSerializer(posts, many=True)
        return Response(data=serializer.data)


@extend_schema(tags=["Post"])
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def create(self, request: Request, *args, **kwargs):
        data = request.data
        title = data.get("title")
        topic_id = data.get("topic")
        topic = get_object_or_404(Topic, id=topic_id)
        if topic.is_private:
            qs = TopicGroupUser.objects.filter(
                group__lte=TopicGroupUser.GroupChoices.common,  # Q(group=0) | Q(group=1)
                topic=topic,
                user=request.user,
            )
            if not qs.exists():
                return Response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    data="This user is not allowed to write a post on this topic",
                )

        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            data["owner"] = request.user
            res: Post = serializer.create(data)
            return Response(
                status=status.HTTP_201_CREATED, data=PostSerializer(res).data
            )
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

        # return super().create(request, *args, **kwargs)
