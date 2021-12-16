from .models import BudgetEntry, Article
from django.contrib.auth.models import User
from rest_framework import serializers
from account.serializers import SimpleUserSerializer
from datetime import timedelta
from .models import BudgetEntry

class ArticleSerializer(serializers.ModelSerializer):
    image_processed = serializers.ImageField(read_only=True)

    class Meta:
        model = Article
        fields = ("specification", "amount", "price", "total",)
        read_only_fields = (
            "specification", 
            "amount", 
            "price",
            "total",
        )


class BudgetEntrySerializer(serializers.ModelSerializer):
    image_processed = serializers.ImageField(read_only=True)
    user = SimpleUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=User.objects.all(),
        source="user",
        default=serializers.CurrentUserDefault(),
    )
    articles = serializers.JSONField()

    """articles_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Article.objects.all(), source="articles"
    )"""
    #articles = ArticleSerializer(read_only=True)

    class Meta:
        model = BudgetEntry
        fields = (
            "id",
            "date",
            "user",
            "name",
            "user_id",
            "articles",
            "description",
            "confirmed",
            "clearingNr",
            "bankNr",
            "bankName",
            "location",
            "committee",
            "approvedKas",
            "approvedDeg",
            "payed",
            "image",
            "image_processed",
            "ipaddr",  
            "total_sum"
        )
        read_only_fields = (
            "confirmed", 
            "approvedKas",
            "approvedDeg",
            "image_processed",
            "payed",
            "ipaddr")
        extra_kwargs = {
            'image': {'write_only': True},
        }

    def create(self, validated_data):
        validated_data["ipaddr"] = self.context.get('request').META.get("REMOTE_ADDR")
        #validated_data[""]
        return BudgetEntry.objects.create(**validated_data)

    def validate_user_id(self, value):
        user = self.context["request"].user
        print(value)
        print(user)
        if user != value:
            raise serializers.ValidationError(
                "You are only allowed to add expenses for yourself."
            )
        return value

    def validate(self, attrs):
        
        print(attrs)

        if attrs["articles"] == None:
            raise serializers.ValidationError(
                "Articles can not be set to None"
            )

        return attrs


class ApprovalSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=User.objects.all(),
        source="user",
        default=serializers.CurrentUserDefault(),
    )

    """articles_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Article.objects.all(), source="articles"
    )"""
    #articles = ArticleSerializer(read_only=True)

    class Meta:
        model = BudgetEntry
        fields = (
            "id",
            "user",
            "user_id",
            "confirmed",
            "approvedKas",
            "approvedDeg",
            "payed",
        )
        read_only_fields = (
            "date",
            "confirmed", 
            "ipaddr")