from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.contrib import messages

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


class RequestHistoryViewSet(viewsets.ModelViewSet):
    """ViewSet برای Request History - با قابلیت حذف و اجرای مجدد"""
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

    @action(detail=True, methods=['post'])
    def re_execute(self, request, pk=None):
        """اجرای مجدد درخواست از تاریخچه"""
        history = self.get_object()
        
        # ایجاد درخواست موقت برای اجرای مجدد
        temp_request_data = {
            'method': history.method,
            'url': history.url.split('?')[0],  # حذف پارامترهای قبلی
            'headers': history.headers,
            'body': history.body
        }
        
        try:
            new_history = execute_quick_request(temp_request_data, request.user)
            serializer = RequestHistorySerializer(new_history, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'خطا در اجرای مجدد درخواست: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        """پاک کردن تمام تاریخچه کاربر"""
        deleted_count = RequestHistory.objects.filter(user=request.user).count()
        RequestHistory.objects.filter(user=request.user).delete()
        
        return Response({
            'message': f'{deleted_count} مورد از تاریخچه پاک شد.',
            'deleted_count': deleted_count
        }, status=status.HTTP_200_OK)


class SavedResponseViewSet(viewsets.ModelViewSet):
    """ViewSet برای Saved Response"""
    serializer_class = SavedResponseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedResponse.objects.filter(user=self.request.user)


@api_view(['POST'])
def quick_request(request):
    """اجرای درخواست سریع بدون ذخیره - بدون نیاز به لاگین"""
    serializer = QuickRequestSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        try:
            # اگر کاربر لاگین نباشد، user رو None می‌گذاریم
            user = request.user if request.user.is_authenticated else None
            history = execute_quick_request(serializer.validated_data, user)
            response_serializer = RequestHistorySerializer(history, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'خطا در اجرای درخواست: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def dashboard_stats(request):
    """آمار داشبورد - بدون نیاز به لاگین"""
    if request.user.is_authenticated:
        user = request.user
        stats = {
            'total_collections': Collection.objects.filter(user=user).count(),
            'total_environments': Environment.objects.filter(user=user).count(),
            'recent_requests': RequestHistory.objects.filter(user=user).order_by('-executed_at')[:5]
        }
        
        # سریالایز کردن recent_requests
        recent_serializer = RequestHistorySerializer(
            stats['recent_requests'], 
            many=True, 
            context={'request': request}
        )
        stats['recent_requests'] = recent_serializer.data
    else:
        # اگر لاگین نباشد، آمار خالی برگردان
        stats = {
            'total_collections': 0,
            'total_environments': 0,
            'recent_requests': [],
            'message': 'برای مشاهده آمار وارد شوید'
        }
    
    return Response(stats)


# Views برای Frontend
def index(request):
    """صفحه اصلی - بدون نیاز به لاگین"""
    return render(request, 'request/dashboard_new.html')


@login_required
def collections(request):
    """صفحه کالکشن‌ها - نیاز به لاگین"""
    if not request.user.is_authenticated:
        messages.warning(request, 'برای مشاهده کالکشن‌ها باید وارد شوید')
        return redirect('login')
    
    user_collections = Collection.objects.filter(user=request.user)
    return render(request, 'request/collections.html', {
        'collections': user_collections
    })


@login_required
def history(request):
    """صفحه تاریخچه - نیاز به لاگین"""
    if not request.user.is_authenticated:
        messages.warning(request, 'برای مشاهده تاریخچه باید وارد شوید')
        return redirect('login')
    
    user_history = RequestHistory.objects.filter(user=request.user).order_by('-executed_at')[:50]
    return render(request, 'request/history.html', {
        'history': user_history
    })


@login_required
def environments(request):
    """صفحه محیط‌ها - نیاز به لاگین"""
    if not request.user.is_authenticated:
        messages.warning(request, 'برای مشاهده محیط‌ها باید وارد شوید')
        return redirect('login')
    
    user_environments = Environment.objects.filter(user=request.user)
    return render(request, 'request/environments.html', {
        'environments': user_environments
    })


@login_required
def collection_detail(request, collection_id):
    """صفحه جزئیات کالکشن - نیاز به لاگین"""
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    return render(request, 'request/collection_detail.html', {
        'collection': collection
    })


def signup(request):
    """صفحه ثبت نام"""
    if request.user.is_authenticated:
        return redirect('request:index')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'حساب کاربری با موفقیت ایجاد شد!')
            return redirect('request:index')
        else:
            messages.error(request, 'لطفاً خطاهای زیر را بررسی کنید')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})


def custom_login(request):
    """صفحه ورود سفارشی"""
    if request.user.is_authenticated:
        return redirect('request:index')
    
    from django.contrib.auth.views import LoginView
    return LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True,
        next_page='request:index'
    )(request)
