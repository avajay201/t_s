from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from calendar import monthrange
from django.utils.timezone import localdate
from orders.models import Order
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
from utils.helpers import validate_query_params



class IncomeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_last_week_income(self, paid_orders):
        '''Compute income for the last full 7-day week.'''
        today = localdate()
        last_week_start = today - timedelta(days=today.weekday() + 7)
        last_week_end = last_week_start + timedelta(days=6)
        return f"Rs. {paid_orders.filter(created_at__date__range=(last_week_start, last_week_end)).aggregate(total_income=Sum('total_price'))['total_income'] or 0:.2f}"

    def get_last_month_income(self, paid_orders):
        '''Compute income for the last calendar month.'''
        today = localdate()
        first_day_current_month = today.replace(day=1)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        first_day_last_month = last_day_previous_month.replace(day=1)
        return f"Rs. {paid_orders.filter(created_at__date__range=(first_day_last_month, last_day_previous_month)).aggregate(total_income=Sum('total_price'))['total_income'] or 0:.2f}"

    def get(self, request):
        valid_param_keys = ['start_date', 'end_date', 'date']
        param_status = validate_query_params(valid_param_keys, list(request.query_params.keys()))
        if not param_status:
            return Response({'error': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        specific_date = request.query_params.get('date')

        orders = Order.objects.filter(seller__user=request.user)
        multi_income = True

        if start_date or end_date or specific_date:
            try:
                if specific_date:
                    specific_date = datetime.strptime(specific_date.strip(), '%Y-%m-%d').date()
                    orders = orders.filter(created_at__date=specific_date)
                elif start_date and end_date:
                    start_date = datetime.strptime(start_date.strip(), '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date.strip(), '%Y-%m-%d').date()
                    orders = orders.filter(created_at__date__range=[start_date, end_date])
                else:
                    return Response({'error': 'Please provide either a specific date or a date range (start_date and end_date).'},
                                    status=status.HTTP_400_BAD_REQUEST)

            except:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
            multi_income = False

        paid_orders = orders.filter(order_status='PAID')
        all_orders = len(orders)
        failed_orders = orders.filter(order_status='FAILED').count()
        pending_orders = orders.filter(order_status='PENDING').count()
        cancelled_orders = orders.filter(order_status='CANCELLED').count()
        completed_orders = len(paid_orders)

        income_data = {
            'all_orders': all_orders,
            'failed_orders': failed_orders,
            'cancelled_orders': cancelled_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'total_income': 'Rs. {:.2f}'.format(paid_orders.aggregate(total_income=Sum('total_price'))['total_income'] or 0),
            }
        if multi_income:
            income_data['today_income'] = 'Rs. {:.2f}'.format(paid_orders.filter(created_at__date=localdate()).aggregate(total_income=Sum('total_price'))['total_income'] or 0)
            income_data['last_week_income'] = self.get_last_week_income(paid_orders)
            income_data['last_month_income'] = self.get_last_month_income(paid_orders)

        return Response(income_data, status=status.HTTP_200_OK)


class IncomeGraphAPIView(APIView):
    def get(self, request):
        valid_param_keys = ['period', 'proceed', 'reference_date', 'reference_year']
        param_status = validate_query_params(valid_param_keys, list(request.query_params.keys()))
        if not param_status:
            return Response({'error': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)

        period = request.query_params.get('period', 'daily')
        proceed = request.query_params.get('proceed')
        reference_date = request.query_params.get('reference_date', localdate().replace(day=1).strftime("%Y-%m-%d"))
        reference_year = request.query_params.get('reference_year', localdate().strftime("%Y"))

        orders = Order.objects.filter(seller__user=request.user, order_status='PAID')

        try:
            current_date = datetime.strptime(reference_date, "%Y-%m-%d").date()
            reference_year = datetime.strptime(reference_year, "%Y").year
        except Exception as e:
            print('Error:', e)
            if reference_year:
                return Response({'error': 'Invalid reference year format. Use YYYY'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'error': 'Invalid reference date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

        response_data = {}

        if period == 'daily':
            current_date = self._handle_daily_period(request, current_date, proceed)
            response_data = self.__get_daily_data(current_date, orders)
        elif period == 'weekly':
            current_date = self._handle_weekly_period(request, current_date, proceed)
            response_data = self.__get_weekly_data(request, current_date, orders)
        elif period == 'monthly':
            filter_year = datetime.now().year
            filter_month = datetime.now().month
            filter_months = list(range(1, filter_month + 1))
            if proceed and proceed == 'back':
                filter_year = reference_year - 1
                if filter_year == request.user.seller.created_at.year:
                    filter_month = request.user.seller.created_at.month
                    filter_months = list(range(filter_month, 13))
            elif proceed and proceed == 'next':
                filter_year = reference_year + 1
                filter_month = 12
                filter_months = list(range(1, filter_month + 1))

            filter_data = (
                orders
                .filter(created_at__year=filter_year, created_at__month__in=filter_months)
                .annotate(month=TruncMonth('created_at'))
                .values('month')
                .annotate(total=Sum('total_price'))
                .order_by('month')
            )
            data = [
                {
                    "month": entry["month"].strftime("%b %Y"),
                    "total": f"Rs. {entry['total']:.2f}"
                }
                for entry in filter_data
            ]
            
            back_exists = orders.filter(created_at__year=filter_year - 1).exists()
            next_exists = orders.filter(created_at__year=filter_year + 1).exists()
            response_data['data'] = data
            response_data['reference_year'] = reference_year
            response_data['back_exists'] = back_exists
            response_data['next_exists'] = next_exists
        elif period == 'yearly':
            filter_data = orders.annotate(year=TruncYear('created_at')).values('year').annotate(total=Sum('total_price')).order_by('year')
            response_data = [
                {
                    "year": entry["year"].strftime("%Y"),
                    "total": f"Rs. {entry['total']:.2f}"
                }
                for entry in filter_data
            ]
        else:
            return Response({'error': 'Invalid period.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(response_data, status=status.HTTP_200_OK)

    def _handle_daily_period(self, request, current_date, proceed):
        if proceed == 'back':
            current_date = (current_date - timedelta(days=1)).replace(day=1)
        elif proceed == 'next':
            days_in_month = monthrange(current_date.year, current_date.month)[1]
            current_date = current_date + timedelta(days=days_in_month)
        return current_date

    def __get_daily_data(self, current_date, orders):
        month_start = current_date
        month_end = month_start.replace(day=monthrange(month_start.year, month_start.month)[1])
        data = orders.filter(created_at__date__range=[month_start, month_end]) \
            .annotate(date=TruncDate('created_at')) \
            .values('date') \
            .annotate(total=Sum('total_price')) \
            .order_by('date')

        income_data = {}
        for record in data:
            formatted_date = record['date'].strftime("%d %b")
            income_data[formatted_date] = f"Rs. {record['total']:.2f}"
        month_name = current_date.strftime("%B %Y")

        previous_month_start = (month_start.replace(day=1) - timedelta(days=1)).replace(day=1)
        next_month_start = (month_end.replace(day=1) + timedelta(days=31)).replace(day=1)
        back_exists = orders.filter(created_at__date__lt=previous_month_start).exists()
        next_exists = orders.filter(created_at__date__gte=next_month_start).exists()
        data = {
            "month": month_name,
            "reference_date": current_date.strftime("%Y-%m-%d"),
            "income_data": income_data,
            "back": back_exists,
            "next": next_exists
        }
        return data

    def _handle_weekly_period(self, request, current_date, proceed):
        if proceed == 'back':
            current_date = (current_date.replace(day=1) - timedelta(days=1)).replace(day=1)
        elif proceed == 'next':
            days_in_month = monthrange(current_date.year, current_date.month)[1]
            current_date = current_date + timedelta(days=days_in_month)
        return current_date

    def __get_weekly_data(self, request, current_date, orders):
        month_start = current_date.replace(day=1)
        month_end = month_start.replace(day=monthrange(month_start.year, month_start.month)[1])

        data = orders.filter(created_at__date__range=[month_start, month_end]) \
            .annotate(week_start=TruncWeek('created_at')) \
            .values('week_start') \
            .annotate(total=Sum('total_price')) \
            .order_by('week_start')

        income_data = {}
        week_start_date = month_start
        while week_start_date <= month_end and week_start_date < localdate():
            week_end_date = min(week_start_date + timedelta(days=6), month_end)
            if week_end_date >= request.user.seller.created_at.date():
                week_label = f"{week_start_date.strftime('%d %b')} - {week_end_date.strftime('%d %b')}"
                matching_week = next((record for record in data if record['week_start'].date() >= week_start_date and record['week_start'].date() <= week_end_date), None)
                total_income = matching_week['total'] if matching_week else 0.00
                income_data[week_label] = f"Rs. {total_income:.2f}"

            week_start_date += timedelta(days=7)

        previous_week_start = month_start - timedelta(days=7)
        next_week_start = month_end + timedelta(days=1)

        back_exists = orders.filter(created_at__date__lt=previous_week_start).exists()
        next_exists = orders.filter(created_at__date__gte=next_week_start).exists()

        return {
            "month": current_date.strftime("%B %Y"),
            "reference_date": current_date.strftime("%Y-%m-%d"),
            "income_data": income_data,
            "back": back_exists,
            "next": next_exists
        }
