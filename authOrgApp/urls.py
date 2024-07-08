from django.urls import path
from .views import RegisterView, LoginView, UserDetailView, OrganisationListView, OrganisationDetailView, CreateOrganisationView, AddUserToOrganisationView

urlpatterns = [
    path('auth/register', RegisterView.as_view(), name='register'),
    path('auth/login', LoginView.as_view(), name='login'),
    path('api/users/<int:id>', UserDetailView.as_view(), name='user_detail'),
    path('api/organisations', OrganisationListView.as_view(), name='organisation_list'),
    path('api/organisations/<str:orgId>', OrganisationDetailView.as_view(), name='organisation_detail'),
    path('api/organisations', CreateOrganisationView.as_view(), name='create_organisation'),
    path('api/organisations/<str:orgId>/users', AddUserToOrganisationView.as_view(), name='add_user_to_organisation'),
]
