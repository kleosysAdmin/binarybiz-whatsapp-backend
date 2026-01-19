from rest_framework import serializers
from apps.role_permissions_management.features.models import Feature
from apps.role_permissions_management.feature_actions.models import FeatureAction
 
class FeatureActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureAction
        fields = ['feature_actions_action_keys',"feature_actions_action"]
 
class FeatureWithActionsSerializer(serializers.ModelSerializer):
    feature_actions = serializers.SerializerMethodField()
 
    class Meta:
        model = Feature
        fields = ['features_keys', 'features_name', 'features_actions']
 
    def get_actions(self, obj):
        actions = FeatureAction.objects.filter(feature_actions_features_keys=obj.features_key)
        return FeatureActionSerializer(actions, many=True).data