from rest_framework import serializers
from .models import Category, Expense

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id", "created_at"]

class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    receipt = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Expense
        fields = [
            "id",
            "title",
            "amount",
            "category",
            "category_name",
            "spent_on",
            "receipt",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]