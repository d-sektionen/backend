from .models import BudgetEntry, Article
from django.contrib.auth.models import User
from rest_framework import serializers
from account.serializers import SimpleUserSerializer
from datetime import timedelta
from account.serializers import MeSerializer
from committee.serializers import CommitteeSerializer
from committee.models import Committee
from .models import BudgetEntry, Image, ImageAlbum, File

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

class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Image
        fields = ("file",)

class ImageSerializer(serializers.ModelSerializer):
    file = serializers.FileField()

    class Meta:
        model = Image
        fields = ("image","entry")


class BudgetEntrySerializer(serializers.ModelSerializer):
    image_processed = serializers.ImageField(read_only=True)
    user = MeSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=User.objects.all(),
        source="user",
        default=serializers.CurrentUserDefault(),
    )
    articles = serializers.JSONField()
    committee = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Committee.objects.all(),
        #source="committee",
        default=CommitteeSerializer(),
    )
    #image2 = ImageSerializer()
    #list_test = serializers.ListField(child=serializers.FileField(max_length=1000000))

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
            "total_sum",
            "comment",
            "report_pdf",
            "list_test"
            #"album",
            #"file",
            #"image2"
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
            "image2": {
                "required": False,
            }
        }

    def create(self, validated_data):
        validated_data["ipaddr"] = self.context.get('request').META.get("REMOTE_ADDR")
        budget_entry = BudgetEntry.objects.create(**validated_data)
        files = validated_data.pop("list_test")
        for f in files:
            _ = File.objects.create(file=f, entry=budget_entry)

        return budget_entry

    def validate_user_id(self, value):
        user = self.context["request"].user
        
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

class CommentSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=User.objects.all(),
        source="user",
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = BudgetEntry
        fields = (
            "id",
            "user",
            "user_id",
            "comment",
        )
        read_only_fields = (
            "date",
            "confirmed", 
            "ipaddr")