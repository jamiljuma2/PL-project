from django.urls import path
from .views import (
    AdminAssignmentsView, ApproveAssignmentView, RejectAssignmentView,
    AdminSubmissionsView, ApproveSubmissionView,
    AdminUsersView, PatchUserView,
)

urlpatterns = [
    path('admin/assignments', AdminAssignmentsView.as_view(), name='admin-assignments'),
    path('admin/assignments/<uuid:id>/approve', ApproveAssignmentView.as_view(), name='admin-assignments-approve'),
    path('admin/assignments/<uuid:id>/reject', RejectAssignmentView.as_view(), name='admin-assignments-reject'),
    path('admin/submissions', AdminSubmissionsView.as_view(), name='admin-submissions'),
    path('admin/submissions/<uuid:id>/approve', ApproveSubmissionView.as_view(), name='admin-submissions-approve'),
    path('admin/users', AdminUsersView.as_view(), name='admin-users'),
    path('admin/users/<int:id>', PatchUserView.as_view(), name='admin-users-patch'),
]