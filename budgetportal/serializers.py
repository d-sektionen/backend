import json
from datetime import timedelta
from django.contrib.auth.models import User
from rest_framework import serializers

from account.serializers import SimpleUserSerializer
from account.serializers import MeSerializer
from committee.serializers import CommitteeSerializer
from committee.models import Committee
from .models import BudgetEntry, File


class FileSerializer(serializers.ModelSerializer):
    file = serializers.FileField()

    class Meta:
        model = File
        fields = ("file", "expense")
        read_only_fields = ("file", "expense")


class BudgetEntrySerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=User.objects.all(),
        source="user",
        default=serializers.CurrentUserDefault(),
    )
    articles = serializers.JSONField()
   
    committee_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Committee.objects.all(),
        source="committee",
        default=CommitteeSerializer(),
        
    )
    committee = CommitteeSerializer(read_only=True)

    class Meta:
        model = BudgetEntry
        fields = (
            "id",
            "articles",
            "description",
            "total_sum",
            "clearingNr",
            "bankNr",
            "bankName",
            "committee",
            "committee_id",
            "name",
            "user_id",
            "user",
            "location",
            "date",
            "ipaddr",  
            "confirmed",
            "approvedKas",
            "approvedDeg",
            "payed",
            "comment",
        )
        read_only_fields = (
            "ipaddr",
            "confirmed", 
            "approvedKas",
            "approvedDeg",
            "payed",
        )

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data["ipaddr"] = self.context.get('request').META.get("REMOTE_ADDR")
        instance = BudgetEntry.objects.create(**validated_data)
        
        print(f'{request.FILES = }')
        print(f'{request.FILES.getlist("file") = }')
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

    def validate_articles(self, value: list):
        if type(value) is not list:
            raise serializers.ValidationError(
                "Articles must be a list of dictionaries."
            )

        for article in value:
            if type(article) is not dict:
                raise serializers.ValidationError(
                    "Articles must be a list of dictionaries."
                )

            spec = article.get('spec')
            amount = article.get('amount')
            price = article.get('price')
            
            if type(spec) is not str or \
                    type(int(amount)) is not int or \
                    type(float(price)) is not float:
                raise serializers.ValidationError(
                    'Each article must have the fields spec (string), amount (integer), and price (float).'
                )

        return value

    def to_representation(self, instance: BudgetEntry):
        ret = super().to_representation(instance)

        # Convert articles json string to json object
        articles = ret.get('articles')
        ret['articles'] = json.loads(str(articles).replace('\'', '"'))

        return ret


class ApprovalSerializer(serializers.ModelSerializer):
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
            "user_id",
            "user",
            "confirmed",
            "approvedKas",
            "approvedDeg",
            "payed",
        )
        read_only_fields = (
            "date",
            "ipaddr",
            "confirmed", 
        )


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
            "user_id",
            "user",
            "comment",
        )
        read_only_fields = (
            "date",
            "ipaddr",
            "confirmed", 
        )
