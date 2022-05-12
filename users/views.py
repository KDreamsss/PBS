from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile
from feed.models import Post
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import HttpResponseRedirect
from .models import Profile, FriendRequest
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.http import HttpResponse  
from django.shortcuts import render, redirect  
from django.contrib.auth import login, authenticate  
from django.contrib.sites.shortcuts import get_current_site  
from django.utils.encoding import force_bytes, force_str 
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  
from django.template.loader import render_to_string  
from .token import account_activation_token  
from django.contrib.auth.models import User  
from django.core.mail import EmailMessage  
import random

User = get_user_model()

def register(request):  
    if request.method == 'POST':  
        form = UserRegisterForm(request.POST)  
        if form.is_valid() and User.objects.filter(email=request.POST['email']).exists()  != True: 
            # save form in the memory not in database  
            user = form.save(commit=False)  
            user.is_active = False  
            user.save()  
            # to get the domain of the current site  
            current_site = get_current_site(request)  
            mail_subject = 'Activation link has been sent to your email id'  
            message = render_to_string('users/acc_active_email.html', {  
                'user': user,  
                'domain': current_site.domain,  
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
                'token':account_activation_token.make_token(user),  
            })  
            to_email = form.cleaned_data.get('email')  
            email = EmailMessage(mail_subject, message, to=[to_email])  
            email.send() 
            return render(request, 'users/register_done.html')
            # return HttpResponse('Please confirm your email address to complete the registration') 
    else:  
        form = UserRegisterForm()  
    return render(request, 'users/register.html', {'form': form})  

def activate(request, uidb64, token):  
    User = get_user_model()
    try:  
        uid = force_str(urlsafe_base64_decode(uidb64))  
        user = User.objects.get(pk=uid)  
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):  
        user = None  
    if user is not None and account_activation_token.check_token(user, token):  
        user.is_active = True  
        user.save()
        return render(request, 'users/register_complete.html')  
        # return HttpResponseRedirect('Thank you for your email confirmation. Now you can login your account.')  
    else:  
        return HttpResponse('Activation link is invalid!')  



@login_required
def users_list(request):
	users = Profile.objects.exclude(user=request.user)
	sent_friend_requests = FriendRequest.objects.filter(from_user=request.user)
	sent_to = []
	friends = []
	for user in users:
		friend = user.friends.all()
		for f in friend:
			if f in friends:
				friend = friend.exclude(user=f.user)
		friends+=friend
	my_friends = request.user.profile.friends.all()
	for i in my_friends:
		if i in friends:
			friends.remove(i)
	if request.user.profile in friends:
		friends.remove(request.user.profile)
	random_list = random.sample(list(users), min(len(list(users)), 10))
	for r in random_list:
		if r in friends:
			random_list.remove(r)
	friends+=random_list
	for i in my_friends:
		if i in friends:
			friends.remove(i)
	for se in sent_friend_requests:
		sent_to.append(se.to_user)
	context = {
		'users': friends,
		'sent': sent_to
	}
	return render(request, "users/users_list.html", context)

def friend_list(request):
	p = request.user.profile
	friends = p.friends.all()
	context={
	'friends': friends
	}
	return render(request, "users/friend_list.html", context)

@login_required
def send_friend_request(request, id):
	user = get_object_or_404(User, id=id)
	frequest, created = FriendRequest.objects.get_or_create(
			from_user=request.user,
			to_user=user)
	return HttpResponseRedirect('/users/{}'.format(user.profile.slug))

@login_required
def cancel_friend_request(request, id):
	user = get_object_or_404(User, id=id)
	frequest = FriendRequest.objects.filter(
			from_user=request.user,
			to_user=user).first()
	frequest.delete()
	return HttpResponseRedirect('/users/{}'.format(user.profile.slug))

@login_required
def accept_friend_request(request, id):
	from_user = get_object_or_404(User, id=id)
	frequest = FriendRequest.objects.filter(from_user=from_user, to_user=request.user).first()
	user1 = frequest.to_user
	user2 = from_user
	user1.profile.friends.add(user2.profile)
	user2.profile.friends.add(user1.profile)
	if(FriendRequest.objects.filter(from_user=request.user, to_user=from_user).first()):
		request_rev = FriendRequest.objects.filter(from_user=request.user, to_user=from_user).first()
		request_rev.delete()
	frequest.delete()
	return HttpResponseRedirect('/users/{}'.format(request.user.profile.slug))

@login_required
def delete_friend_request(request, id):
	from_user = get_object_or_404(User, id=id)
	frequest = FriendRequest.objects.filter(from_user=from_user, to_user=request.user).first()
	frequest.delete()
	return HttpResponseRedirect('/users/{}'.format(request.user.profile.slug))

@login_required
def friend_request_list(request):
	p = request.user.profile
	you = p.user
	sent_friend_requests = FriendRequest.objects.filter(from_user=you)
	rec_friend_requests = FriendRequest.objects.filter(to_user=you)

	context = {
		'u': you,
		'sent_friend_requests': sent_friend_requests,
		'rec_friend_requests': rec_friend_requests,
	}

	return render(request, "users/friend_request_list.html", context)

@login_required
def delete_friend(request, id):
	user_profile = request.user.profile
	friend_profile = get_object_or_404(Profile, id=id)
	user_profile.friends.remove(friend_profile)
	friend_profile.friends.remove(user_profile)
	return HttpResponseRedirect('/users/{}'.format(friend_profile.slug))

@login_required
def profile_view(request, slug):
	p = Profile.objects.filter(slug=slug).first()
	u = p.user
	sent_friend_requests = FriendRequest.objects.filter(from_user=p.user)
	rec_friend_requests = FriendRequest.objects.filter(to_user=p.user)
	user_posts = Post.objects.filter(user_name=u)

	friends = p.friends.all()

	# is this user our friend
	button_status = 'none'
	if p not in request.user.profile.friends.all():
		button_status = 'not_friend'

		# if we have sent him a friend request
		if len(FriendRequest.objects.filter(
			from_user=request.user).filter(to_user=p.user)) == 1:
				button_status = 'friend_request_sent'

		# if we have recieved a friend request
		if len(FriendRequest.objects.filter(
			from_user=p.user).filter(to_user=request.user)) == 1:
				button_status = 'friend_request_received'

	context = {
		'u': u,
		'button_status': button_status,
		'friends_list': friends,
		'sent_friend_requests': sent_friend_requests,
		'rec_friend_requests': rec_friend_requests,
		'post_count': user_posts.count,
		'posts' : user_posts,
	}

	return render(request, "users/profile.html", context)

@login_required
def edit_profile(request):
	if request.method == 'POST':
		u_form = UserUpdateForm(request.POST, instance=request.user)
		p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
		if u_form.is_valid() and p_form.is_valid():
			u_form.save()
			p_form.save()
			messages.success(request, f'Your account has been updated!')
			return redirect('my_profile')
	else:
		u_form = UserUpdateForm(instance=request.user)
		p_form = ProfileUpdateForm(instance=request.user.profile)
	context ={
		'u_form': u_form,
		'p_form': p_form,
	}
	return render(request, 'users/edit_profile.html', context)

@login_required
def my_profile(request):
	p = request.user.profile
	you = p.user
	sent_friend_requests = FriendRequest.objects.filter(from_user=you)
	rec_friend_requests = FriendRequest.objects.filter(to_user=you)
	user_posts = Post.objects.filter(user_name=you).order_by('-date_posted')
	friends = p.friends.all()

	# is this user our friend
	button_status = 'none'
	if p not in request.user.profile.friends.all():
		button_status = 'not_friend'

		# if we have sent him a friend request
		if len(FriendRequest.objects.filter(
			from_user=request.user).filter(to_user=you)) == 1:
				button_status = 'friend_request_sent'

		if len(FriendRequest.objects.filter(
			from_user=p.user).filter(to_user=request.user)) == 1:
				button_status = 'friend_request_received'

	context = {
		'u': you,
		'button_status': button_status,
		'friends_list': friends,
		'sent_friend_requests': sent_friend_requests,
		'rec_friend_requests': rec_friend_requests,
		'post_count': user_posts.count,
		'posts' : user_posts,
	}

	return render(request, "users/profile.html", context)

@login_required
def search_users(request):
	query = request.GET.get('q')
	object_list = User.objects.filter(username__icontains=query)
	context ={
		'users': object_list
	}
	return render(request, "users/search_users.html", context)

@login_required
def user_delete(request, id):
	try:
		user = get_object_or_404(User, id=id)
		if request.user.is_staff:
			username = user.get_username
			current_site = get_current_site(request)
			mail_subject = 'Account has been deleted by the Admin.'
			message = render_to_string('users/email_user_delete.html', {
				'user': username,
				'domain': current_site.domain,
			})
			email = EmailMessage(mail_subject, message, to=[user.email])

			if user.delete():
				email.send()
				messages.success(request, f'Your action of delete user is success')
			else:
				messages.error(request, f'This user could not be deleted')
	except:
		messages.error(request, f'An error occured please try again...')
		
	return redirect('home')


# Create your views here.
