from . import models
from . import forms
from .decorators import user_is_authenticated, allowed_users
import csv
from datetime import timedelta
from datetime import date
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import render, redirect
from django.http.response import HttpResponseRedirect
from django.http import JsonResponse
from django.utils import timezone
from pathlib import Path
import os
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
        profile = models.Profile.objects.get(pk = id)
        profile.first_time = False
        profile.save()
        profile = forms.EditProfile(request.POST, request.FILES , instance = profile)
        if profile.is_valid():
            profile.save()
            messages.success(request, 'Edited profile successfully')
        else:
            for field in profile.errors.values():
                for error in field:
                    messages.error(request, error)
    context["profile"] = models.Profile.objects.get(pk = id)
    return render(request, 'ad/edit_profile.html', context)


@login_required
@allowed_users(allowed_roles=['ADMIN'])
def delete_user(request, id):
    user = User.objects.get(pk = id)
    messages.success(request, 'Deleting acount succeed')
    user.delete()
    return redirect("user")

# ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN-ADMIN
# --------HOME--------
@login_required
def home(request):
    context = context_data()
    context['page_title'] = 'Admin Home'
    return render(request, 'ad/home.html', context)

# --------CATEGORY--------
@login_required
def category(request):
    context = context_data()
    context['page_title'] = 'Categories'
    context['category'] = models.Category.objects.all()
    return render(request, 'ad/category.html', context)

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def manage_category(request, id = None):
    context = context_data()
    context['page_title'] = 'Manage Categories'
    if id:
        context['category'] = models.Category.objects.get(pk = id)
        context['type'] = 'Save'
    else:
        context['category'] = {}
        context['type'] = 'Add'
    return render(request, 'ad/manage_category.html', context)

@allowed_users(allowed_roles=['ADMIN'])
def save_category(request):
    if request.method == "POST":
        post = request.POST
        if post['id']:
            category = models.Category.objects.get(pk = post['id'])
            category = forms.SaveCategory(request.POST,request.FILES, instance=category)
        else:
            category = forms.SaveCategory(request.POST,request.FILES)
        if category.is_valid():
            category.save()
            messages.success(request, 'New category added')
        else:
            for field in category.errors.values():
                for error in field:
                    messages.error(request, error)
        return HttpResponseRedirect('/category/')
    else:
        pass

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def delete_category(request, id):
    category = models.Category.objects.get(pk = id)
    try:
        os.remove(category.image.path)
    except:
        pass
    category.delete()
    return HttpResponseRedirect('/category/')

@login_required
def view_category(request, id):
    context = context_data()
    context['page_title'] = 'View Categories'
    context['category'] = models.Category.objects.get(pk = id)
    return render(request, 'ad/view_category.html', context)

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def export_category(request):
    category = models.Category.objects.all()
    file = open('export/category.csv','w',encoding='utf-8',newline='')
    writer = csv.writer(file, delimiter=';',quoting=csv.QUOTE_ALL)
    writer.writerow(['Name', 'Description','Image'])
    for cat in category:
        writer.writerow([
            cat.name,
            cat.description,
            cat.image,
        ])
    file.close()
    return HttpResponseRedirect('/category/')

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def import_category(request):
    if request.method == "POST":
        file = request.FILES["csv_file"]
        storage = FileSystemStorage()
        filepath = storage.path(storage.save(file.name, file))
        with open(filepath, "r", encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=";")
            data = list(reader)
            if len(data[0]) == 3:
                csvfile.seek(0)
                try:
                    for row in reader:
                        category = models.Category()
                        category.name = str(row[0])
                        category.description = str(row[1])
                        category.image = "images/categoryCover/"+row[2]
                        try:
                            models.Category.objects.get(name=category.name)
                            messages.warning(request, message='This category name already exists.')
                        except:
                            category.save()
                            messages.success(request,message='Import succesfully')
                except:
                    messages.warning(request, message ='Wrong .csv input')
            else:
                messages.warning(request, message ='The number of fields value in the imported file does not match the number of fields')
        os.remove(filepath)
    return render(request, 'ad/import_category.html')


# --------SOURCE TYPE--------
@login_required
def source_type(request):
    context = context_data()
    context['page_title'] = 'Source Types'
    context['source_type'] = models.SourceType.objects.all()
    return render(request, 'ad/source_type.html', context)

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def manage_source_type(request, id = None):
    context = context_data()
    context['page_title'] = 'Manage Source Type'
    if id:
        context['source_type'] = models.SourceType.objects.get(pk = id)
        context['type'] = 'Save'
    else:
        context['source_type'] = {}
        context['type'] = 'Add'
    return render(request, 'ad/manage_source_type.html', context)

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def save_source_type(request):
    if request.method == "POST":
        post = request.POST
        if post['id']:
            source_type = models.SourceType.objects.get(pk = post['id'])
            source_type = forms.SaveSourceType(request.POST, instance=source_type) 
        else:
            source_type = forms.SaveSourceType(request.POST)    
        if source_type.is_valid():
            source_type.save()
            messages.success(request, 'New source type added')
        else:
            for field in source_type.errors.values():
                for error in field:
                    messages.error(request, error)
        return HttpResponseRedirect('/source_type/')
    else:
        pass

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def delete_source_type(request, id):
    source_type = models.SourceType.objects.get(pk = id)
    source_type.delete()
    return HttpResponseRedirect('/source_type/')

@login_required
def view_source_type(request, id):
    context = context_data()
    context['page_title'] = 'View Source Types'
    context['source_type'] = models.SourceType.objects.get(pk = id)
    return render(request, 'ad/view_source_type.html', context)

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def export_source_type(request):
    source_type = models.SourceType.objects.all()
    file = open('export/source_type.csv','w',encoding='utf-8',newline='')
    writer = csv.writer(file, delimiter=',',quoting=csv.QUOTE_ALL)
    writer.writerow(['Code', 'Name', 'Description'])
    for st in source_type:
        writer.writerow([
            st.code,
            st.name,
            st.description
        ])
    file.close()
    return HttpResponseRedirect('/source_type/')

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def import_source_type(request):
    if request.method == "POST":
        file = request.FILES["csv_file"]
        storage = FileSystemStorage()
        filename = storage.save(file.name, file)

        with open(storage.path(filename), "r", encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=";")
            data = list(reader)
            if len(data[0]) == 3:
                csvfile.seek(0)
                try:
                    for row in reader:
                        source_type = forms.SaveSourceType(
                            data = {
                                'id':'1',
                                'code': row[1],
                                'name': row[0],
                                'description': row[2],
                            }
                        )
                        if source_type.is_valid():
                            source_type.save()
                            messages.success(request,message='Import succesfully')
                        else:
                            for error in source_type.errors.values():
                                messages.warning(request, error)
                except:
                    messages.warning(request, message ='Wrong .csv input')
            else:
                messages.warning(request, message ='The number of fields value in the imported file does not match the number of fields')
        os.remove(storage.path(filename))
    return render(request, 'ad/import_source_type.html')

# --------LANGUAGE------------
@login_required
def language(request):
    context = context_data()
    context['page_title'] = 'Languages'
    context['language'] = models.Language.objects.all()
    return render(request, 'ad/language.html', context)

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def manage_language(request, id = None):
    context = context_data()
    context['page_title'] = 'Manage Language'
    if id:
        context['language'] = models.Language.objects.get(pk = id)
        context['type'] = 'Save'
    else:
        context['language'] = {}
        context['type'] = 'Add'
    return render(request, 'ad/manage_language.html', context)

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def save_language(request):
    if request.method == "POST":
        post = request.POST
        if post['id']:
            language = models.Language.objects.get(pk = post['id'])
            language = forms.SaveLanguage(request.POST, instance=language) 
        else:
            language = forms.SaveLanguage(request.POST)
        if language.is_valid():
            language.save()
            messages.success(request, 'New language added')
        else:
            for field in language.errors.values():
                for error in field:
                    messages.error(request, error)
        return HttpResponseRedirect('/language/')
    else:
        pass

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def delete_language(request, id):
    language = models.Language.objects.get(pk = id)
    language.delete()
    return HttpResponseRedirect('/language/')

@login_required
def view_language(request, id):
    context = context_data()
    context['page_title'] = 'View Languages'
    context['language'] = models.Language.objects.get(pk = id)
    return render(request, 'ad/view_language.html', context)

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def export_language(request):
    language = models.Language.objects.all()
    file = open('export/language.csv','w',encoding='utf-8',newline='')
    writer = csv.writer(file, delimiter=',',quoting=csv.QUOTE_ALL)
    writer.writerow(['Code', 'Fullname'])
    for lang in language:
        writer.writerow([
            lang.code,
            lang.fullname
        ])
    file.close()
    return HttpResponseRedirect('/language/')

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def import_language(request):
    if request.method == "POST":
        file = request.FILES["csv_file"]
        storage = FileSystemStorage()
        filename = storage.save(file.name, file)

        with open(storage.path(filename), "r", encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=";")
            data = list(reader)
            if len(data[0]) == 2:
                csvfile.seek(0)
                try:
                    for row in reader:
                        language = forms.SaveLanguage(
                            data = {
                                'id':'1',
                                'fullname': row[0],
                                'code': row[1],
                            }
                        )
                        if language.is_valid():
                            language.save()
                            messages.success(request,message='Import succesfully')
                        else:
                            for error in language.errors.values():
                                messages.warning(request, error)
                except:
                    messages.warning(request, message ='Wrong .csv input')
            else:
                messages.warning(request, message ='The number of fields value in the imported file does not match the number of fields')
    return render(request, 'ad/import_language.html')


# --------BOOK--------
@login_required
def book(request):
    context = context_data()
    context['page_title'] = 'Books'
    context['book'] = models.Book.objects.all()
    return render(request, 'ad/book.html', context)

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def manage_book(request, id = None):
    context = context_data()
    context['page_title'] = 'Manage Book'
    context['category'] = models.Category.objects.all()
    if id:
        context['book'] = models.Book.objects.get(pk = id)
        context['type'] = 'Save'
    else:
        context['book'] = {}
        context['type'] = 'Add'
    context['category'] = models.Category.objects.all()
    context['sourcetype'] = models.SourceType.objects.all()
    context['language'] = models.Language.objects.all()
    return render(request, 'ad/manage_book.html', context)

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def save_book(request):
    if request.method == "POST":
        post = request.POST
        if post['id']:
            book = models.Book.objects.get(pk = post['id'])
            book = forms.SaveBook(request.POST, request.FILES, instance=book)
        else:
            book = forms.SaveBook(request.POST, request.FILES)
        if book.is_valid():
            book.save()
        else:
            for field in book.errors.values():
                for error in field:
                    messages.error(request, error)        
        return HttpResponseRedirect('/book/')
    else:
        pass

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def manage_book_request(request, order = 'id'):
    context = context_data()
    context["page_title"] = "List of book requests"
    requests = models.BookRequest.objects.all().order_by(order)
    categories = models.Category.objects.all()
    source_types = models.SourceType.objects.all()
    languages = models.Language.objects.all()
    p = Paginator(requests, 5)
    page = request.GET.get('page')
    requests = p.get_page(page)
    context["requests"] = requests
    context["categories"] = categories
    context["source_types"] = source_types
    context["languages"] = languages
    return render(request, "ad/manage_book_request.html", context)

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def view_book_request(request, id):
    context = context_data()
    context["page_title"] = "View Book Request"
    context["book_request"] = models.BookRequest.objects.get(pk=id)
    return render(request, "ad/view_book_request.html", context)

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def decline_book_request(request, id):
    book_request = models.BookRequest.objects.get(pk=id)
    book_request.status = '3'
    book_request.save(update_fields=['status'])
    messages.success(request, 'Decline successfully!')
    return HttpResponseRedirect('/book/')

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def accept_book_request(request, id):
    book_request = models.BookRequest.objects.get(pk = id)
    book_data = {
        'id': '',
        'title' : book_request.title,
        'publication_year' : book_request.publication_year,
        'author' : book_request.author,
        'category' : book_request.category.all(),
        'description' : book_request.description,
        'sourcetype' : book_request.sourcetype,
        'language' : book_request.language,
        'quantity' : 1,
    }
    book_file={
        'image' : book_request.image,
    }
    book = forms.SaveBook(data=book_data, files=book_file)
    if book.is_valid():
        book.save()
        book_request.status = '2'
        book_request.save(update_fields=['status'])
        messages.success(request, 'Accepted book request')
    else:
        for error in book.errors.values():
            messages.warning(request, error)
    return HttpResponseRedirect('/book/')


@login_required
@allowed_users(allowed_roles=['ADMIN'])
def delete_book(request, id):
    book = models.Book.objects.get(pk = id)
    try:
        os.remove(book.image.path)
    except:
        pass
    book.delete()
    return HttpResponseRedirect('/book/')

@login_required
def view_book(request, id):
    context = context_data()
    context['page_title'] = 'View Books'
    context['book'] = models.Book.objects.get(pk = id)
    return render(request, 'ad/view_book.html', context)

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def export_book(request):
    book = models.Book.objects.all()
    file = open('export/book.csv','w',encoding='utf-8',newline='')
    writer = csv.writer(file, delimiter=',',quoting=csv.QUOTE_ALL)
    writer.writerow(['Title', 'Publication year', 'Author', 'Category', 'Description', 'Source Type', 'Language', 'Image', 'Quantity'])
    for b in book:
        writer.writerow([
            b.title,
            b.publication_year,
            b.author,
            ','.join(b.category.values_list('name', flat=True)),
            b.description,
            b.sourcetype,
            b.language,
            b.image,
            b.quantity,
        ])
    file.close()
    return HttpResponseRedirect('/book/')

@login_required
@allowed_users(allowed_roles=['ADMIN'])
def import_book(request):
    if request.method == "POST":
        file = request.FILES["csv_file"]
        storage = FileSystemStorage()
        filename = storage.save(file.name, file)
        valid = True
        with open(storage.path(filename), "r", encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=";")
            data = list(reader)
            if len(data[0]) == 9:
                csvfile.seek(0)
                try:
                    for row in reader:
                        book = models.Book()
                        book.title = row[0]
                        book.author = row[1]
                        book.publication_year = int(row[2])
                        book.quantity = 0
                        book.save()
                        category_names = row[3].split(',')

                        try:
                            for names in category_names:
                                category_instance = models.Category.objects.filter(name = names).first()
                                category_id = category_instance.pk
                                book.category.add(category_id)
                        except:
                            messages.warning(request, message ='Category name does not exist in database')
                            valid = False

                        try:
                            book.sourcetype = models.SourceType.objects.get(name = row[4])
                        except:
                            messages.warning(request, message ='Source type name does not exist in database')
                            valid = False

                        try:
                            book.language = models.Language.objects.get(fullname = row[5])
                        except:
                            messages.warning(request, message ='Language name does not exist in database')
                            valid = False

                        book.description = row[6]
                        book.image = "images/bookCover/"+row[7]
                        book.quantity = int(row[8])

                        try:
                            if models.Book.objects.filter(title=book.title).count() > 1:
                                messages.warning(request, message='This book title already exists.')
                                valid = False
                        except:
                            pass

                        if book.publication_year > timezone.now().year:
                            messages.warning(request, message='Publication year exceeds current year.')
                            valid = False
                        if book.quantity < 0:
                            messages.warning(request, message='The book quantity is smaller than 0.')
                            valid = False

                        if valid == True:
                            book.save()
                            messages.success(request,message='Import book successfully')
                        else:
                            book.delete()
                except:
                    messages.warning(request, message ='Wrong .csv input')
            else:
                messages.warning(request, message ='The number of fields value in the imported file does not match the number of fields')
        os.remove(storage.path(filename))
    return render(request, 'ad/import_book.html')