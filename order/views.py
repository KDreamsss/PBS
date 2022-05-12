from datetime import datetime, timezone
from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from .models import Photographer, Order
from feed.models import Post
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.conf import settings
from django.views.generic import ListView, UpdateView, DeleteView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import PhotographerRegisterForm, ProfileUpdateForm, NewOrderForm
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site 
import random

User = get_user_model()


@login_required
def photographers_list(request):
	photographers = Photographer.objects.exclude(user=request.user)	
	
	try:
		photographer = Photographer.objects.get(user=request.user)
		context = {
			'photographers': photographers,
			'photographer': photographer
				}
	except:
		context = {'photographers': photographers}
		
	return render(request, "order/photographer_list.html", context)

@login_required
def create_photographer(request):
	if request.method == 'POST':
		data = request.POST.dict()
		data['user'] = request.user
		form = PhotographerRegisterForm(data, request.FILES)
		print("Create photographer called", data, form.errors, form.is_valid())
		if form.is_valid():
			Photographer.objects.create(user=request.user, experience=data["experience"], devices=data["devices"], application=data["application"], price=data["price"])
			username = form.cleaned_data.get('username')
			messages.success(request, f'Successfully become a photographer!')
			return redirect('photographers_list')
	else:
		form = PhotographerRegisterForm()
	return render(request, 'order/register_photographer.html', {'form':form})

@login_required
def photographer_profile(request):
	photographer = Photographer.objects.get(user=request.user)
	context = {'photographer': photographer}
	return render(request, "order/photographer_profile.html", context)

@login_required
def edit_photographer(request):
	if request.method == 'POST':
		p_form = ProfileUpdateForm(request.POST, instance=request.user.photographer_user)
		if p_form.is_valid():
			p_form.save()
			messages.success(request, f'Your account has been updated!')
			return redirect('photographers_list')
	else:
		p_form = ProfileUpdateForm()
	context ={
		'p_form': p_form,
	}
	return render(request, 'order/edit_photographer.html', context)

@login_required
def search_photographers(request):
	query = request.GET.get('q')
	object_list = User.objects.filter(username__icontains=query)
	context ={
		'photographers': object_list
	}
	return render(request, "order/search_photographers.html", context)

class OrderListView(ListView):
	model = Order
	template_name = 'order/order_list.html'
	context_object_name = 'orders'
	ordering = ['-timestamp']
	paginate_by = 10

	def get_queryset(self):
		return Order.objects.filter(date__gte=datetime.now())

class HistoryOrderListView(ListView):
	model = Order
	template_name = 'order/order_history.html'
	context_object_name = 'orders'
	ordering = ['-timestamp']
	paginate_by = 10

	def get_queryset(self):
		return Order.objects.filter(date__lte=datetime.now())

# Use it in future for the history or personal check list. 
# class UserOrderListView(LoginRequiredMixin, ListView):
# 	model = Order
# 	template_name = 'order/user_orders.html'
# 	context_object_name = 'orders'
# 	paginate_by = 10

# 	def get_context_data(self, **kwargs):
# 		context = super(UserOrderListView, self).get_context_data(**kwargs)
# 		return context

# 	def get_queryset(self):
# 		user = get_object_or_404(User, username=self.kwargs.get('username'))
# 		return Order.objects.filter(user==user).order_by('-timestamp')

@login_required
def order_detail(request, pk):
	order = get_object_or_404(Order, pk=pk)
	return render(request, 'order/order_detail.html', {'order':order})

@login_required
def create_order(request, to_user_id):
	user = request.user # customer
	photographer = Photographer.objects.get(id=to_user_id)
	if request.method == "POST":	
		data = request.POST.dict()
		# data['to_user1'] = photographer
		# data['from_user1'] = user
		form = NewOrderForm(request.POST, photographer=photographer, customer=user)
		if form.is_valid():	
			Order.objects.create(
				to_user1=photographer, from_user1=user, date=data["date"], start_time=data["start_time"], 
				end_time=data["end_time"], place=data["place"], description=data["description"]
			)
			messages.success(request, f'Ordered Successfully')
			return redirect('order')
		else: messages.error(request, form.errors)
	form = NewOrderForm(photographer=photographer, customer=user)
	return render(request, 'order/create_order.html', {'form':form})

class OrderUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Order
	# fields = '__all__'
	fields = ['date', 'start_time', 'end_time', 'place', 'description' ]
	# form_class = NewOrderForm
	template_name = 'order/create_order.html'

	def form_valid(self, form):
		form.instance.user_name = self.request.user
		return super().form_valid(form)

	def test_func(self):
		order = self.get_object()
		if self.request.user == order.from_user1:
			return True
		return False

@login_required
def order_delete(request, pk):
	order = Order.objects.get(pk=pk)
	if request.user == order.from_user1:
		Order.objects.get(pk=pk).delete()
	return redirect('order')

@login_required
def order_reject(request, pk):
	order = Order.objects.get(pk=pk)
	if request.user == order.to_user1.user:
		order.status = 'Rejected'
		order.save()
	return redirect('order')


@login_required
def order_accept(request, pk):
	order = Order.objects.get(pk=pk)
	if request.user == order.to_user1.user:
		order.status = 'Accepted'
		order.save()
	return redirect('order')