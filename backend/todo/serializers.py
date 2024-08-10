from rest_framework import serializers
from .models import Task, Step
from django.contrib.auth.models import User
from section.serializers import MemberSerializer
from section.models import Member
from section.serializers import MemberSerializer


#Tasks -----------------------------------------------------------------------------

class TaskSerializer(serializers.ModelSerializer):
    viewers = MemberSerializer(many=True, read_only=True)  # Display viewers as a list of members
    viewer_ids = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all(), source='viewers', many=True, write_only=True
    )

    class Meta:
        model = Task
        fields = '__all__'

    def create(self, validated_data):
        viewers = validated_data.pop('viewers', [])
        task = Task.objects.create(**validated_data)
        task.viewers.set(viewers)
        return task


class UpdateTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title','description','implementation_duration_hours','status', 'viewers']



#Steps -----------------------------------------------------------------------------

class AddStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ['title', 'description','start_time','end_time','status','task']


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = '__all__'

class UpdateStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ['title','description','status']

