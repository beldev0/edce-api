from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Child
from .serializers import ChildSerializer, ChildUpdateSerializer

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def child_list_create(request):
    if request.method == 'GET':
        children = Child.objects.all().order_by('-created_at')
        serializer = ChildSerializer(children, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = ChildSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH', 'DELETE'])
@permission_classes([AllowAny])
def child_detail_update_delete(request, pk):
    # Django get_object_or_404 automatically handles UUID lookup translation from strings
    child_record = get_object_or_404(Child, pk=pk)

    if request.method == 'PATCH':
        # partial=True tells DRF that missing fields are completely acceptable
        serializer = ChildUpdateSerializer(child_record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Re-serialize with the main serializer to return the updated object payload
            full_data_serializer = ChildSerializer(child_record)
            return Response(full_data_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        child_record.delete()
        return Response({"message": "Child record deleted successfully."}, status=status.HTTP_204_NO_CONTENT)