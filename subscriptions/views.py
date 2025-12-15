from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsWriter
from .models import Subscription
from .serializers import SubscriptionSerializer
from payments.models import LipanaTransaction
from payments.services import trigger_stk_push


class SubscriptionPayView(APIView):
    permission_classes = [IsAuthenticated, IsWriter]

    def post(self, request):
        plan = request.data.get('plan')
        if plan not in ['P2', 'P5', 'P10']:
            return Response({"detail": "Invalid plan"}, status=status.HTTP_400_BAD_REQUEST)
        amount = {'P2': 2, 'P5': 5, 'P10': 10}[plan]
        sub, _ = Subscription.objects.get_or_create(user=request.user)
        data = trigger_stk_push(request.user.id, amount, 'SUBSCRIPTION')
        ref = data.get('reference')
        LipanaTransaction.objects.create(user=request.user, amount=amount, purpose='SUBSCRIPTION', reference=ref)
        sub.plan = plan
        sub.active = False
        sub.save(update_fields=['plan', 'active'])
        return Response({"detail": "Payment initiated", "reference": ref})


class SubscriptionStatusView(APIView):
    permission_classes = [IsAuthenticated, IsWriter]

    def get(self, request):
        sub, _ = Subscription.objects.get_or_create(user=request.user)
        return Response(SubscriptionSerializer(sub).data)
