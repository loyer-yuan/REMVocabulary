"""REMVocabulary_DBMS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path


from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('base/', views.test, name='base'),
    path('register/', views.register, name='register'),
    # index
    path('index/', views.indexPage, name='index'),
    # setting
    path('setting/', views.setPage, name='setting'),
    # word_book
    path('delete_word_book/', views.delete_word_book, name='delete_word_book'),
    path('word_book/', views.word_book_page, name='word_book'),
    path('upload_word_book/', views.upload_word_book, name='upload_word_book'),
    path('download_word_book/', views.download_word_book, name='download_word_book'),
    path('select_book/', views.select_book, name='select_book'),
    # study
    path('study/', views.studyPage, name='study'),
    # search
    path('search/', views.search, name='search')
]