from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.role_permissions_management.features.models import Feature
from apps.role_permissions_management.feature_actions.models import FeatureAction
from apps.role_permissions_management.feature_actions.serializers import FeatureActionSerializer
 
class FeatureActionsListAPIView(APIView):
    def get(self, request):
        try:
            features = Feature.objects.filter(features_is_active=True)
            response_data = []
 
            for feature in features:
                actions = FeatureAction.objects.filter(
                    feature_actions_features_keys=feature.features_keys,
                    feature_actions_is_active=True
                )
 
                serialized_actions = FeatureActionSerializer(actions, many=True).data
 
                feature_data = {
                    "features_keys": feature.features_keys,
                    "features_name": feature.features_name,
                    "features_actions": serialized_actions
                }
 
                response_data.append(feature_data)

 
            return Response({
                "success": True,
                "status": 200,
                "message": "Feature and actions fetched",
                "data": response_data
            }, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response({
                "success": False,
                "status": 500,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)