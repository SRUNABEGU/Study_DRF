from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.serializers import UserRegisterSerializer
from . import serializers
from . import services
from .filters import PaymentFilter
from .models import User, Payment
from .permissions import IsProfileOwner
from .serializers import UserSerializer, PaymentSerializer, UserPublicSerializer


class UserRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['paid_at']
    ordering = ['-paid_at']


class UserRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            obj = self.get_object()
            if obj != self.request.user:
                return UserPublicSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsProfileOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]


class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.PaymentCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        payment = serializer.save(
            user=self.request.user,
            amount=course.price,
            method=Payment.Method.CARD,
        )
        product = services.create_stripe_product(course.title)
        price = services.create_stripe_price(product.id, payment.amount)
        session_id, link = services.create_stripe_session(price.id)

        payment.stripe_session_id = session_id
        payment.payment_link = link
        payment.save()


class PaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk, user=request.user)
        if not payment.stripe_session_id:
            return Response({'detail': 'У платежа нет сессии Stripe'}, status=400)

        session = services.get_session(payment.stripe_session_id)
        payment.status = session.payment_status
        payment.save(update_fields=['status'])
        return Response({'id': payment.id, 'status': payment.status})
