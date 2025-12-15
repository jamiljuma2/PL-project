from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdminRole
from accounts.models import User, Rating
from assignments.models import Assignment, Submission
from payments.models import WalletTransaction
from .models import AdminActionLog
from django.db import transaction


class AdminAssignmentsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        qs = Assignment.objects.all().order_by('-created_at')
        data = [{
            'id': str(a.id), 'title': a.title, 'status': a.status, 'student': a.student_id,
        } for a in qs]
        return Response(data)


class ApproveAssignmentView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, id):
        a = Assignment.objects.get(id=id)
        a.status = Assignment.Status.APPROVED
        a.save(update_fields=['status'])
        AdminActionLog.objects.create(admin=request.user, action='APPROVE_ASSIGNMENT', target=str(id))
        return Response({"detail": "Assignment approved"})


class RejectAssignmentView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, id):
        a = Assignment.objects.get(id=id)
        a.status = Assignment.Status.REJECTED
        a.save(update_fields=['status'])
        AdminActionLog.objects.create(admin=request.user, action='REJECT_ASSIGNMENT', target=str(id))
        return Response({"detail": "Assignment rejected"})


class AdminSubmissionsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        qs = Submission.objects.all().order_by('-uploaded_at')
        data = [{
            'assignment': str(s.assignment_id), 'writer': s.writer_id, 'status': s.status,
        } for s in qs]
        return Response(data)


class ApproveSubmissionView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, id):
        s = Submission.objects.get(assignment_id=id)
        with transaction.atomic():
            s.status = Submission.Status.APPROVED
            s.save(update_fields=['status'])
            a = s.assignment
            a.status = Assignment.Status.COMPLETED
            a.save(update_fields=['status'])
            # +5 rating points
            if hasattr(s.writer, 'rating'):
                s.writer.rating.add_points(5)
            AdminActionLog.objects.create(admin=request.user, action='APPROVE_SUBMISSION', target=str(id))
        return Response({"detail": "Submission approved"})


class AdminUsersView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        qs = User.objects.all().order_by('id')
        data = [{
            'id': u.id, 'username': u.username, 'email': u.email, 'role': u.role,
            'is_active': u.is_active, 'is_verified': u.is_verified,
        } for u in qs]
        return Response(data)


class PatchUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def patch(self, request, id):
        u = User.objects.get(id=id)
        for field in ['role', 'is_active', 'is_verified']:
            if field in request.data:
                setattr(u, field, request.data[field])
        u.save()
        AdminActionLog.objects.create(admin=request.user, action='PATCH_USER', target=str(id), details=str(request.data))
        return Response({"detail": "User updated"})from django.shortcuts import render

# Create your views here.
