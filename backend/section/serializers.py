from rest_framework import serializers, status
from django.contrib.auth.models import Group
from account.models import User
from .models import Project, Team, Member
from account.serializers import UserSerializer
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
import json



class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']



# Member ---------------------------------------------------------------------------------------------------------------------------
class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Member
        fields = ['id','user', 'is_team_leader','team','is_active','added_at', 'updated_at']


class AddMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = Member
        fields = ['id', 'user', 'is_team_leader', 'team', 'added_at', 'updated_at']

    def validate(self, data):
        user = data.get('user')
        team = data.get('team')
        is_team_leader = data.get('is_team_leader')
        
        if not team.is_active:
            raise ValidationError(
                {"Error": f"The team is not active"},
                code=status.HTTP_403_FORBIDDEN
            )
        # Check if the user is already a member of the team
        existing_member = Member.objects.filter(user=user, team=team).exists()
        
        if existing_member:
            raise ValidationError({"error": "This user is already a member of this team."})

        # Check if another team leader already exists in the team
        if is_team_leader:
            if self.instance:
                existing_team_leader = Member.objects.filter(team=team, is_team_leader=True).exclude(id=self.instance.id).first()
            else:
                existing_team_leader = Member.objects.filter(team=team, is_team_leader=True).first()

            if existing_team_leader:
                raise ValidationError({"error": "This team already has a team leader."})

        return data

    def create(self, validated_data):
        user = validated_data.pop('user')
        member = Member.objects.create(user=user, **validated_data)
        return member

class UpdateMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['is_team_leader','team', 'is_active']
#-------------------------------------------------------------------------------------------------------------------------------


# Team ---------------------------------------------------------------------------------------------------------------------------
class TeamSerializer(serializers.ModelSerializer):
    members = serializers.ListField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Team
        fields = ['id', 'project', 'name', 'slug', 'color', 'team_picture','is_active', 'members']

    def create(self, validated_data):
        # Extract the project
        project = validated_data.get('project')

        # Check if the project's status is Done or Cancelled
        if project.status in ['Done', 'Cancelled']:
            raise ValidationError(
                {"Error": f"Cannot add teams to a project that is {project.status}"},
                code=status.HTTP_403_FORBIDDEN
            )
        
        # Proceed with team creation
        members_data = validated_data.pop('members', None)

        # Handle the case where members_data is a string with escaped characters
        if isinstance(members_data, list) and len(members_data) == 1 and isinstance(members_data[0], str):
            try:
                # Decode the nested string and parse as JSON
                members_data = members_data[0].replace("\\", "")
                members = json.loads(members_data)
            except json.JSONDecodeError:
                raise ValidationError({"Error": "Invalid JSON format for members"})
        elif members_data is None:
            members = []
        else:
            members = members_data

        team = Team.objects.create(**validated_data)
        group_name = f"team_{team.name}"
        group, _ = Group.objects.get_or_create(name=group_name)
        team.group = group
        team.is_active = True
        team.save()

        # Create members for the team
        for member in members:
            member_data = {
                "user": member["id"],
                "is_team_leader": member["is_team_leader"],
                "team": team.id
            }
            member_serializer = AddMemberSerializer(data=member_data)
            if member_serializer.is_valid(raise_exception=True):
                member_serializer.save()

        return team
    
    def update(self, instance, validated_data):

        if not instance.is_active:
            raise ValidationError(
                {"Error": f"Cannot Edit this team"},
                code=status.HTTP_403_FORBIDDEN
            )
        members_data = validated_data.pop('members', None)
        # Handle the case where members_data is a string with escaped characters
        if isinstance(members_data, list) and len(members_data) == 1 and isinstance(members_data[0], str):
            try:
                # Decode the nested string and parse as JSON
                members_data = members_data[0].replace("\\", "")
                members = json.loads(members_data)
            except json.JSONDecodeError:
                raise ValidationError({"Error": "Invalid JSON format for members"})
        elif members_data is None:
            members = []
        else:
            members = members_data

       # instance.project = validated_data.get('project', instance.project)
        instance.name = validated_data.get('name', instance.name)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.color = validated_data.get('color', instance.color)
        instance.team_picture = validated_data.get('team_picture', instance.team_picture)
        instance.save()

        group_name = f"team_{instance.name}"
        group, _ = Group.objects.get_or_create(name=group_name)
        instance.group = group
        instance.save()
        if members:
            # Get the current user IDs of the team members
            current_members = set(instance.team_members.values_list('user_id', flat=True))
            members_ids = [member["id"] for member in members]
            
            # Identify and remove members who are no longer part of the team
            removed_members = [id for id in current_members if id not in members_ids]
            for id in removed_members:
                member = Member.objects.get(user__id=id, team=instance.id)
                member.delete()

            # Update or add new members
            for member in members:
                user_id = member["id"]
                
                # Add new members only
                if user_id not in current_members:
                    member_data = {
                        "user": member["id"],
                        "is_team_leader": member["is_team_leader"],
                        "team": instance.id
                    }
                    member_serializer = AddMemberSerializer(data=member_data)
                    if member_serializer.is_valid(raise_exception=True):
                        member_serializer.save()
                else:
                    # Update existing members
                    member_data = {
                        "is_team_leader": member["is_team_leader"],
                        "team": instance.id
                    }
                    existing_member = Member.objects.get(user_id=user_id, team=instance)
                    member_serializer = UpdateMemberSerializer(existing_member, data=member_data, partial=True)
                    if member_serializer.is_valid(raise_exception=True):
                        member_serializer.save()

        return instance

    


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        members = Member.objects.filter(team=instance)
        representation['members'] = MemberSerializer(members, many=True).data
        return representation
    
class UserTeamSerializer(serializers.ModelSerializer):
    is_team_leader = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = '__all__'

    def get_is_team_leader(self, obj):
        user = self.context['request'].user
        # Check if the user is a team leader in the specific team
        return Member.objects.filter(team=obj, user=user, is_team_leader=True).exists()

    def get_members(self, obj):
        members = Member.objects.filter(team=obj)
        return MemberSerializer(members, many=True, context=self.context).data

#-------------------------------------------------------------------------------------------------------------------------------



#Project--------------------------------------------------------------------------------------------------------------------------

class ProjectSerializer(serializers.ModelSerializer):
    teams = serializers.SerializerMethodField(method_name="get_teams", read_only=True)
    class Meta:
        model = Project
        fields = '__all__'

    def get_teams(self, obj):
        teams = Team.objects.filter(project=obj)
        serializer = TeamSerializer(teams, many=True)
        return serializer.data