from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, Lesson, Subscription
from .paginators import LmsPagination
from .serializers import CourseSerializer, LessonSerializer
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsModer, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    pagination_class = LmsPagination
    serializer_class = CourseSerializer

    def get_queryset(self):
        if self.request.user.groups.filter(name='moders').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, ~IsModer]
        elif self.action in ['list', 'retrieve', 'update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsModer | IsOwner]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, ~IsModer, IsOwner]
        return [permission() for permission in self.permission_classes]


class LessonCreateAPIView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModer]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    pagination_class = LmsPagination
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.groups.filter(name='moders').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]


class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModer, IsOwner]


class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, pk=request.data.get('course_id'))
        subs = Subscription.objects.filter(user=request.user, course=course)

        if subs.exists():
            subs.delete()
            message = 'подписка удалена'
        else:
            Subscription.objects.create(user=request.user, course=course)
            message = 'подписка добавлена'

        return Response({'message': message})