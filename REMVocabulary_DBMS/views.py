from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from REMVocabulary_DBMS.model import *


def passes(request):
    """
    Just for testing, it doesn't make sense.
    """
    t = request.session['username']
    context = {'hello': t}
    return render(request, 'pass.html', context)


def test(request):
    """
    Show base.html
    """
    username = request.session['username']
    context = {'username': username}
    return render(request, 'base.html', context)


def login(request):
    """
    Process login verification
    """
    if request.method == 'GET':
        # 1, 首先检查session，判断用户是否第一次登录，如果不是，则直接重定向到首页
        if 'username' in request.session:
            # context = {'hello': request.session['username']}
            # return render(request, 'pass.html', context)
            return HttpResponseRedirect('/base/')  # TODO: return render(首页)
        # 2, 然后检查cookie，是否保存了用户登录信息
        if 'username' in request.COOKIES:
            # 若存在则赋值回session，并重定向到首页
            request.session['username'] = request.COOKIES['username']
            # context = {'hello': request.session['username']}
            # return render(request, 'pass.html', context)
            return HttpResponseRedirect('/base/')  # TODO: return render(首页)
        # 不存在则重定向登录页，让用户登录
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # 查询
        result = verify(username, password)
        if result == 0:
            request.session['username'] = username
            # 检查post 提交的所有键中是否存在 isSaved 键
            response = HttpResponseRedirect('/base/')  # TODO: return render(首页)
            if 'isSaved' in request.POST.keys():
                # 若存在则说明用户选择了记住用户名功能，执行以下语句设置cookie的过期时间
                response.set_cookie('username', username, 60 * 60 * 24 * 7)
            return response
        elif result == 1:
            context = {'error': '用户名或者密码为空！'}
            return render(request, 'login.html', context)
        else:
            context = {'error': '输入的用户名或者密码错误！'}
            return render(request, 'login.html', context)


def logout(request):
    """
    Process logout operation
    """
    # 删除session
    if 'username' in request.session:
        del request.session['username']
    resp = HttpResponseRedirect('/login/')
    # 删除cookie
    if 'username' in request.COOKIES:
        resp.delete_cookie('username')
    return resp

