from rest_framework import serializers

from voting.models import Section


class SectionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Section
        fields = ('name', 'program_codes')
