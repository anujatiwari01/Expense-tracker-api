from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from rest_framework.response import Response

from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Category, Expense
from .serializers import CategorySerializer, ExpenseSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Prevent Swagger AnonymousUser error
        if getattr(self, "swagger_fake_view", False):
            return Category.objects.none()

        # Show only logged-in user's categories
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically attach logged-in user
        serializer.save(user=self.request.user)


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    # JSONParser = normal JSON
    # MultiPartParser/FormParser = file upload
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filterset_fields = ["category", "spent_on"]

    def get_parsers(self):
    
      if self.request.method in ["POST", "PUT", "PATCH"]:
        return [MultiPartParser(), FormParser()]
      return [JSONParser()]

    @swagger_auto_schema(
        operation_description="Send monthly expense summary to the logged-in user's email.",
        manual_parameters=[
            openapi.Parameter(
                "month",
                openapi.IN_QUERY,
                description="Month number, example: 6",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "year",
                openapi.IN_QUERY,
                description="Year, example: 2026",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
    )
    @action(detail=False, methods=["get"])
    def summary(self, request):
        month = request.query_params.get("month")
        year = request.query_params.get("year")

        if not month or not year:
            return Response(
                {"error": "Please provide month and year."},
                status=400,
            )

        expenses = Expense.objects.filter(
            user=request.user,
            spent_on__month=month,
            spent_on__year=year,
        )

        total = expenses.aggregate(total=Sum("amount"))["total"] or 0

        message = f"""
Hello {request.user.username},

Your spending summary for {month}/{year}:

Total expenses: ${total}

Thank you.
"""

        send_mail(
            subject="Monthly Expense Summary",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=False,
        )

        return Response(
            {"message": "Monthly summary email sent successfully."}
        )

    def get_queryset(self):
        # Prevent Swagger AnonymousUser error
        if getattr(self, "swagger_fake_view", False):
            return Expense.objects.none()

        queryset = Expense.objects.filter(user=self.request.user)

        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")

        if month:
            queryset = queryset.filter(spent_on__month=month)

        if year:
            queryset = queryset.filter(spent_on__year=year)

        return queryset

    def perform_create(self, serializer):
        # Automatically attach logged-in user
        serializer.save(user=self.request.user)