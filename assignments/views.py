from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from accounts.permissions import IsStudent, IsWriter
from accounts.models import Notification, Rating
from subscriptions.models import Subscription
from .models import Assignment, AssignmentFile, TaskClaim, Submission
from .serializers import AssignmentSerializer, AssignmentCreateSerializer, SubmissionSerializer


class CreateAssignmentView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request):
        serializer = AssignmentCreateSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                assignment = serializer.save(student=request.user)
                # files upload via multipart input files[]
                for f in request.FILES.getlist('files'):
                    AssignmentFile.objects.create(assignment=assignment, file=f)
                Notification.objects.create(user=request.user, title='Assignment Created', body=f'Assignment {assignment.title} submitted for approval')
            return Response(AssignmentSerializer(assignment).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyAssignmentsView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        qs = Assignment.objects.filter(student=request.user).order_by('-created_at')
        return Response(AssignmentSerializer(qs, many=True).data)


class AvailableTasksView(APIView):
    permission_classes = [IsAuthenticated, IsWriter]

    def get(self, request):
        qs = Assignment.objects.filter(status=Assignment.Status.APPROVED).order_by('created_at')
        return Response(AssignmentSerializer(qs, many=True).data)


class ClaimTaskView(APIView):
    permission_classes = [IsAuthenticated, IsWriter]

    def post(self, request, id):
        assignment = get_object_or_404(Assignment, id=id)
        if assignment.status != Assignment.Status.APPROVED:
            return Response({"detail": "Task not available"}, status=status.HTTP_400_BAD_REQUEST)
        if hasattr(assignment, 'claim'):
            return Response({"detail": "Task already claimed"}, status=status.HTTP_409_CONFLICT)
        # Enforce daily task limits
        sub, _ = Subscription.objects.get_or_create(user=request.user)
        if not sub.can_claim():
            return Response({"detail": "Daily task limit reached"}, status=status.HTTP_403_FORBIDDEN)
        with transaction.atomic():
            TaskClaim.objects.create(assignment=assignment, writer=request.user)
            assignment.status = Assignment.Status.IN_PROGRESS
            assignment.save(update_fields=['status'])
            sub.register_claim()
            Notification.objects.create(user=request.user, title='Task Claimed', body=f'Assignment {assignment.title} claimed')
        return Response({"detail": "Task claimed"})


class SubmitWorkView(APIView):
    permission_classes = [IsAuthenticated, IsWriter]

    def post(self, request):
        assignment_id = request.data.get('assignment')
        assignment = get_object_or_404(Assignment, id=assignment_id)
        if assignment.status != Assignment.Status.IN_PROGRESS:
            return Response({"detail": "Cannot submit now"}, status=status.HTTP_400_BAD_REQUEST)
        if not hasattr(assignment, 'claim') or assignment.claim.writer_id != request.user.id:
            return Response({"detail": "You did not claim this task"}, status=status.HTTP_403_FORBIDDEN)
        file = request.FILES.get('file')
        if not file:
            return Response({"detail": "File required"}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            Submission.objects.update_or_create(
                assignment=assignment,
                defaults={"writer": request.user, "file": file, "status": Submission.Status.PENDING_REVIEW, "uploaded_at": timezone.now()},
            )
            Notification.objects.create(user=assignment.student, title='Submission Received', body=f'Writer submitted work for {assignment.title}')
        return Response({"detail": "Submitted for review"}, status=status.HTTP_201_CREATED)
