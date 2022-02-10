from django.contrib.auth.models import User
from rest_framework import serializers
from account.serializers import SimpleUserSerializer
from datetime import timedelta
from account.serializers import MeSerializer
from committee.serializers import CommitteeSerializer
from committee.models import Committee
from .models import BudgetEntry, File


class FileSerializer(serializers.ModelSerializer):
    file = serializers.FileField()

    class Meta:
        model = File
        fields = ("file","expense")
        read_only_fields=("file","expense")

class BudgetEntrySerializer(serializers.ModelSerializer):
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
        default=CommitteeSerializer(),
    )
    
    read_only_custom_model_field = serializers.CharField(source='custom_property', read_only=True)


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
            "ipaddr",  
            "total_sum",
            "comment",
        )
        read_only_fields = (
            "confirmed", 
            "approvedKas",
            "approvedDeg",
            "payed",
            "ipaddr")
        extra_kwargs = {
            
        }

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data["ipaddr"] = self.context.get('request').META.get("REMOTE_ADDR")
        instance = BudgetEntry.objects.create(**validated_data)
        
        print(request)
        print(request.FILES)
        print(request.FILES.getlist("file"))
        files = request.FILES
        
        for f in files.getlist("file"):
            mf = File.objects.create(file=f, expense=instance)
            mf.save()
        
        return instance

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