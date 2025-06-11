from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Environment, Collection, APIRequest, RequestHistory, SavedResponse
from .serializers import (
    EnvironmentSerializer, CollectionSerializer, APIRequestSerializer,
    RequestHistorySerializer, SavedResponseSerializer, ExecuteRequestSerializer,
    QuickRequestSerializer
)
from .services import execute_api_request, execute_quick_request


class EnvironmentViewSet(viewsets.ModelViewSet):
    """ViewSet برای Environment"""
    serializer_class = EnvironmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Environment.objects.filter(user=self.request.user)


class CollectionViewSet(viewsets.ModelViewSet):
    """ViewSet برای Collection"""
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Collection.objects.filter(user=self.request.user)

    @action(detail=True, methods=['get'])
    def requests(self, request, pk=None):
        """دریافت درخواست‌های یک کالکشن"""
        collection = self.get_object()
        requests = APIRequest.objects.filter(collection=collection, user=request.user)
        serializer = APIRequestSerializer(requests, many=True, context={'request': request})
        return Response(serializer.data)


class APIRequestViewSet(viewsets.ModelViewSet):
    """ViewSet برای API Request"""
    serializer_class = APIRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = APIRequest.objects.filter(user=self.request.user)
        
        # فیلتر بر اساس کالکشن
        collection_id = self.request.query_params.get('collection')
        if collection_id:
            queryset = queryset.filter(collection_id=collection_id)
        
        # جستجو
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(url__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-updated_at')

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """اجرای درخواست"""
        api_request = self.get_object()
        
        try:
            history = execute_api_request(api_request, request.user)
            serializer = RequestHistorySerializer(history, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'خطا در اجرای درخواست: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """تاریخچه درخواست"""
        api_request = self.get_object()
        history = RequestHistory.objects.filter(
            request=api_request, 
            user=request.user
        ).order_by('-executed_at')
        
        serializer = RequestHistorySerializer(history, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """کپی کردن درخواست"""
        original_request = self.get_object()
        
        # ایجاد کپی
        new_request = APIRequest.objects.create(
            name=f"{original_request.name} - Copy",
            method=original_request.method,
            url=original_request.url,
            description=original_request.description,
            headers=original_request.headers,
            params=original_request.params,
            auth_type=original_request.auth_type,
            auth_data=original_request.auth_data,
            body_type=original_request.body_type,
            body_raw=original_request.body_raw,
            body_raw_type=original_request.body_raw_type,
            body_form_data=original_request.body_form_data,
            body_urlencoded=original_request.body_urlencoded,
            timeout=original_request.timeout,
            follow_redirects=original_request.follow_redirects,
            user=request.user,
            collection=original_request.collection,
            environment=original_request.environment,
        )
        
        serializer = APIRequestSerializer(new_request, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RequestHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet برای Request History - فقط خواندنی"""
    serializer_class = RequestHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = RequestHistory.objects.filter(user=self.request.user)
        
        # فیلتر بر اساس درخواست
        request_id = self.request.query_params.get('request')
        if request_id:
            queryset = queryset.filter(request_id=request_id)
        
        # فیلتر بر اساس وضعیت
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-executed_at')


class SavedResponseViewSet(viewsets.ModelViewSet):
    """ViewSet برای Saved Response"""
    serializer_class = SavedResponseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedResponse.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quick_request(request):
    """اجرای درخواست سریع بدون ذخیره"""
    serializer = QuickRequestSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        try:
            history = execute_quick_request(serializer.validated_data, request.user)
            response_serializer = RequestHistorySerializer(history, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'خطا در اجرای درخواست: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """آمار داشبورد"""
    user = request.user
    
    stats = {
        'total_requests': APIRequest.objects.filter(user=user).count(),
        'total_collections': Collection.objects.filter(user=user).count(),
        'total_history': RequestHistory.objects.filter(user=user).count(),
        'successful_requests': RequestHistory.objects.filter(
            user=user, 
            status='success'
        ).count(),
        'recent_requests': RequestHistory.objects.filter(user=user).order_by('-executed_at')[:5]
    }
    
    # سریالایز کردن recent_requests
    recent_serializer = RequestHistorySerializer(
        stats['recent_requests'], 
        many=True, 
        context={'request': request}
    )
    stats['recent_requests'] = recent_serializer.data
    
    return Response(stats)


# Views برای Frontend
@login_required
def index(request):
    """صفحه اصلی"""
    return render(request, 'request/index.html')


@login_required
def collections(request):
    """صفحه کالکشن‌ها"""
    user_collections = Collection.objects.filter(user=request.user)
    return render(request, 'request/collections.html', {
        'collections': user_collections
    })


@login_required
def history(request):
    """صفحه تاریخچه"""
    user_history = RequestHistory.objects.filter(user=request.user).order_by('-executed_at')[:50]
    return render(request, 'request/history.html', {
        'history': user_history
    })


@login_required
def environments(request):
    """صفحه محیط‌ها"""
    user_environments = Environment.objects.filter(user=request.user)
    return render(request, 'request/environments.html', {
        'environments': user_environments
    })
