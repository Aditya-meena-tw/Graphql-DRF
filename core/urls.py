# myapp/urls.py
from django.urls import path
from .views import UserViewSet, task_list, task_detail, user_registration, custom_login, custom_logout,graphql_view
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from django.views.decorators.csrf import csrf_exempt
router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('api/register/', user_registration, name='user-registration'),
    path('api/login/', custom_login, name='custom-login'),
    path('api/logout/', custom_logout, name='custom-logout'),
    # Other API endpoints
    path('api/users/', UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='user-list'),
    path('api/tasks/', task_list, name='task-list'),
    path('api/tasks/<int:pk>/', task_detail, name='task-detail'),
    path('api/graphql/',csrf_exempt(graphql_view), name='graphql-view'),
]

urlpatterns += router.urls
