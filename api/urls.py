from django.urls import path 
from . import views
from . import webhooks
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="Identity Service Endpoints",
        default_version='v1',
        description="Paths for BCR service, ignore webhook related endpoints.",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),  
)

urlpatterns = [
    path('register/', views.Register.as_view()),
    path('schema/', views.Schemas.as_view()),
    path('issue/', views.Issue.as_view()),
    path('revoke/', views.Revoke.as_view()),
    path('revokecred/', views.RevokeCred.as_view()),
    path('agent/', views.ConnectAgents.as_view()),
    path('proof/', views.VerifyUser.as_view()),
    path('credential/',views.Credential.as_view()),
    path('issuer/topic/<str:topic>/', webhooks.connections),
    path('holder/topic/<str:topic>/', webhooks.holder),
    path('verifier/topic/<str:topic>/', webhooks.proof),
    path('webhooks/topic/<str:topic>/', webhooks.user),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
