from rest_framework import serializers
from .models import Task, Step
# from django.contrib.auth.models import User
from section.serializers import MemberSerializer
from section.models import Member
from section.serializers import MemberSerializer
from account.models import User


#Tasks -----------------------------------------------------------------------------

class TaskSerializer(serializers.ModelSerializer):
    steps = serializers.SerializerMethodField(method_name="get_steps", read_only=True)
    viewers = MemberSerializer(many=True, read_only=True)  # Display viewers as a list of members
    viewer_ids = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all(), source='viewers', many=True, write_only=True
    )

    class Meta:
        model = Task
        fields = '__all__'

    def validate_viewer_ids(self, viewer_ids):
        team = self.initial_data.get('team')  # Get the team from the initial data
        if team is None:
            raise serializers.ValidationError("Team must be provided.")

        team_members = Member.objects.filter(team=team)

        team_member_ids = set(team_members.values_list('id', flat=True))

        # Check if all viewer_ids are part of the team
        invalid_viewers = [viewer.id for viewer in viewer_ids if viewer.id not in team_member_ids]

        if invalid_viewers:
            raise serializers.ValidationError(f"The following viewer IDs are not part of the team: {invalid_viewers}")

        return viewer_ids

    def create(self, validated_data):
        viewers = validated_data.pop('viewers', [])
        task = Task.objects.create(**validated_data)
        task.viewers.set(viewers)
        return task

    def get_steps(self, obj):
        steps = Step.objects.filter(task=obj)
        serializer = StepSerializer(steps, many=True)
        return serializer.data



class UpdateTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title', 'description', 'implementation_duration_hours', 'status', 'viewers']

    def validate(self, attrs):
        viewer_ids = attrs.get('viewers', [])
        team = self.initial_data.get('team')  # Get the team from the initial data
        if team is None:
            raise serializers.ValidationError("Team must be provided.")


        team_members = Member.objects.filter(team=team)
        team_member_ids = set(team_members.values_list('id', flat=True))

        # Check if all viewer_ids are part of the team
        invalid_viewers = [viewer.id for viewer in viewer_ids if viewer.id not in team_member_ids]

        if invalid_viewers:
            raise serializers.ValidationError(f"The following viewer IDs are not part of the team: {invalid_viewers}")

        return attrs

    def update(self, instance, validated_data):
        viewers = validated_data.pop('viewers', None)
        instance = super().update(instance, validated_data)

        if viewers is not None:
            instance.viewers.set(viewers)

        return instance


#Steps -----------------------------------------------------------------------------

class AddStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ['title', 'description', 'status', 'task']

    def validate(self, attrs):
        task = attrs.get('task')

        # Check if the task status is 'Done' or 'Cancelled'
        if task.status in ['Done', 'Cancelled', 'Archived']:
            raise serializers.ValidationError(
                f"Cannot add a step to a task that is {task.status}"
            )
        
        return attrs


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = '__all__'

class UpdateStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ['title','description','status']


