from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Organisation
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, OrganisationSerializer


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = RefreshToken.for_user(user)
            organisation_name = f"{user.first_name}'s Organisation"
            Organisation.objects.create(name=organisation_name, users=user)
            return Response({
                'status': 'success',
                'message': 'Registration successful',
                'data': {
                    'accessToken': str(token.access_token),
                    'user': UserSerializer(user).data
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': 'Bad request',
            'message': 'Registration unsuccessful',
            'errors': serializer.errors
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.filter(email=serializer.validated_data['email']).first()
            if user and user.check_password(serializer.validated_data['password']):
                token = RefreshToken.for_user(user)
                return Response({
                    'status': 'success',
                    'message': 'Login successful',
                    'data': {
                        'accessToken': str(token.access_token),
                        'user': UserSerializer(user).data
                    }
                }, status=status.HTTP_200_OK)
        return Response({
            'status': 'Bad request',
            'message': 'Authentication failed',
            'statusCode': 401
        }, status=status.HTTP_401_UNAUTHORIZED)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        user = User.objects.filter(id=id).first()
        if user:
            return Response({
                'status': 'success',
                'message': 'User found',
                'data': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response({
            'status': 'Bad request',
            'message': 'User not found',
            'statusCode': 404
        }, status=status.HTTP_404_NOT_FOUND)

class OrganisationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        organisations = request.user.organisations.all()
        return Response({
            'status': 'success',
            'message': 'Organisations found',
            'data': OrganisationSerializer(organisations, many=True).data
        }, status=status.HTTP_200_OK)

class OrganisationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, orgId):
        organisation = Organisation.objects.filter(org_id=orgId, users=request.user).first()
        if organisation:
            return Response({
                'status': 'success',
                'message': 'Organisation found',
                'data': OrganisationSerializer(organisation).data
            }, status=status.HTTP_200_OK)
        return Response({
            'status': 'Bad request',
            'message': 'Organisation not found',
            'statusCode': 404
        }, status=status.HTTP_404_NOT_FOUND)

class CreateOrganisationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrganisationSerializer(data=request.data)
        if serializer.is_valid():
            organisation = serializer.save()
            organisation.users.add(request.user)
            return Response({
                'status': 'success',
                'message': 'Organisation created successfully',
                'data': OrganisationSerializer(organisation).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': 'Bad Request',
            'message': 'Client error',
            'errors': serializer.errors,
            'statusCode': 400
        }, status=status.HTTP_400_BAD_REQUEST)

class AddUserToOrganisationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, orgId):
        organisation = Organisation.objects.filter(org_id=orgId, users=request.user).first()
        if not organisation:
            return Response({
                'status': 'Bad Request',
                'message': 'Organisation not found or permission denied',
                'statusCode': 404
            }, status=status.HTTP_404_NOT_FOUND)
        user_id = request.data.get('userId')
        user = User.objects.filter(user_id=user_id).first()
        if user:
            organisation.users.add(user)
            return Response({
                'status': 'success',
                'message': 'User added to organisation successfully'
            }, status=status.HTTP_200_OK)
        return Response({
            'status': 'Bad Request',
            'message': 'User not found',
            'statusCode': 404
        }, status=status.HTTP_404_NOT_FOUND)
