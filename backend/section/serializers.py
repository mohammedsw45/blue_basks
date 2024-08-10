from rest_framework import serializers, status
from django.contrib.auth.models import Group,User
from .models import Project, Team, Member
from account.serializers import UserSerializer
from django.core.exceptions import ValidationError


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']



# Member ---------------------------------------------------------------------------------------------------------------------------
class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Member
        fields = ['id','user', 'is_team_leader','team','added_at', 'updated_at']


class AddMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = Member
        fields = ['id', 'user', 'is_team_leader', 'team', 'added_at', 'updated_at']

    def validate(self, data):
        user = data.get('user')
        team = data.get('team')
        is_team_leader = data.get('is_team_leader')

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
        fields = ['is_team_leader','team']
#-------------------------------------------------------------------------------------------------------------------------------


# Team ---------------------------------------------------------------------------------------------------------------------------
class TeamSerializer(serializers.ModelSerializer):
    members = serializers.ListField(write_only=True)

    class Meta:
        model = Team
        fields = ['id', 'project', 'name', 'members']

    
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
        members = validated_data.pop("members")
        team = Team.objects.create(**validated_data)
        group_name = f"team_{team.name}"
        group, _ = Group.objects.get_or_create(name=group_name)
        team.group = group
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
        members = validated_data.pop("members")
        instance.project = validated_data.get('project', instance.project)
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        group_name = f"team_{instance.name}"
        group, _ = Group.objects.get_or_create(name=group_name)
        instance.group = group
        instance.save()

        # Get the current user IDs of the team members
        current_members = set(instance.member_set.values_list('user_id', flat=True))

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
    class Meta:
        model = Team
        fields = ['id', 'name', 'project', 'created_at', 'updated_at']


#-------------------------------------------------------------------------------------------------------------------------------



#Project--------------------------------------------------------------------------------------------------------------------------

class ProjectSerializer(serializers.ModelSerializer):
    teams = serializers.SerializerMethodField(method_name="get_teams", read_only=True)
    class Meta:
        model = Project
        fields = ['id','name', 'color','implementation_duration_days','status', 'begin_time', 'end_time', 'created_at', 'updated_at', 'teams']

    def get_teams(self, obj):
        teams = Team.objects.filter(project=obj)
        serializer = TeamSerializer(teams, many=True)
        return serializer.data