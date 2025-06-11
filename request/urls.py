from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router برای API endpoints
router = DefaultRouter()
router.register(r'environments', views.EnvironmentViewSet, basename='environment')
router.register(r'collections', views.CollectionViewSet, basename='collection')
router.register(r'requests', views.APIRequestViewSet, basename='apirequest')
router.register(r'history', views.RequestHistoryViewSet, basename='requesthistory')
router.register(r'saved-responses', views.SavedResponseViewSet, basename='savedresponse')

app_name = 'request'

urlpatterns = [
    # Frontend Views
    path('', views.index, name='index'),
    path('collections/', views.collections, name='collections'),
    path('history/', views.history, name='history'),
    path('environments/', views.environments, name='environments'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/quick-request/', views.quick_request, name='quick-request'),
    path('api/dashboard-stats/', views.dashboard_stats, name='dashboard-stats'),
] 