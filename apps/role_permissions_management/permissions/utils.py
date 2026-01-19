from apps.role_permissions_management.permissions.models import Permission

class PermissionChecker:
    def __init__(self, role_key, branch_key):

        if not role_key or not isinstance(role_key, str):
            raise ValueError("role_key must be a non-empty string")
        if not branch_key or not isinstance(branch_key, str):
            raise ValueError("branch_key must be a non-empty string")
            
        self.role_key = role_key
        self.branch_key = branch_key

    def has_permission(self, feature_key, action_key=None):
        try:
            permission = Permission.objects.filter(
                permissions_user_roles_keys=self.role_key,
                permissions_branches_unique_id=self.branch_key,
                permissions_features_keys__features_keys=feature_key,
                permissions_is_active=True,
                permissions_is_deleted=False
            ).first()

            if not permission:
                return False

            actions = permission.permissions_feature_actions_keys
            if action_key is None:
                return True


            if isinstance(actions, list):
                if all(isinstance(x, str) for x in actions):
                    print(actions)
                    return str(action_key) in actions
                
                elif all(isinstance(x, dict) for x in actions):
                    return any(
                        str(action.get('action_key')) == str(action_key) and 
                        action.get('has_permission', False)
                        for action in actions
                    )
            
            return False

        except Exception as e:
            return False