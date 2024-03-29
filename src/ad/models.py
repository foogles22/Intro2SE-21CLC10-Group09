from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.


# -User-User--User--User--User--User--User--User--User--User--User--User--User--User--User--User--User--User-
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, blank=False, null= False)
    last_name = models.CharField(max_length=255, blank=False, null= False)
    email = models.EmailField(max_length=255, blank=False, null= False)
    identity = models.CharField(max_length=9, blank=False, null= False)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(default= timezone.now, blank=True)
    sex = models.CharField(max_length=2, choices=(('1','MALE'), ('2', 'FEMALE')), blank=True)
    profile_img = models.ImageField(upload_to=('images/avatars/'),default=('images/avatars/default.jpg'))
    first_time = models.BooleanField(null=False, default=True)
    bio = models.CharField(null=True, max_length=255, default="Edit profile for more.")
    date_joined = models.DateField(null=True, default=timezone.now)    
    class ROLE(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        READER = "READER", "Reader"
        LIBRARIAN = "LIBRARIAN", "Librarian"

    role = models.CharField(max_length=20, choices=ROLE.choices, default = ROLE.READER)

    def init_identity(self):
        if self.role == "ADMIN":
            name = 'AD'
        if self.role == "LIBRARIAN":
            name = 'LB'
        if self.role == "READER":
            name = 'RD'
        try:
            total = Profile.objects.all().filter(role=self.role)
            id_list = [each.identity for each in total]
            id_list.pop()
            number = int(id_list[-1][-1])
            number +=1
        except:
            number = 1
        self.identity = name + str(number)

    def __str__(self):
        return str(self.identity)

@receiver(post_save, sender = User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user = instance)
        user_profile.save()
        if instance.is_superuser:
            user_profile.role = "ADMIN"
            user_profile.save(update_fields=['role'])
        user_profile.init_identity()
        user_profile.save()


class ReaderRequest(models.Model):
    first_name = models.CharField(max_length=255, blank=False, null= False)
    last_name = models.CharField(max_length=255, blank=False, null= False)
    email = models.EmailField(max_length=255, blank=False, null= False)
    date_added = models.DateTimeField(null=False, default=timezone.now)
    status = models.CharField(
        max_length=2, choices=(("1", "Wait"), ("2", "Accept"), ("3", "Decline")), default="1"
    )
    def __str__(self):
        return str('Request_' + self.email)


# -ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN
class Category(models.Model):
    name = models.CharField(blank=False, null=False, max_length=500)
    description = models.TextField(blank=False, null=False, max_length=500)
    date_added = models.DateTimeField(null=False, default=timezone.now)
    image = models.ImageField(null=False, blank=False, upload_to="images/category/")

    def __str__(self):
        return str(f"{self.name}")


class SourceType(models.Model):
    code = models.CharField(blank=False, null=False, max_length=50)
    name = models.CharField(null= False, blank=False, max_length=500)
    description = models.TextField(blank=False, null=False, max_length=500)
    date_added = models.DateTimeField(null=False, default=timezone.now)

    def __str__(self):
        return str(f"{self.name}")


class Language(models.Model):
    code = models.CharField(max_length=255, blank=False, null=False)
    fullname = models.CharField(max_length=500,blank=False, null=False)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(f"{self.fullname}")


class Book(models.Model):
    title = models.CharField(blank=False, null=False, max_length=500)
    publication_year = models.IntegerField(null= False, blank=False, validators=[MaxValueValidator(timezone.now().year)])
    author = models.CharField(null= False, blank=False, max_length=500)
    category = models.ManyToManyField(Category)
    description = models.TextField(blank=False, null=False, max_length=500)
    sourcetype = models.ForeignKey(SourceType, on_delete=models.SET_NULL, null=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(null=False, blank=False, upload_to="images/books/")
    quantity = models.IntegerField(null=False, blank=False, validators=[MinValueValidator(0)])
    status = models.CharField(
        max_length=2, choices=(("1", "Active"), ("2", "Inactive")), default="1"
    )
    date_added = models.DateTimeField(null=False, default=timezone.now)

    def __str__(self):
        words = self.title.split()
        abbreviations = [word[0].upper() for word in words if word]
        return ''.join(abbreviations)
    

class BookRequest(models.Model):
    title = models.CharField(max_length=500, blank=False, null=False)
    publication_year = models.IntegerField(blank=False, null=False)
    author = models.CharField(max_length=500, blank=False, null=False)
    category = models.ManyToManyField(Category)
    description = models.TextField(max_length=500, blank=False, null=False)
    sourcetype = models.ForeignKey(SourceType, null=True, on_delete=models.SET_NULL)
    language = models.ForeignKey(Language, null=True, on_delete=models.SET_NULL)
    image = models.ImageField(null=False, blank=False, upload_to="images/books_request/")
    date_added = models.DateTimeField(null=False, default=timezone.now)   
    status = models.CharField(
        max_length=2, choices=(("1", "Wait"), ("2", "Accept"), ("3", "Decline")), default="1"
    )

    def __str__(self):
            return 'Request_' + str(self.title)

class LoanTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date_loan = models.DateTimeField(default=timezone.now, null= False)
    date_expired = models.DateTimeField(default=(timezone.now() + timedelta(7)), null= False)
    overdue = models.CharField(
        max_length=2, choices=(("0", "No"), ("1", "Yes")), default="0"
    )
    returned = models.CharField(
        max_length=2, choices=(("0", "No"), ("1", "Yes")), default="0"
    )
    renew_limit = models.IntegerField(default=1)
    class Meta:
            unique_together = ('user', 'book', 'date_loan')
    def __str__(self):
        return str(f'{self.user.profile.identity}_{self.book}')
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.profile.first_name} {self.user.profile.last_name} on {self.book.title} at {self.created_at}"
    
    
class Post(models.Model):
    title = models.CharField(max_length=500, null=False, blank=False)
    writer = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    content = models.TextField(blank=False, null=False, max_length=500)
    main_content = models.TextField(blank=False, null=False, max_length=5000)
    image_blog = models.ImageField(blank=False, null=False, upload_to="images/post/")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(f"{self.title}")
    
