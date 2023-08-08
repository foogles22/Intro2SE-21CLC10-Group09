from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [

    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    # ----------------------------------READER------------------------------------------------
    # path('homepage/', views.homepage, name = 'homepage'), 

    # ----------------------------------LIBRARIAN--------------------------------------------
    # --------Borrowing Transactions-------
    path('loan/', views.loan, name = 'loan'),
    path('loan/<str:order>', views.loan, name = 'loan'),
    path('manage_loan/', views.manage_loan, name = 'manage_loan'),
    path('manage_loan/<int:id>', views.manage_loan, name = 'manage_loan_pk'),
    path('save_loan/', views.save_loan, name = 'save_loan'),
    path('delete_loan/<int:id>', views.delete_loan, name = 'delete_loan'),
    path('identity_search/', views.identity_search, name ='identity_search'),
    path('book_search/', views.book_search, name ='book_search'),
    path('return_book/<int:id>', views.return_book, name ='return_book'),
    path('renew_book/<int:id>', views.renew_book, name ='renew_book'),
    # ---------Reader Information----------
    path("reader_info/", views.reader_info, name="reader_info"),
    path("reader_info/<str:order>", views.reader_info, name="reader_info"),
    path("request_reader/<str:order>", views.request_reader, name ="request_reader"),
    path("delete_request_reader/<int:id>", views.delete_request_reader, name ="delete_request_reader"),

    path("request_book/<str:order>", views.request_book, name ="request_book"),
    path("save_request_book/", views.save_request_book, name ="save_request_book"),
    path("delete_request_book/<int:id>", views.delete_request_book, name ="delete_request_book"),


# ----------------------------------ADMIN------------------------------------------------
    # --------CATEGORY--------
    path('home/', views.home, name = 'home'),
    path('category/<str:order>', views.category, name = 'category'),
    path('manage_category/', views.manage_category, name = 'manage_category'),
    path('manage_category/<int:id>', views.manage_category, name = 'manage_category_pk'),
    path('save_category/', views.save_category, name = 'save_category'),
    path('delete_category/<int:id>', views.delete_category, name = 'delete_category'),

    # --------Source Type--------
    path('source_type/<str:order>', views.source_type, name = 'source_type'),
    path('manage_source_type/', views.manage_source_type, name = 'manage_source_type'),
    path('manage_source_type/<int:id>', views.manage_source_type, name = 'manage_source_type_pk'),
    path('save_source_type/', views.save_source_type, name = 'save_source_type'),
    path('delete_source_type/<int:id>', views.delete_source_type, name = 'delete_source_type'),
    
    # --------Languages----------
    path('language/<str:order>', views.language, name = 'language'),
    path('manage_language/', views.manage_language, name = 'manage_language'),
    path('manage_language/<int:id>', views.manage_language, name = 'manage_language_pk'),
    path('save_language/', views.save_language, name = 'save_language'),
    path('delete_language/<int:id>', views.delete_language, name = 'delete_language'),

    # --------Book--------
    path('book/<str:order>', views.book, name = 'book'),
    path('manage_book/', views.manage_book, name = 'manage_book'),
    path('manage_book/<int:id>', views.manage_book, name = 'manage_book_pk'),
    path('save_book/', views.save_book, name = 'save_book'),
    path('delete_book/<int:id>', views.delete_book, name = 'delete_book'),

    # --------------User------------------
    path('user/<str:order>', views.user, name = 'user'),
    path('manage_user/', views.manage_user, name = 'manage_user'),
    # path('manage_user/<int:id>', views.manage_user, name = 'manage_user_pk'),
    path('save_user/', views.save_user, name = 'save_user'),
    path('delete_user/<int:id>', views.delete_user, name = 'delete_user'),
    path('view_user/<int:id>', views.view_user, name= 'view_user'),
    path('edit_profile/<int:id>', views.edit_profile, name='edit_profile'),
    path('manage_reader_request/', views.manage_reader_request, name="manage_reader_request"),
    path('decline_reader_request/<int:id>', views.decline_reader_request, name="decline_reader_request"),
    path('accept_reader_request/', views.accept_request_reader, name="accept_reader_request"),
]