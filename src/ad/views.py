from django.shortcuts import render, redirect
from django.contrib import messages
from django.http.response import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from . import models
from . import forms
from .decorators import user_is_authenticated, allowed_users
from datetime import timedelta
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.forms import PasswordChangeForm

# Create your views here.


def context_data():
    context = {
        "page_title": "",
        "system_name": "Wellib",
    }
    return context


# AUTHENTICATE-AUTHENTICATE-AUTHENTICATE-AUTHENTICATE-AUTHENTICATE-AUTHENTICATE-AUTHENTICATE-AUTHENTICATE


@user_is_authenticated
def login_user(request):
    context = context_data()
    context["page_title"] = "Login"
    if request.method == "POST":
        auth = authenticate(
            username=request.POST["userID"], password=request.POST["password"]
        )
        if auth is not None:
            login(request, auth)
            if request.user.profile.first_time == True:
                messages.info(request, 'Please edit your profile!')
                return redirect('edit_profile', request.user.id)
            else:
                messages.success(request, 'You have logged in!')
                return redirect('home')        
        else:
            messages.error(request, 'Login failed!')
            return render(request, "authenticate/login.html", context)        
    return render(request, "authenticate/login.html", context)


def logout_user(request):
    logout(request)
    return redirect("login")

@user_is_authenticated
def register_user(request, *args, **kwargs):
    context = context_data()
    context["page_title"] = "Register"
    if request.method == "POST":
        register_form = forms.CustomUserCreationForm(request.POST)
        if register_form.is_valid():
            register_form.save()
            messages.success(request, 'Register successfully!')
            return redirect('login')
        else:
            for error in register_form.errors.values():
                messages.error(request, error)
    return render(request, "authenticate/register.html", context)

@login_required
def edit_profile(request, id):
    context = context_data()
    context["page_title"] = "Edit Profile"
    if request.method == "POST":
        print(request.POST)
        profile = models.Profile.objects.get(pk = id)
        profile.first_time = False
        profile.save()
        profile = forms.EditProfile(request.POST, instance = profile)
        if profile.is_valid():
            profile.save()
            messages.success(request, 'Edited profile successfully')
        else:
            for field in profile.errors.values():
                for error in field:
                    messages.error(request, error)
    context["profile"] = models.Profile.objects.get(pk = id)
    return render(request, 'homepage/edit_profile.html', context)

@login_required
def edit_avatar(request, id):
    context = context_data()
    if request.method == "POST":
        profile = models.Profile.objects.get(pk = id)
        profile = forms.EditAvatar(request.POST, request.FILES, instance = profile)
        if profile.is_valid():
            profile.save()
            messages.success(request, "Edit avatar successfully")
        else:
            messages.error(request, "Can not change your avatar")
    
    context["profile"] = models.Profile.objects.get(pk = id)
    return render(request, 'homepage/edit_profile.html', context)

# ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN
# --------HOME--------
@login_required
@allowed_users(allowed_roles=['ADMIN','LIBRARIAN'])
def home(request):
    context = context_data()
    context["page_title"] = "Admin Home"
    return render(request, "ad/home.html", context)


# --------CATEGORY--------
@login_required
@allowed_users(allowed_roles=['ADMIN'])
def category(request):
    context = context_data()
    context["page_title"] = "Categories"
    context["category"] = models.Category.objects.all()
    return render(request, "ad/category.html", context)


@login_required
@allowed_users(allowed_roles=['ADMIN'])
def manage_category(request, id=None):
    context = context_data()
    context["page_title"] = "Manage Categories"
    if id:
        context["category"] = models.Category.objects.get(pk=id)
        context["type"] = "Save"
    else:
        context["category"] = {}
        context["type"] = "Add"
    return render(request, "ad/manage_category.html", context)


@login_required
@allowed_users(allowed_roles=['ADMIN'])
def save_category(request):
    if request.method == "POST":
        post = request.POST
        if post["id"]:
            category = models.Category.objects.get(pk=post["id"])
            category = forms.SaveCategory(post, instance=category)
        else:
            category = forms.SaveCategory(post)
        category.save()
        return redirect("category")
    else:
        pass


@login_required
@allowed_users(allowed_roles=['ADMIN'])
def delete_category(request, id):
    category = models.Category.objects.get(pk=id)
    category.delete()
    return redirect("category")


@login_required
@allowed_users(allowed_roles=['ADMIN'])
def view_category(request, id):
    context = context_data()
    context["page_title"] = "View Categories"
    context["category"] = models.Category.objects.get(pk=id)
    return render(request, "ad/view_category.html", context)


# --------SOURCE TYPE--------
@login_required
@allowed_users(allowed_roles=['ADMIN'])
def source_type(request):
    context = context_data()
    context["page_title"] = "Source Types"
    return render(request, "ad/source_type.html", context)


# --------LANGUAGE------------
@login_required
@allowed_users(allowed_roles=['ADMIN'])
def language(request):
    context = context_data()
    context["page_title"] = "Language"
    return render(request, "ad/language.html", context)


# --------BOOK--------
@login_required
@allowed_users(allowed_roles=['ADMIN'])
def book(request):
    context = context_data()
    context["page_title"] = "Books"
    return render(request, "ad/book.html", context)


# Librarian-Librarian-Librarian-Librarian-Librarian-Librarian-Librarian-Librarian-Librarian-Librarian

# ---------LOAN Transaction-----------
@login_required
@allowed_users(allowed_roles=['LIBRARIAN'])
def loan(request):
    context = context_data()
    context["page_title"] = "Loan Transaction"
    context["loan"] = models.LoanTransaction.objects.all()
    return render(request, "ad/loan.html", context)

@login_required
@allowed_users(allowed_roles=['LIBRARIAN'])
def manage_loan(request, id=None):
    context = context_data()
    context["page_title"] = "Manage Loan Transaction"
    context["loan"] = {}
    return render(request, "ad/manage_loan.html", context)

@login_required
@allowed_users(allowed_roles=['LIBRARIAN'])
def save_loan(request):
    if request.method == "POST":
        loan = forms.SaveTransaction(request.POST)
        if loan.is_valid():
            loan.save()
            flag = loan.check_book_status()
            if not flag:
                messages.info(request, 'Book is out of quantity')
            else:
                messages.success(request,'Adding New Transaction succeed')
            return redirect("loan")
        else:
            for field in loan.errors.values():
                for error in field:
                    messages.error(request, error)
                
            return redirect("loan")
    else:
        messages.error(request, 'No data has been sent')
        return redirect("loan")

@login_required
@allowed_users(allowed_roles=['LIBRARIAN'])
def delete_loan(request, id):
    loan = models.LoanTransaction.objects.get(pk=id)
    loan.delete()
    book = loan.book
    book.quantity += 1
    if book.quantity == 1:
        book.status = '1'
    book.save(update_fields=['quantity', 'status'])
    messages.success(request, 'Deleting transaction succeed!')
    return redirect("loan")


@login_required
@allowed_users(allowed_roles=['LIBRARIAN'])
def return_book(request, id):
    loan = models.LoanTransaction.objects.get(pk=id)
    loan.returned = True
    loan.save(update_fields=['returned'])
    book = loan.book
    book.quantity += 1
    if book.quantity == 1:
        book.status = '1'
    book.save(update_fields=['quantity', 'status'])
    messages.success(request, 'Reader returning book succeed!')
    return redirect("loan")

@login_required
@allowed_users(allowed_roles=['LIBRARIAN'])
def renew_book(request, id):
    loan = models.LoanTransaction.objects.get(pk=id)
    loan.date_expired += timedelta(7)
    loan.save(update_fields=['date_expired'])
    messages.success(request, 'Reader renew book succeed!')
    return redirect("loan")



# ---------------------Users----------------
@login_required
@allowed_users(allowed_roles=['ADMIN'])
def user(request):
    context = context_data()
    context["page_title"] = "Users"
    context["users"] = User.objects.all()
    return render(request, "ad/user.html", context)

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def manage_user(request):
    context = context_data()
    context["page_title"] = "Manage Users"
    context["user"] = {}
    context["type"] = "Add"
    return render(request, "ad/manage_user.html", context)
    
def save_profile(profile, post):
    profile.role = post['role']
    profile.first_name = post['first_name'] 
    profile.last_name = post['last_name']
    profile.email = post['email']
    profile.first_time = False
    profile.save(update_fields = ['role','first_name','last_name','email','first_time'])
    profile.init_identity()
    profile.save()

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def save_user(request):
    if request.method == "POST":
        post = request.POST
        user = User.objects.create_user(username = post['username'], password = post['password'])
        user.save()
        profile = models.Profile.objects.get(pk = user.id)
        save_profile(profile,post)
        return redirect("user")
    else:
        pass

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def delete_user(request, id):
    user = User.objects.get(pk = id)
    user.delete()
    return redirect("user")


# @login_required
# def view_user(request, id):
#     context = context_data()
#     context["page_title"] = "View Categories"
#     context["user"] = models.user.objects.get(pk=id)
#     return render(request, "ad/view_user.html", context)


# SEARCHING

def identity_search(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        search_query = request.GET.get('query', '')
        items = models.Profile.objects.filter(identity__contains=search_query)[:10]
        item_list = [item.identity for item in items]
        return JsonResponse(item_list, safe=False)
    return render(request, 'manage_loan.html')

def book_search(request):
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        search_query = request.GET.get('query', '')
        items = models.Book.objects.filter(pk__contains=search_query)[:10]
        item_list = [item.pk for item in items]
        return JsonResponse(item_list, safe=False)
    return render(request, 'manage_loan.html')

def homepage(request):
    context = {}
    categories = models.Category.objects.all()[0:6]
    context['categories'] = categories
    books = models.Book.objects.all()[0:12]
    context['books'] = books
    allcategory = models.Category.objects.all()
    context['allcategory'] = allcategory
    newbooks = models.Book.objects.all().order_by('-date_added')[0]
    context['newbooks'] = newbooks
    blogs = models.Post.objects.all().order_by('-created_at')[0:3]
    context['blogs'] = blogs
    blogs_footer = models.Post.objects.all().order_by('-created_at')[0:2]
    context['blogs_footer'] = blogs_footer
    context['categories_footer'] = models.Category.objects.all().order_by('-date_added')[0:4]
    return render(request,'homepage/index.html', context)

def events(request):
    context={}
    context['blogs'] = models.Post.objects.all()
    blogs_footer = models.Post.objects.all().order_by('-created_at')[0:2]
    context['blogs_footer'] = blogs_footer
    context['categories_footer'] = models.Category.objects.all().order_by('-date_added')[0:4]
    return render(request,'homepage/event.html', context)

def help(request):
    context = {}
    blogs_footer = models.Post.objects.all().order_by('-created_at')[0:2]
    context['blogs_footer'] = blogs_footer
    context['categories_footer'] = models.Category.objects.all().order_by('-date_added')[0:4]
    return render(request,'homepage/help.html', context)
    
def about(request):
    context = {}
    blogs_footer = models.Post.objects.all().order_by('-created_at')[0:2]
    context['blogs_footer'] = blogs_footer
    context['categories_footer'] = models.Category.objects.all().order_by('-date_added')[0:4]
    return render(request,'homepage/aboutus.html')

def blog(request, id = None):
    context = {}
    context['blog'] = models.Post.objects.all().get(pk = id)
    blog_recently = models.Post.objects.all().exclude(pk = id).order_by('-created_at')[0:3]
    context['blog_recently'] = blog_recently
    blogs_footer = models.Post.objects.all().order_by('-created_at')[0:2]
    context['blogs_footer'] = blogs_footer
    context['categories_footer'] = models.Category.objects.all().order_by('-date_added')[0:4]
    return render(request,'homepage/blog-single.html', context)

def profile(request, id = None):
    context = {}
    context['profile'] = models.Profile.objects.get(pk = id)
    context['booksloan'] = models.LoanTransaction.objects.all().filter(user = id).order_by('returned')
    blogs_footer = models.Post.objects.all().order_by('-created_at')[0:2]
    context['blogs_footer'] = blogs_footer
    context['categories_footer'] = models.Category.objects.all().order_by('-date_added')[0:4]
    return render(request,'homepage/profile.html',context)

def editprofile(request, id = None):
    context = {}
    context['profile'] = models.Profile.objects.get(pk = id)
    blogs_footer = models.Post.objects.all().order_by('-created_at')[0:2]
    context['blogs_footer'] = blogs_footer
    context['categories_footer'] = models.Category.objects.all().order_by('-date_added')[0:4]
    return render(request,'homepage/editprofile.html', context)

def bookdetail(request, id = None):
    context = {}
    book = models.Book.objects.all().get(pk = id)
    context['book'] = book
    context['categories']  = models.Category.objects.all()
    context['comments']  = models.Comment.objects.all().filter(book = id)
    context['bookralated'] = models.Book.objects.all().exclude(pk = id).filter(category__in = book.category.all())[0:6]
    blogs_footer = models.Post.objects.all().order_by('-created_at')[0:2]
    context['blogs_footer'] = blogs_footer
    context['categories_footer'] = models.Category.objects.all().order_by('-date_added')[0:4]
    return render(request,'homepage/book-single.html', context)

def save_comment(request, id = None):
    comment = forms.SaveComment(request.POST)
    if comment.is_valid():
        comment.save()
        messages.success(request,'Comment successfully')
    else:
        messages.error(request,'Something wrong')
    return redirect('bookdetail', id)

def filtervalue(post):
    searchs = post.split(' ')

    q_objects = [Q(category__name__contains = search) | Q(title__contains  = search)  | Q(author__contains  = search)  
                                                | Q(language__fullname__contains  = search) | Q(sourcetype__name__contains  = search)
                                                | Q(publication_year__contains  = search) for search in searchs]
    
    combined_q_objects = Q()
    for q_object in q_objects:
        combined_q_objects |= q_object

    filtered_objects = models.Book.objects.all().filter(combined_q_objects)

    return filtered_objects

def searchbook(request, cate = None):
    context = {}
    if request.method == "POST":
        books = filtervalue(request.POST['searchbox'])
    else:
        books = models.Book.objects.all()
        if cate != 0:
            books = books.filter(category = cate)
    context['books'] = books
    context['categories'] = models.Category.objects.all()
    context['languages'] = models.Language.objects.all()
    context['sourcetypes'] = models.SourceType.objects.all()
    blogs_footer = models.Post.objects.all().order_by('-created_at')[0:2]
    context['blogs_footer'] = blogs_footer
    context['categories_footer'] = models.Category.objects.all().order_by('-date_added')[0:4]
    return render(request,'homepage/book.html', context)
