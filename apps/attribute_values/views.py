from rest_framework.views import APIView
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from apps.attribute_values.models import AttributeValue
from apps.attribute_values.serializers import AttributeValueSerializer


class AttributeValueListCreateView(APIView):
    # GET requests to fetch attribute values with filters
    @transaction.atomic
    def get(self, request):
        try:
            attribute_values = AttributeValue.objects.filter(attribute_values_is_deleted=False)
            
            # Filter by audience ID
            audience_id = request.GET.get('audience_id')
            if audience_id:
                attribute_values = attribute_values.filter(attribute_values_audiences_id=audience_id)
            
            # Filter by attribute ID
            attribute_id = request.GET.get('attribute_id')
            if attribute_id:
                attribute_values = attribute_values.filter(attribute_values_attributes_id=attribute_id)
            
            serializer = AttributeValueSerializer(attribute_values, many=True)
            return Response({
                "success": True,
                "status": 200,
                "message": "Fetched attribute value data successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "status": 500,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # POST requests to create a new attribute value
    @transaction.atomic
    def post(self, request):
        try:
            serializer = AttributeValueSerializer(data=request.data, context={"request": request})
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": 201,
                    "message": "Attribute value created successfully",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            error_message = list(serializer.errors.values())[0][0] if serializer.errors else "Invalid request."
            return Response({
                "success": False,
                "status": 400,
                "message": "Invalid Input",
                "error": error_message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                "status": 500,
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AttributeValueDetailView(APIView):
    # Retrieve attribute value by ID if not soft deleted
    @transaction.atomic
    def get(self, request, attribute_values_id):
        try:
            attribute_value = AttributeValue.objects.get(
                attribute_values_id=attribute_values_id, 
                attribute_values_is_deleted=False
            )
            serializer = AttributeValueSerializer(attribute_value)
            return Response({
                "success": True,
                "status": 200,
                "message": "Fetched Attribute Value by ID Successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Attribute Value not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                "status": 500,
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Update the attribute value
    @transaction.atomic
    def put(self, request, attribute_values_id):
        try:
            attribute_value = AttributeValue.objects.get(
                attribute_values_id=attribute_values_id, 
                attribute_values_is_deleted=False
            )
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Attribute Value not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            serializer = AttributeValueSerializer(
                attribute_value, 
                data=request.data, 
                partial=True, 
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": True,
                    "status": 200,
                    "message": "Attribute value updated successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            
            error_message = list(serializer.errors.values())[0][0] if serializer.errors else "Invalid request for update."
            return Response({
                "success": False,
                "status": 400,
                "error": error_message
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                "status": 500,
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Mark the attribute value as soft deleted
    @transaction.atomic
    def delete(self, request, attribute_values_id):
        try:
            attribute_value = AttributeValue.objects.get(
                attribute_values_id=attribute_values_id, 
                attribute_values_is_deleted=False
            )
            attribute_value.attribute_values_is_deleted = True
            attribute_value.save()

            return Response({
                "success": True,
                "status": 200,
                "message": "Attribute value deleted successfully"
            }, status=status.HTTP_200_OK)
            
        except ObjectDoesNotExist:
            return Response({
                "success": False,
                "status": 404,
                "error": "Attribute Value not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": 500,
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)