from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from REMVocabulary_DBMS.model import *

"""
    session and cookie：
    'user' = {'username': ,'alias': }
"""
debug = True


def test(request):
    """
    Show base.html
    """
    if 'user' not in request.session:
        return HttpResponseRedirect('/login/')
    user = request.session['user']
    context = {'user': user}
    return render(request, 'base.html', context)


def register(request):
    """
    help user register
    """
    if request.method == 'GET':
        return render(request, 'register.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        repeat_password = request.POST.get('repeat_password')
        # 注册
        result = registerUser(username, password, repeat_password)
        if result > 0:
            if result == 1:
                context = {'error': '该邮箱已经被注册过'}
            if result == 2:
                context = {'error': '两次输入的密码不一致'}
            if result == 3:
                context = {'error': '输入不能为空'}
            return render(request, 'register.html', context)
        else:  # result is 0
            request.session['user'] = {'username': username,
                                       'alias': username}
            return HttpResponseRedirect('/login/')


def login(request):
    """
    Process login verification
    """
    if request.method == 'GET':
        # 1, 首先检查session，判断用户是否第一次登录，如果不是，则直接重定向到首页
        if 'user' in request.session:
            if debug:
                print("存在session，直接登录")
            # 触发的业务：
            user = request.session['user']
            loginDo(user)
            return HttpResponseRedirect('/index/')  # TODO: return HttpResponseRedirect(首页)
        # 2, 然后检查cookie，是否保存了用户登录信息
        if 'user' in request.COOKIES:
            # 若存在则赋值回session，并重定向到首页
            if debug:
                print("存在cookie，直接登录")
            # 触发的业务：
            user = request.session['user']
            loginDo(user)
            request.session['user'] = request.COOKIES['user']
            return HttpResponseRedirect('/index/')  # TODO: return HttpResponseRedirect(首页)
        # 不存在则重定向登录页，让用户登录
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # 查询
        result = verify(username, password)
        # 可以登录
        if result == 0:
            alias = getAlias(username)
            user = {'username': username, 'alias': alias}
            request.session['user'] = user
            # 触发的业务：
            loginDo(user)
            # 检查post 提交的所有键中是否存在 isSaved 键
            response = HttpResponseRedirect('/index/')  # TODO: return HttpResponseRedirect(首页)
            if 'isSaved' in request.POST.keys():
                # 若存在则说明用户选择了记住用户名功能，执行以下语句设置cookie的过期时间
                response.set_cookie('username', username, 60 * 60 * 24 * 7)
            if debug:
                print("密码和用户名正确，直接登录")
            return response
        # 不能登录
        elif result == 1:
            context = {'error': '用户名或者密码为空！'}
            if debug:
                print("不能登录，因为用户名或者密码为空！")
            return render(request, 'login.html', context)
        else:
            context = {'error': '输入的用户名或者密码错误！'}
            if debug:
                print("不能登录，因为输入的用户名或者密码错误！")
            return render(request, 'login.html', context)


def logout(request):
    """
    Process logout operation
    """
    # 删除session
    if 'user' in request.session:
        del request.session['user']
    resp = HttpResponseRedirect('/login/')
    # 删除cookie
    if 'user' in request.COOKIES:
        resp.delete_cookie('user')
    if debug:
        print("已经退出，删除了session和cookie")
    return resp


def indexPage(request):
    """
    向index传递数据为
    'user' = {'username': , 'alias': }
    'data' = {'study_number': {日期；数目} {'study_number_key' 'study_number_data'}
                ' progress': （str 如：20，0-100）
                'oblivion_rate': {日期: 遗忘率} {'or_key' 'or_data'}
                'consecutive_check: '
                'add_check: '
                'max_check: '
                'avg_study: '
                'avg_preview: '
               }
    """
    if 'user' not in request.session:
        return HttpResponseRedirect('/login/')
    user = request.session['user']
    data = getDataOfIndex(user)
    context = {'user': user, 'data': data}
    return render(request, 'index.html', context)
