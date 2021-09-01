import os.path

from django.http import HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import render, redirect
from django.utils.encoding import escape_uri_path

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
    # 首先检查session，判断用户是否第一次登录，如果不是，则直接重定向到首页
    if 'user' not in request.session:
        return HttpResponseRedirect('/login/')
    user = request.session['user']
    # 取出展示数据需要的所有数据
    data = getDataOfIndex(user)
    context = {'user': user, 'data': data}
    return render(request, 'index.html', context)


def setPage(request):
    # 首先检查session，判断用户是否第一次登录，如果不是，则直接重定向到首页
    if 'user' not in request.session:
        return HttpResponseRedirect('/login/')
    # 取出user数据
    user = request.session['user']
    if request.method == "GET":
        """
        向setPage页面传递的数据为：
        'user' = {'username': ,'alias': }
        'plan_number' =  
        """
        plan_numbers = getSetPageData(user)
        context = {'user': user,
                   'plan_number': plan_numbers}
        return render(request, 'setting.html', context)
    if request.method == "POST":
        # 获取表单的type，从而明确提交过来的是哪个表单
        types = request.POST.get("type")
        types = str(types)

        # 处理修改每日学习数量的表单
        if types == "plan_number":
            change_data = request.POST.get("plan_number")
            # 修改计划学习数量
            setPlanNum(user, int(change_data))

        # 处理修改别名的表单
        if types == "alias":
            change_data = request.POST.get("alias")
            # 修改别名
            setAlias(user, change_data)
            user['alias'] = change_data
            if debug:
                print("修改了用户：" + user['username']
                      + "的别名为： " + user['alias'])
            request.session['user'] = user

        # 处理修改密码的表单
        if types == "changePassword":
            old_password = request.POST.get("oldPassword")
            new_password = request.POST.get("newPassword")
            repeat_new_password = request.POST.get("repeatNewPassword")
            # 两次密码输入不一致
            if new_password != repeat_new_password:
                plan_numbers = getSetPageData(user)
                context = {'user': user,
                           'plan_number': plan_numbers,
                           'error': "两次密码输入不一致"}
                return render(request, 'setting.html', context)
            # 验证旧密码是否正确
            state = verify(user['username'], old_password)
            # 旧密码输入不正确
            if state != 0:
                plan_numbers = getSetPageData(user)
                context = {'user': user,
                           'plan_number': plan_numbers,
                           'error': "旧密码输入错误"}
                return render(request, 'setting.html', context)
            # 密码输入正确，且两次都正确，修改密码
            setPassword(user, new_password)
            # 更新密码需要重新登录
            return HttpResponseRedirect('/logout/')

        # 执行完修改plan_number和alias，重新载入页面
        return HttpResponseRedirect('/setting/')


def upload_word_book(request):
    """
    处理上传单词本
    """
    username = request.POST.get("username")
    # 获取上传的文件，如果没有文件，则默认为None
    word_book = request.FILES.get("word_book", None)
    # 没有上传文件，没有上传txt文件
    book_name = str(word_book.name)

    # 错误需要重新渲染html
    user = request.session['user']
    # 获取数据
    book_list = get_book_list(user)
    the_current_book = get_current_book(user)
    current_book = []
    # 如果有数据
    if the_current_book:
        current_book = the_current_book[0]
    left_book_list = []
    right_book_list = []
    # book_list存在数据
    if book_list:
        flag = True
        for book in book_list:
            # 交替分配数据给两个列表
            if flag:
                left_book_list.append(book[0])
                flag = False
            else:
                right_book_list.append(book[0])
                flag = True
    context = {'user': user,
               'left_book_list': left_book_list,
               'right_book_list': right_book_list,
               'current_book': current_book}
    # 没有上传文件
    if not word_book:
        error = '没有上传文件'
        context['error'] = error
        return render(request, 'word_book.html', context)
    # 上传文件不是txt
    if not book_name.endswith(".txt"):
        error = '上传单词本不是txt格式'
        context['error'] = error
        return render(request, 'word_book.html', context)
    # 命名带有下划线
    if len(book_name.split('_')) > 1:
        error = '命名不能带有下划线'
        context['error'] = error
        return render(request, 'word_book.html', context)
    # 上传了同名文件
    if is_exist_book(username, book_name):
        error = '已经上传了相同名字的单词本'
        context['error'] = error
        return render(request, 'word_book.html', context)

    # 先存储，再处理，再放入mysql
    # 命名：用户名_单词本
    filename = username + "_" + book_name
    # getcwd()获取当前路径，然后找到word_book文件夹
    destination = open(os.path.join(os.getcwd()+r"\word_book", filename), 'wb+')
    # 分块写入文件
    for chunk in word_book.chunks():
        destination.write(chunk)
    destination.close()
    if debug:
        print("文件 " + filename + " 写入word_book文件夹完成！")

    # 将单词本导入到数据库中
    isSuccess = word_book_to_sql(filename)
    if not isSuccess:
        # 插入的单词本有不在单词库的单词
        error = '插入的单词本有不在单词库的单词，请检查'
        context['error'] = error
        return render(request, 'word_book.html', context)
    return HttpResponseRedirect('/word_book/')


def download_word_book(request):
    """
    下载对应的单词本
    """
    def down_chunk_file_manager(file_path, chuck_size=1024):
        with open(file_path, "rb") as file:
            while True:
                chuck_stream = file.read(chuck_size)
                if chuck_stream:
                    yield chuck_stream
                else:
                    break
    if 'user' not in request.session:
        return HttpResponseRedirect('/login/')
    book_name = request.GET.get("word_book")
    username = request.session['user']['username']
    file_name = username + "_" + book_name + ".txt"
    filepath = os.path.join(os.getcwd()+r"\word_book", file_name)

    response = StreamingHttpResponse(down_chunk_file_manager(filepath))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(escape_uri_path(book_name+".txt"))

    return response


def select_book(request):
    """
    选择要背诵的单词本
    """
    username = request.session['user']['username']
    word_book = request.POST.get('word_book')
    choice_book(username, word_book)

    return HttpResponseRedirect('/word_book/')


def word_book_page(request):
    """
    填充选择单词本页面的相应的数据:
    'user': {'username','alias'}
    'left_book_list': []
    'right_book_list': []
    'current_book':
    """
    # 没有登录就访问，直接要登录
    if 'user' not in request.session:
        return HttpResponseRedirect('/login/')
    user = request.session['user']
    # 获取数据
    book_list = get_book_list(user)
    the_current_book = get_current_book(user)
    current_book = []
    # 如果有数据
    if the_current_book:
        current_book = the_current_book[0]
    left_book_list = []
    right_book_list = []
    # book_list存在数据
    if book_list:
        flag = True
        for book in book_list:
            # 交替分配数据给两个列表
            if flag:
                left_book_list.append(book[0])
                flag = False
            else:
                right_book_list.append(book[0])
                flag = True
    context = {'user': user,
               'left_book_list': left_book_list,
               'right_book_list': right_book_list,
               'current_book': current_book}
    return render(request, "word_book.html", context)
