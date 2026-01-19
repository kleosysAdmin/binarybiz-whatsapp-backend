import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.db import transaction
from apps.role_permissions_management.permissions.models import Permission
from apps.role_permissions_management.permissions.serializers import PermissionSerializer

class UserRoleListCreateView(APIView):
    @transaction.atomic
    def get(self, request):
        try:
            product_key = request.query_params.get('product_key', 'whatsapp')
            branch_key = request.headers.get('X-Branch-Key')
            
            if not branch_key:
                return Response({
                    "status": False,
                    "message": "branch key are required."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            headers = {
                "X-Product-Key": product_key,
                "X-Branch-Key": branch_key
            }
    
            url = f"{settings.AUTH_SERVICE_BASE_URL}/api/v1/roles/"
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                return Response({
                    "success": True,
                    "status": 200,
                    "message": "User Roles fetched successfully",
                    "data": response.json().get("data", [])
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "success": False,
                    "status": response.status_code,
                    "message":  response.json().get("message"),
                    "error":  response.json().get("error"),
                }, status=response.status_code)

        except Exception as e:
            return Response({
                "success": False,
                "status": 500,
                "message": "Error while connecting to connect api",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def post(self, request):
        try:
            product_key = request.query_params.get('product_key', 'whatsapp')
            branch_key = request.headers.get('X-Branch-Key')

            
            if not branch_key:
                return Response({
                    "status": False,
                    "message": "branch key are required."
                }, status=status.HTTP_400_BAD_REQUEST)

            headers = {
                "X-Product-Key": product_key,
                "X-Branch-Key": branch_key,
                "Content-Type": "application/json"
            }
 
            role_payload = {
                "user_roles_name": request.data.get("user_roles_name")
            }
 
            # Create Role in binarybiz
            role_url = f"{settings.AUTH_SERVICE_BASE_URL}/api/v1/roles/"
            role_response = requests.post(role_url, headers=headers, json=role_payload)
 
            if role_response.status_code not in [200, 201]:
                return Response({
                    "success": False,
                    "status": role_response.status_code,
                    "message": role_response.json().get("message"),
                    "error": role_response.json().get("error")
                }, status=role_response.status_code)
 
            created_role = role_response.json().get("data", {})
            role_key = created_role.get("user_roles_keys")
 
            permissions_payload = request.data.get("permissions", [])

            if not permissions_payload:
                return Response(
                    {"success": False, "error": "At least one permission must be selected"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            errors = []
 
            for perm in permissions_payload:
                perm["permissions_user_roles_keys"] = role_key
                perm["permissions_branches_unique_id"] = branch_key
                perm["permissions_is_active"] = True
 
                serializer = PermissionSerializer(data=perm, context={"request": request})
                if serializer.is_valid():
                    serializer.save()
                else:
                    errors.append(serializer.errors)
 
            return Response({
                "success": True,
                "status": 201,
                "message": "Role and permissions created",
                "data": {
                    "role": created_role,
                    "permission_errors": errors if errors else None
                }
            }, status=status.HTTP_201_CREATED)
 
        except Exception as e:
            return Response({
                "success": False,
                "status": 500,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UserRoleDetailView(APIView):

    @transaction.atomic
    def get(self, request, user_roles_keys):
        try:
            product_key = request.query_params.get('product_key', 'whatsapp')
            branch_key = request.headers.get('X-Branch-Key')

            
            if not branch_key:
                return Response({
                    "status": False,
                    "message": "branch key are required."
                }, status=status.HTTP_400_BAD_REQUEST)

            headers = {
                "X-Product-Key": product_key,
                "X-Branch-Key": branch_key
            }

            url = f"{settings.AUTH_SERVICE_BASE_URL}/api/v1/roles/{user_roles_keys}/"
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                return Response({
                    "success": True,
                    "status": 200,
                    "message": "Role fetched successfully",
                    "data": response.json().get("data", {})
                }, status=status.HTTP_200_OK)

            return Response({
                "success": False,
                "status": response.status_code,
                "message": response.json().get("message"),
                "error": response.json().get("error")
            }, status=response.status_code)

        except Exception as e:
            return Response({
                "success": False,
                "status": 500,
                "message": "Error while fetching role from CONNECT API",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def put(self, request, user_roles_keys):
        try:
            product_key = request.query_params.get('product_key', 'whatsapp')
            branch_key = request.headers.get('X-Branch-Key')

            
            if not branch_key:
                return Response({
                    "status": False,
                    "message": "branch key are required."
                }, status=status.HTTP_400_BAD_REQUEST)

            headers = {
                "X-Product-Key": product_key,
                "X-Branch-Key": branch_key,
                "Content-Type": "application/json"
            }

            url = f"{settings.AUTH_SERVICE_BASE_URL}/api/v1/roles/{user_roles_keys}/"
            response = requests.put(url, headers=headers, json=request.data)

            if response.status_code == 200:
                return Response({
                    "success": True,
                    "status": 200,
                    "message": "Role updated successfully",
                    "data": response.json().get("data", {})
                }, status=status.HTTP_200_OK)

            return Response({
                "success": False,
                "status": response.status_code,
                "message": response.json().get("message"),          
                "error": response.json().get("error")
            }, status=response.status_code)

        except Exception as e:
            return Response({
                "success": False,
                "status": 500,
                "message": "Error while updating role in CONNECT API",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def patch(self, request, user_roles_keys):
        try:

            product_key = request.query_params.get('product_key', 'whatsapp')
            branch_key = request.headers.get('X-Branch-Key')

            if not branch_key:
                return Response({
                    "status": False,
                    "message": "branch key are required."
                }, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                
                headers = {
                    "X-Product-Key": product_key,
                    "X-Branch-Key": branch_key,
                    "Content-Type": "application/json"
                }

                url = f"{settings.AUTH_SERVICE_BASE_URL}/api/v1/roles/{user_roles_keys}/"
                response = requests.patch(url, headers=headers, json=request.data)

                if response.status_code == 200:
                    
                    is_active = response.json().get('data', {}).get('is_active', True)

                    Permission.objects.filter(
                        permissions_user_roles_keys=user_roles_keys,
                        permissions_branches_unique_id=branch_key,
                        permissions_is_deleted = False
                    ).update(
                        permissions_is_active=is_active,
                        permissions_updated_by=str(request.user.id)
                    )

                    return Response({
                        "success": True,
                        "status": 200,
                        "message": "Role status and permissions updated successfully",
                        "data": response.json().get("data", {})
                    }, status=status.HTTP_200_OK)

                return Response({
                    "success": False,
                    "status": response.status_code,
                    "message": response.json().get("message"),
                    "error": response.json().get("error")
                }, status=response.status_code)

        except Exception as e:
            return Response({
                "success": False,
                "status": 500,
                "message": "Error while updating role status in CONNECT API",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def delete(self, request, user_roles_keys):
        try:
            product_key = request.query_params.get('product_key', 'whatsapp')
            branch_key = request.headers.get('X-Branch-Key')

            
            if not branch_key:
                return Response({
                    "status": False,
                    "message": "branch key are required."
                }, status=status.HTTP_400_BAD_REQUEST)

            headers = {
                "X-Product-Key": product_key,
                "X-Branch-Key": branch_key
            }

            url = f"{settings.AUTH_SERVICE_BASE_URL}/api/v1/roles/{user_roles_keys}/"
            response = requests.delete(url, headers=headers)

            if response.status_code == 200:

                Permission.objects.filter(
                    permissions_user_roles_keys=user_roles_keys,
                    permissions_branches_unique_id=branch_key,
                    permissions_is_active = True
                ).update(permissions_is_deleted=True)

                return Response({
                    "success": True,
                    "status": 200,
                    "message": "Role deleted successfully"
                }, status=status.HTTP_200_OK)

            return Response({
                "success": False,
                "status": response.status_code,
                "message": response.json().get("message"),
                "error": response.json().get("error")
            }, status=response.status_code)

        except Exception as e:
            return Response({
                "success": False,
                "status": 500,
                "message": "Error while deleting role from CONNECT API",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

