from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.db.models.signals import post_save
from django.conf import settings
from autoslug import AutoSlugField
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db.models import Q
import datetime


class Photographer(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="photographer_user")
	# photographer = models.CharField(max_length=5, blank=True, null=True)
	# photographer_image = models.ImageField(default='default.png', upload_to='photographer_pics')
	slug = AutoSlugField(populate_from='user')
	experience = models.CharField(max_length=255, blank=False)
	devices = models.CharField(max_length=100, blank=False)
	application = models.CharField(max_length=255, blank=True)
	price = models.CharField(max_length=20, blank=False)
	
	def get_absolute_url(self):
		return "/photographers/{}".format(self.slug)

	@property
	def count_order(self):
		return Order.objects.filter(Q(status='Pending') | Q(status='Accepted'), to_user1__user=self.user).count()

	def __str__(self): 
		return f'{self.user}'

class Order(models.Model):
	to_user1 = models.ForeignKey(Photographer, related_name='to_user1', on_delete=models.CASCADE)
	from_user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='from_user1', on_delete=models.CASCADE)
	timestamp = models.DateTimeField(auto_now_add=True)
	date = models.DateField(max_length=100, blank=False)
	start_time = models.CharField(max_length=100, blank=False)
	end_time = models.CharField(max_length=100, blank=False)
	place = models.CharField(max_length=255, blank=False)
	description = models.CharField(max_length=255, blank=False) 
	status = models.CharField(default='Pending', max_length=10)

	def clean(self):
		cur_date = datetime.datetime.now()
		if self.date.year < cur_date.year or self.date.month < cur_date.month:
			raise ValidationError({'date': 'Invalid date!'})
		if self.date.month == cur_date.month:
			if self.date.day <= cur_date.day:
				raise ValidationError({'date': 'Invalid date!'})

		s_time = (int(self.start_time[0:2]))
		e_time = (int(self.end_time[0:2]))
		if e_time <= s_time:
			raise ValidationError({'end_time': 'Endtime should not be lesser than start time!'})
		if s_time + 1 == e_time:
			sm_time, em_time = int(self.start_time[3:5]), int(self.end_time[3:5])	
			if em_time < sm_time: 
				raise ValidationError({'end_time': 'Endtime should not be lesser than start time!'})
		# to check if any scheduel clashes
		orders = Order.objects.all().exclude(from_user1=self.from_user1)
		for o in orders:
			if self.to_user1_id == o.to_user1.id:
				if str(self.date)[0:10] == str(o.date)[0:10]:
					s__time = int(o.start_time[0:2])
					e__time = (int(o.end_time[0:2]) + 1)
					for this_time in range(s__time, e__time):
						if s_time == this_time:
							raise ValidationError({'start_time': f'From {s__time}:00 to {e__time}:00 is taken by someone!'})
						if e_time == (this_time - 1):
							raise ValidationError({'end_time': f'From {s_time}:00 to {e_time}:00 is taken by someone!'})

	def __str__(self):
		return "From {}, to {}".format(self.from_user1, self.to_user1)

	def get_absolute_url(self):
		return reverse('order-detail', kwargs={'pk': self.pk})


# @receiver(post_save, sender=Order)
# def change_status(sender, instance, created, **kwargs):
#     if created:
#         app, res = Order.objects.get_or_create(student=instance.student)
#         app.crr.add(instance)
#         app.save()