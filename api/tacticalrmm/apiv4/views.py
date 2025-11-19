from django.shortcuts import get_object_or_404
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from agents.models import Agent
from logs.models import PendingAction
from tacticalrmm.constants import AGENT_DEFER, PAStatus


class ChocoResultV4(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, agentid, pk):
        agent = get_object_or_404(Agent.objects.defer(*AGENT_DEFER), agent_id=agentid)
        action = get_object_or_404(PendingAction, agent=agent, pk=pk)

        results: str = request.data["results"]

        software_name = action.details["name"].lower()
        success = [
            "install",
            "of",
            software_name,
            "was",
            "successful",
            "installed",
        ]
        duplicate = [software_name, "already", "installed", "--force", "reinstall"]
        installed = False

        if all(x in results.lower() for x in success):
            installed = True
        elif all(x in results.lower() for x in duplicate):
            installed = True

        action.details["output"] = results
        action.details["installed"] = installed
        action.status = PAStatus.COMPLETED
        action.save(update_fields=["details", "status"])
        return Response("ok")


class InstallomatorResultV4(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, agentid, pk):
        agent = get_object_or_404(Agent.objects.defer(*AGENT_DEFER), agent_id=agentid)
        action = get_object_or_404(PendingAction, agent=agent, pk=pk)

        results: str = request.data["results"]

        # Check for common Installomator success indicators
        success_indicators = [
            "installed",
            "installation succeeded",
            "success",
        ]
        error_indicators = [
            "error",
            "failed",
            "not found",
            "download failed",
        ]
        installed = False

        results_lower = results.lower()

        # Check for success (and no errors)
        if any(x in results_lower for x in success_indicators):
            if not any(x in results_lower for x in error_indicators):
                installed = True

        action.details["output"] = results
        action.details["installed"] = installed
        action.status = PAStatus.COMPLETED
        action.save(update_fields=["details", "status"])
        return Response("ok")
