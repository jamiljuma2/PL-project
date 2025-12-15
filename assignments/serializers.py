from rest_framework import serializers
from .models import Assignment, AssignmentFile, TaskClaim, Submission


class AssignmentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentFile
        fields = ["id", "file", "uploaded_at", "size_bytes"]


class AssignmentSerializer(serializers.ModelSerializer):
    files = AssignmentFileSerializer(many=True, read_only=True)

    class Meta:
        model = Assignment
        fields = ["id", "title", "description", "status", "created_at", "files"]


class AssignmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ["title", "description"]


class TaskClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskClaim
        fields = ["assignment", "writer", "claimed_at"]


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ["assignment", "writer", "file", "status", "notes", "uploaded_at"]