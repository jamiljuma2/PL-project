from django.urls import path
from .views import CreateAssignmentView, MyAssignmentsView, AvailableTasksView, ClaimTaskView, SubmitWorkView

urlpatterns = [
    # Student APIs
    path('assignments/', CreateAssignmentView.as_view(), name='assignments-create'),
    path('assignments/my', MyAssignmentsView.as_view(), name='assignments-my'),
    # Writer APIs
    path('tasks/available', AvailableTasksView.as_view(), name='tasks-available'),
    path('tasks/<uuid:id>/claim', ClaimTaskView.as_view(), name='tasks-claim'),
    path('submissions/', SubmitWorkView.as_view(), name='submissions-create'),
]