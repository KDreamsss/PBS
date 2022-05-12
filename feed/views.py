from multiprocessing import context
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .forms import NewCommentForm, NewPostForm, NewReportForm
from django.views.generic import ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Comments, Like
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, BadHeaderError
from django.views.decorators.http import require_POST
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site 
import json

class PostListView(ListView):
	model = Post
	template_name = 'feed/home.html'
	context_object_name = 'posts'
	ordering = ['-date_posted']
	paginate_by = 10
	def get_context_data(self, **kwargs):
		context = super(PostListView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated:
			liked = [i for i in Post.objects.all() if Like.objects.filter(user = self.request.user, post=i)]
			context['liked_post'] = liked
		return context

class UserPostListView(LoginRequiredMixin, ListView):
	model = Post
	template_name = 'feed/user_posts.html'
	context_object_name = 'posts'
	paginate_by = 10
	def get_context_data(self, **kwargs):
		context = super(UserPostListView, self).get_context_data(**kwargs)
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		liked = [i for i in Post.objects.filter(user_name=user) if Like.objects.filter(user = self.request.user, post=i)]
		context['liked_post'] = liked
		return context

	def get_queryset(self):
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		return Post.objects.filter(user_name=user).order_by('-date_posted')


@login_required
def post_detail(request, pk):
	post = get_object_or_404(Post, pk=pk)
	user = request.user
	is_liked =  Like.objects.filter(user=user, post=post)
	if request.method == 'POST':
		form = NewCommentForm(request.POST)
		if form.is_valid():
			data = form.save(commit=False)
			data.post = post
			data.username = user
			data.save()
			return redirect('post-detail', pk)
	else:
		form = NewCommentForm()
	return render(request, 'feed/post_detail.html', {'post':post, 'is_liked':is_liked, 'form':form})

@login_required
def comment_delete(request, pk):
	comment = Comments.objects.get(pk=pk)
	if request.user== comment.username or request.user.is_staff:
		Comments.objects.get(pk=pk).delete()

	return redirect('post-detail', comment.post.pk)

@login_required
def create_post(request):
	user = request.user
	if request.method == "POST":
		form = NewPostForm(request.POST, request.FILES)
		if form.is_valid():
			data = form.save(commit=False)
			data.user_name = user
			data.save()
			messages.success(request, f'Posted Successfully')
			return redirect('home')
	else:
		form = NewPostForm()
	return render(request, 'feed/create_post.html', {'form':form})

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Post
	fields = ['description', 'pic', 'tags']
	template_name = 'feed/create_post.html'

	def form_valid(self, form):
		form.instance.user_name = self.request.user
		return super().form_valid(form)

	def test_func(self):
		post = self.get_object()
		if self.request.user == post.user_name:
			return True
		return False

@login_required
def post_delete(request, pk):
	post = Post.objects.get(pk=pk)
	if request.user== post.user_name:
		Post.objects.get(pk=pk).delete()
	return redirect('home')

@login_required
def admin_post_delete(request, pk):
	try:
		post = Post.objects.get(pk=pk)
		if request.user.is_staff:
			user = post.user_name		
			current_site = get_current_site(request)
			mail_subject = 'Post has been deleted by the Admin.'
			message = render_to_string('feed/email_post_delete.html', {
				'user': user,
				'domain': current_site.domain,
			})
			email = EmailMessage(mail_subject, message, to=[user.email])

			if post.delete():
				email.send()
				messages.success(request, f'Your action of delete post is success')
			else:
				messages.error(request, f'Post could not be deleted')
	except:
		messages.error(request, f'An error occured please try again...')
		
	return redirect('home')


@login_required
def search_posts(request):
	query = request.GET.get('p')
	object_list = Post.objects.filter(tags__icontains=query)
	liked = [i for i in object_list if Like.objects.filter(user = request.user, post=i)]
	context ={
		'posts': object_list,
		'liked_post': liked
	}
	return render(request, "feed/search_posts.html", context)

@login_required
def like(request):
	post_id = request.GET.get("likeId", "")
	user = request.user
	post = Post.objects.get(pk=post_id)
	liked= False
	like = Like.objects.filter(user=user, post=post)
	if like:
		like.delete()
	else:
		liked = True
		Like.objects.create(user=user, post=post)
	resp = {
        'liked':liked
    }
	response = json.dumps(resp)
	return HttpResponse(response, content_type = "application/json")
    
# def report(request):
# 	if request.method == 'POST':
# 		form = NewReportForm(request.POST)
# 		if form.is_valid():
# 			subject = "Report Post by User" 
# 			body = {
# 			'first_name': form.cleaned_data['first_name'], 
# 			'last_name': form.cleaned_data['last_name'], 
# 			'email': form.cleaned_data['email_address'], 
# 			'message':form.cleaned_data['message'], 
# 			}
# 			message = "\n".join(body.values())
# 			email = form.cleaned_data['email_address']
# 			try:
# 				send_mail(subject, message, email, ['aiupbs2022@gmail.com']) 
# 			except BadHeaderError:
# 				return HttpResponse('Invalid header found.')
# 			return redirect('home')
      
# 	form = NewReportForm()
# 	return render(request, "feed/report.html", {'form':form})

def report(request):

	return render(request, "feed/report.html")
# Create your views here.
