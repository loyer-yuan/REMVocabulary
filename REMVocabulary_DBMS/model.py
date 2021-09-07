import hashlib
import os
from tool.MySQLConn import MyPymysql
import datetime, math

debug = True
# default data
success = 0  # proceed successfully
plan_number = 50  # the default data of remember_word table
study_number = 0  # the default data of remember_word table
preview_number = 0  # the default data of remember_word table
forget_number = 0  # the default data of oblivion table
remember_number = 0  # the default data of oblivion table
oblivion_rate = 0  # the default data of oblivion_rate table
daily_word_number = 0  # the default data of daily_word_number table


def getAlias(username):
    mysql = MyPymysql()
    result = mysql.getOne('select alias from user where username = %s', [username])
    return result[0]


def verify(username, password):
    """
    验证登录的账户
    :param username: 账户名，为邮箱
    :param password: 密码，未加密
    :return:
        0 —— 正确；
        1 —— 用户名或者密码为空
        2 —— 输入的用户名或者密码错误
    """
    m = hashlib.md5()
    m.update(password.encode())
    password_m = m.hexdigest()
    # 用户名或者密码为空
    if not username or not password:
        print('The login failed')
        return 1
    mysql = MyPymysql()
    sql = "select password from user where username = %s;"
    temp = mysql.getOne(sql, [username])
    if debug:
        print('username: ' + username + "\npassword: "
              + password + "\npassword_m: " + password_m)
        print("password_db: " + str(temp))
    mysql.dispose()
    # 不存在用户名或者密码不正确
    if not temp or temp[0] != password_m:
        print('The login failed')
        return 2
    print('Signed in successfully')
    return success


def registerUser(username, password, repeat_password):
    """
    Verify the validity of the parameters, and register in the db
    :param username: username
    :param password: password
    :param repeat_password: the copy of the password
    :return:
        0. Successful registration
        1. The mailbox has been registered
        2. The password entered twice is inconsistent
        3. The input cannot be empty
    """
    # 判断输入是否为空
    if not username or not password or not repeat_password:
        print('The input cannot be empty')
        return 3
    # 两次输入的密码不一致
    if password != repeat_password:
        print('The password entered twice is inconsistent')
        return 2
    mysql = MyPymysql()
    # 查询数据库中是否存在了相同的邮箱/用户名
    result = mysql.getOne('select 1 from user where username = %s', username)
    # 存在相同的用户名
    if result:
        print("The mailbox has been registered")
        return 1
    # 所有条件都符合，开始注册
    if debug:
        print("start register")
    m = hashlib.md5()
    m.update(password.encode())
    password_m = m.hexdigest()
    mysql.begin()
    a = mysql.insert('insert into user(username, alias, password) values (%s, %s, %s)',
                     [username, username, password_m])
    a += mysql.insert('insert into remember_word(username, plan_number, study_number, '
                      'preview_number) values (%s, %s, %s, %s)', [username, plan_number, study_number,
                                                                  preview_number])
    a += mysql.insert('insert into oblivion(username, forget_number, remember_number) '
                      'values (%s, %s, %s);', [username, forget_number, remember_number])
    mysql.end("commit")
    if debug:
        print("if the number of the affected rows is 2, commit successfully! now, is " + str(a))
    print("register successfully!")
    mysql.dispose()
    return success


def loginDo(user):
    if debug:
        print("进入loginDo")
    username = user['username']
    mysql = MyPymysql()
    # 开始事务
    mysql.begin()
    """
    签到
    """
    # 获取最近连续签到的记录
    target = mysql.getOne('select id, username, consecutive_check, update_time from check_in_form where username = %s '
                          'and update_time = '
                          '(select max(update_time) from check_in_form where username = %s);', [username, username])
    # 如果不存在记录，也就是第一次登录
    if not target:
        # 创建新的纪录， id从0开始
        state = mysql.insert('insert into check_in_form(id, username, consecutive_check) '
                             'values (%s, %s, %s);', [0, username, 1])
        if debug:
            print('第一次登录，插入签到表影响的行数为：' + str(state))
        """
        第一次登录，初始化第一次遗忘率为0
        """
        state = mysql.insert("insert into oblivion_rate(username, rate) "
                             "values (%s, %s);", [username, oblivion_rate])
        if debug:
            print("插入oblivion-rate数据为：username: " + str(username)
                  + "\t遗忘率：" + str(oblivion_rate)
                  + "\t影响行数为：" + str(state))
        """
        第一次登录，初始化第一天的单词记忆总量
        """
        state = mysql.insert("insert into daily_word_number(username, daily_word_number) "
                             "values (%s, %s);", [username, daily_word_number])
        if debug:
            print("插入daily_word_number数据为： username: " + str(username)
                  + "\tdaily_word_number: " + str(daily_word_number)
                  + "\t影响行数：" + str(state))
    else:
        # 已经有了记录, 判断是否是昨天的记录
        today = datetime.datetime.today()
        diff = (today.date() - target[3].date()).days
        if debug:
            print("Today is " + str(today) + " diff is " + str(diff))
        # 判断并写入temp_book单词（每天第一次登录时, 更换单词本时）（取一天数据）
        if diff > 0:  # 不是今天登录
            check_temp_book(user, True)
        if diff == 1:
            # 是昨天的记录， 在昨天的记录上consecutive_check+1
            if debug:
                print("签到表最近一次连续签到信息为：id: " + str(target[0]) + "\tusername: " + str(target[1])
                      + "\t连续签到次数：" + str(target[2])
                      + "\t最近更新时间：" + str(target[3])
                      + "\t距离上次登录: " + str(diff))
            mysql.update('update check_in_form '
                         'set consecutive_check = consecutive_check + 1 '
                         'where id = %s and username = %s;', [target[0], target[1]])
        elif diff > 1:
            # 不是昨天的记录，昨天没签到
            state = mysql.insert('insert into check_in_form(id, username, consecutive_check) '
                                 'values (%s, %s, %s);', [target[0] + 1, target[1], 1])
            if debug:
                print("昨天没签到，新建连续签到记录，影响行数：", str(state))
        """
        计算登录前并且为今天之前的遗忘率
        """
        if diff > 0:
            data_oblivion = mysql.getOne("""select username, forget_number, remember_number 
                                        from oblivion where username = %s;""", [username])
            # 判断是否非0
            if data_oblivion[2] == 0:
                insert_data = 0
            else:
                insert_data = data_oblivion[1] / data_oblivion[2]
            state = mysql.insert("insert into oblivion_rate(username, rate) "
                                 "values (%s, %s);", [data_oblivion[0], insert_data])
            if debug:
                print("插入oblivion-rate数据为：username: " + data_oblivion[0]
                      + "\t遗忘率：" + str(insert_data)
                      + "\t影响行数为：" + str(state))
        """
        计算登录前并且为今天之前的单词记忆总量
        """
        if diff > 0:
            data = mysql.getOne("select study_number from remember_word "
                                "where username = %s;", [username])
            state = mysql.insert("insert into daily_word_number(username, daily_word_number) "
                                 "values (%s, %s);", [username, data[0]])
            if debug:
                print("插入daily_word_number数据为： username: " + str(username)
                      + "\tdaily_word_number: " + str(data[0])
                      + "\t影响行数：" + str(state))
    mysql.end("commit")
    mysql.dispose()


def getDataOfIndex(user):
    """
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
    username = user['username']
    mysql = MyPymysql()
    data = {}

    # 取出最近的前20个每天的学习单词总量数据
    study_numbers = mysql.getMany('select daily_word_number, update_time '
                                  'from daily_word_number where username = %s '
                                  'order by update_time desc;', 20, [username])
    # 将从日期大到小，变成从小到大
    study_numbers = study_numbers[::-1]
    study_number_key = []
    study_number_data = []
    # 取出数据
    for i in study_numbers:
        # 取时间
        study_number_key.append(str(i[1].date()))
        # 取数据
        study_number_data.append(str(i[0]))
    if debug:
        print("数据展示中，记忆单词数量条形图数据为：")
        for i in range(len(study_numbers)):
            print("日期为：" + study_number_key[i] + "\t单词数量为；" + study_number_data[i])
    # 将单词总量的数据存入data字典中
    data['study_number_key'] = study_number_key
    data['study_number_data'] = study_number_data

    # 取出进度的数据
    # 先取出当前在背的单词本，有可能为空
    book_name = mysql.getOne("select word_book from remember_word where username = %s;", [username])
    if not book_name:
        # 为空
        data['progress'] = str(0)
        if debug:
            print("数据展示中，单词本进度数据为：")
            print(str(0))
    else:
        # 用book_name在word_book表中取出该单词本的数据
        total_num = mysql.getOne("select count(words) from word_book "
                                 "where word_book = %s and username = %s;", [book_name, username])
        study_word_num = mysql.getOne("select count(words) from word_book "
                                      "where word_book = %s and username = %s and degree = 'finished';"
                                      , [book_name, username])
        # 计算进度，并且换算成百分制
        progress = '0'
        if total_num[0] == 0:
            data['progress'] = progress
        else:
            progress = str(math.ceil(study_word_num[0] / total_num[0] * 100))
            data['progress'] = progress
        if debug:
            print("数据展示中，单词本进度数据为：")
            print("progress: " + str(progress) + "%")

    # 取出20个每日的遗忘率数据
    temp = mysql.getMany("select date, rate from oblivion_rate "
                         "where username = %s order by date desc;", 20, [username])
    # 将从日期大到小，变成从小到大
    temp = temp[::-1]
    or_key = []
    or_data = []
    # 取出数据
    for i in temp:
        # 取时间
        or_key.append(str(i[0].date()))
        # 取数据
        or_data.append(str(i[1]))
    if debug:
        print("数据展示中，遗忘曲线数据为：")
        for i in range(len(temp)):
            print("日期为：" + or_key[i] + "\t遗忘率为；" + or_data[i])
    # 将单词总量的数据存入data字典中
    data['or_key'] = or_key
    data['or_data'] = or_data

    # 取出当前连续签到数
    consecutive_check = mysql.getOne('select consecutive_check from check_in_form where username = %s '
                                     'and update_time = '
                                     '(select max(update_time) from check_in_form where username = %s);',
                                     [username, username])
    consecutive_check = consecutive_check[0]
    data['consecutive_check'] = str(consecutive_check)

    # 取出总签到数
    add_check = mysql.getOne('select count(consecutive_check) from check_in_form where username = %s;', [username])
    if debug:
        print("取出总签到数: " + str(add_check[0]))
    data['add_check'] = str(add_check[0])

    # 取出最大签到数
    max_check = mysql.getOne('select max(consecutive_check) from check_in_form where username = %s;', [username])
    if debug:
        print("取出最大签到数: " + str(max_check[0]))
    data['max_check'] = str(max_check[0])

    # 取出平均学习单词的数量
    total_study_num = mysql.getOne('select study_number from remember_word where username = %s;', [username])
    # register_time = mysql.getOne('select register_time from user where username = %s;', [username])
    # timedelta = (datetime.datetime.now().date() - register_time[0].date()).days
    # avg_study = '0'
    # if timedelta == 0:
    #     data['avg_study'] = avg_study
    # else:
    #     avg_study = format(total_study_num[0] / timedelta, '.2f')
    avg_study = format(total_study_num[0] / int(add_check[0]), '.2f')
    if debug:
        print("取出平均学习单词的数量: " + avg_study)
    data['avg_study'] = avg_study

    # 取出平均复习单词的数量
    total_preview_num = mysql.getOne('select preview_number from remember_word where username = %s;', [username])
    avg_preview = '0'
    # if timedelta == 0:
    #     data['avg_preview'] = avg_preview
    # else:
    #     avg_preview = format(total_preview_num[0] / timedelta, '.2f')
    avg_preview = format(total_preview_num[0] / int(add_check[0]), '.2f')
    if debug:
        print("取出平均复习单词的数量: " + avg_preview)
    data['avg_preview'] = avg_preview

    mysql.end("commit")
    mysql.dispose()
    return data


def getSetPageData(user):
    """
    return study_number
    """
    mysql = MyPymysql()
    username = user['username']
    plan_numbers = mysql.getOne("select plan_number from remember_word where username = %s;", [username])
    if debug:
        print("获得setting页面的数据plan_number： " + str(plan_numbers[0]))
    mysql.dispose()
    return str(plan_numbers[0])


def setPlanNum(user, change_data):
    """
    update plan_number of the user
    """
    username = user['username']
    mysql = MyPymysql()
    if debug:
        print("修改remember_word表的username为：" + str(username)
              + "中的plan_number为：" + str(change_data))
    mysql.update("update remember_word "
                 "set plan_number = %s "
                 "where username = %s;", [change_data, username])
    mysql.end("commit")
    mysql.dispose()


def setAlias(user, change_data):
    """
    update alias of the user
    """
    username = user['username']
    mysql = MyPymysql()
    if debug:
        print("修改remember_word表的username为：" + str(username)
              + "中的alias为：" + str(change_data))
    mysql.update("update user "
                 "set alias = %s "
                 "where username = %s;", [change_data, username])
    mysql.end("commit")
    mysql.dispose()


def setPassword(user, password):
    """
    update password
    """
    username = user['username']
    m = hashlib.md5()
    m.update(password.encode())
    password_m = m.hexdigest()
    mysql = MyPymysql()
    if debug:
        print("现在更新用户为：" + username
              + "的密码\t新密码为：" + password
              + "\t加密后，存入数据库新密码为" + password_m)
    mysql.update("update user "
                 "set password = %s "
                 "where username = %s;", [password_m, username])
    mysql.end("commit")
    mysql.dispose()


def word_book_to_sql(file_name):
    """
    将单词本从txt文件导入到数据库中
    :param file_name: username_bookname.txt
    :returns
    False - 插入的单词本有不在单词库的单词
    True - 成功插入
    """
    # 获取文件位置
    target = os.path.join(os.getcwd() + r"\word_book", file_name)
    # 去掉后缀名
    book = file_name.split(".")[0]
    # 获取用户名
    username = book.split("_")[0]
    if debug:
        print("book: " + book + " username: " + username)
    # 去掉用户名
    book = book.split("_")[1]
    mysql = MyPymysql()

    # sql准备
    sql = "insert into word_book (words, word_book, username) " \
          "values (%s, %s, %s);"

    # 开始事务
    error_word = []
    try:
        mysql.begin()
        # 获取文件每一行的单词
        with open(target, 'r') as f:
            # 不能使用readlines(), 会读取到\n
            data_set = f.read().splitlines()
            for data in data_set:
                # 全部小写
                data = str.lower(data)
                # 查找有无单词
                result = mysql.getOne("select words from vocabulary where words = %s;", [data])
                if not result:
                    error_word.append(data)
                    print("没有该单词： " + data)
                else:
                    mysql.insert(sql, [data, book, username])
        # 结束事务
        mysql.end("commit")
    except:
        mysql.end("rollback")
        mysql.dispose()
        return False, error_word
    if debug:
        print("单词本 " + book + " 插入数据库完成！")
    mysql.dispose()
    if error_word:
        return False, error_word
    else:
        return True, error_word


def is_exist_book(username, book_name):
    """
    查找是否该用户已经存在该单词本
    """
    # 去掉后缀名
    book = book_name.split(".")[0]
    mysql = MyPymysql()
    state = mysql.getOne("select 1 from word_book "
                         "where username = %s and word_book = %s;",
                         [username, book])
    mysql.dispose()
    if state:
        # 存在该单词本
        return True
    else:
        return False


def choice_book(username, book_name):
    """
    修改在背的单词书
    """
    mysql = MyPymysql()

    mysql.begin()
    mysql.update("update remember_word "
                 "set word_book = %s "
                 "where username = %s;", [book_name, username])
    mysql.end("commit")
    mysql.dispose()
    if debug:
        print("修改用户 " + username + " 背诵的单词书为 " + book_name)


def get_book_list(user):
    """
    获取用户的所有单词本列表，可能为空
    """
    mysql = MyPymysql()
    username = user['username']

    book_list = mysql.getAll("select distinct word_book "
                             "from word_book "
                             "where username = %s;", [username])
    if debug:
        print("获取到用户 " + username + " 的单词本列表\n" + str(book_list))
    mysql.dispose()
    return book_list


def get_current_book(user):
    """
    获取当前用户的当前学习的单词书，有可能返回空集合
    """
    username = user['username']
    mysql = MyPymysql()

    book = mysql.getOne("select word_book "
                        "from remember_word "
                        "where username = %s;", [username])
    mysql.dispose()
    return book


def check_temp_book(user, flag):
    """
    判断temp_book内单词的数量，补充单词，每天第一次登陆时才执行
    :return True - 正常执行流程
            False - 用户没有指定单词本学习，不正常退出
    """
    username = user['username']
    mysql = MyPymysql()

    # 获取最近一次的登录时间
    login_time = mysql.getOne(
        'select update_time from check_in_form where username = %s '
        'and update_time = '
        '(select max(update_time) from check_in_form where username = %s);', [username, username])
    today = datetime.datetime.today()
    # 计算距离最近一次的登陆时间为多少
    diff = (today.date() - login_time[0].date()).days
    # 如果是今天登录
    if diff == 0 and flag:
        return True

    # 如果今天没有登录，开始事务
    mysql.begin()
    # 获取用户的当前学习的单词本
    word_book = mysql.getOne("select word_book from remember_word where username = %s;", [username])
    word_book = word_book[0]
    if debug:
        print()
        if word_book is None:
            print("当前没有学习的单词本")
        else:
            print("当前学习的单词本为： " + word_book)
    # 用户还没有指定单词本学习
    if word_book is None:
        return False

    # 取出复习的单词
    preview_word_list = []
    degree = {'f1': 1, 'f2': 2, 'f4': 4, 'f7': 7, 'f15': 15}
    for i in degree.keys():
        # 取出f系列等级的单词
        temp = mysql.getAll("select words, time from word_book "
                            "where username = %s and word_book = %s and degree = %s;",
                            [username, word_book, i])
        if temp:
            for j in temp:
                diff_day = (today.date() - j[1].date()).days
                # 取出当天及更早之前要复习的单词
                if diff_day >= degree[i]:
                    preview_word_list.append(j[0])

    count = 0
    # 将需要复习单词写入temp_book
    if debug:
        print()
        print("写入temp_book复习单词为：")
    for i in preview_word_list:
        state = mysql.getOne("select 1 from temp_book "
                             "where word = %s and word_book = %s and username = %s;", [i, word_book, username])
        # 如果已经存在，那就不插入
        if not state:
            mysql.insert("insert into temp_book(word, word_book, username, degree) "
                         "values (%s, %s, %s, 'preview');", [i, word_book, username])
            count += 1
            if debug:
                print("单词 " + i + ", 单词本 " + word_book + ", 用户名 " + username)
    # 更新复习的单词数量
    mysql.update("update remember_word set preview_number = preview_number+%s "
                 "where username = %s;", [count, username])
    mysql.end("commit")
    if debug:
        print()
        print("更新复习的单词的数量： " + str(count))

    # 事务再次开始
    mysql.begin()
    # 取需要学习的单词
    study_word_list = []
    # 查看temp_book内已经有的单词数量，是否达到一天所要学习的数量
    exist_number = mysql.getOne("select count(word) from temp_book "
                                "where username = %s and word_book = %s;",
                                [username, word_book])
    exist_number = exist_number[0]
    # 取规划好的学习量
    plan_word_num = mysql.getOne("select plan_number from remember_word where username = %s;", [username])
    plan_word_num = plan_word_num[0]
    # 需要增加的学习量
    diff_word_num = 0
    # 判断用户temp_book的单词数量是否到达学习目标
    if exist_number < plan_word_num:
        diff_word_num = plan_word_num - exist_number
    if debug:
        print()
        print("需要增加的学习量为： " + str(diff_word_num))
    # 不是0
    if diff_word_num != 0:
        temp = mysql.getMany("select words from word_book "
                             "where username = %s and word_book = %s and degree = 'not learning';",
                             diff_word_num, [username, word_book])
        if temp:
            for i in temp:
                study_word_list.append(i[0])
    if debug:
        print()
        print("写入temp_book的学习的单词为：")
    # 将需要学习的单词写入temp_book
    for i in study_word_list:
        state = mysql.getOne("select 1 from temp_book "
                             "where word = %s and word_book = %s and username = %s;", [i, word_book, username])
        # 如果已经存在，那就不插入
        if not state:
            mysql.insert("insert into temp_book(word, word_book, username, degree) "
                         "values (%s, %s, %s, 'study');", [i, word_book, username])
            if debug:
                print("单词 " + i + ", 单词本 " + word_book + ", 用户名 " + username)
    mysql.end("commit")

    count_all = mysql.getOne("select count(distinct word) from temp_book "
                             "where username = %s and word_book = %s;", [username, word_book])
    if count_all:
        count_all = count_all[0]
        mysql.update("update remember_word "
                     "set temp_num = %s "
                     "where username = %s;", [count_all, username])
    mysql.dispose()
    return True


def get_word_list(user):
    """
    从temp_book获取需要背诵的单词组
    """
    username = user['username']
    mysql = MyPymysql()
    # 获取用户的当前学习的单词本
    word_book = mysql.getOne("select word_book from remember_word where username = %s;", [username])
    word_book = word_book[0]

    # 结算一轮走完的所有情况
    mysql.begin()
    mysql.update("update temp_book "
                 "set list = list-1 "
                 "where username = %s and word_book = %s and list = '1';", [username, word_book])
    mysql.update("update temp_book "
                 "set list = list-1 "
                 "where username = %s and word_book = %s and list = '2';", [username, word_book])
    mysql.end("commit")

    # 事务开始
    mysql.begin()
    word_list = []
    # 查找有没有需要复习的单词
    temp = mysql.getAll("select word from temp_book "
                        "where username = %s and word_book = %s and degree = 'preview';", [username, word_book])
    # 如果有需要复习的单词
    if temp:
        for i in temp:
            # 放入session列表中
            word_list.append([str(i[0]), 'preview2'])
            # 设置temp_book中degree为preview2，设置list为2
            mysql.update("update temp_book "
                         "set degree = 'preview2', list = '2' "
                         "where username = %s and word_book = %s and word = %s;", [username, word_book, str(i[0])])
    else:
        # 取出<=7个study类型的单词
        temp = mysql.getMany("select word from temp_book "
                             "where username = %s and word_book = %s and degree = 'study';", 7, [username, word_book])
        # 存在study的单词
        if temp:
            # 将study的单词放入session的word_list中
            for i in temp:  # TODO: 检查取单词有无问题
                word_list.append([str(i[0]), 'study'])
            temp = mysql.getAll("select word, degree from temp_book "
                                "where username = %s and word_book = %s and list = '0';", [username, word_book])
            # 将所有要复习的单词放入session的word_list中
            if temp:
                for i in temp:
                    word_list.append([str(i[0]), str(i[1])])
        # 不存在study的单词
        else:
            temp = mysql.getAll("select word, degree from temp_book "
                                "where username = %s and word_book = %s and list is not null;", [username, word_book])
            if temp:
                for i in temp:
                    word_list.append([str(i[0]), str(i[1])])
    mysql.end("commit")
    mysql.dispose()
    if debug:
        print("session中的单词为：")
        for i in word_list:
            print("{0}: {1}".format(i[0], i[1]))
    if not word_list:
        if debug:
            print("已经背完单词")
        return False
    return word_list


def increase_study_number(user):
    """
     更新当前用户的remember_word的study_number+1
    """
    username = user['username']
    mysql = MyPymysql()
    state = mysql.update("update remember_word "
                         "set study_number = study_number+1 "
                         "where username = %s;", [username])
    if debug:
        print("更新用户 " + username + " 的study_number +1，数据库影响行数为" + str(state))
    mysql.dispose()


def increase_remember_number(user):
    """
    更新oblivion的remember_number+1
    """
    username = user['username']
    mysql = MyPymysql()
    state = mysql.update("update oblivion "
                         "set remember_number = remember_number+1 "
                         "where username = %s;", [username])
    if debug:
        print("更新用户 " + username + " 的remember_number +1，数据库影响行数为" + str(state))
    mysql.dispose()


def get_word_data(word, degree):
    """
    获取单词的相应程度的数据，不同程度的，有不同种类和数量的数据
    :param word: 需要查找的单词
    :param degree: 对应的程度 分别有[study, detail, preview, after_preview]
    :return: dict, 包含相应的数据集
        'type' == 'study':
            'word':
            'examples': (list)
        'type' == 'detail'/'after_preview':
            'word':
            'pronounce':
            'chineses': (list）
                {'part_of_speech', 'chinese'}
            'examples': (list)
                {'example', 'chinese'}
        'type' == 'preview':
            'chineses': (list）
                {'part_of_speech', 'chinese'}
            'examples': (list)
                {'example', 'chinese'} 去掉需要填写的单词
    """
    mysql = MyPymysql()

    # 取音标
    pronounce = ""
    temp = mysql.getAll("select pronounce from pronounce where words = %s;", [word])
    if temp:
        for i in temp:
            pronounce += i[0] + "   "

    # 取中文释义
    chineses = []
    temp = mysql.getAll("select part_of_speech, chinese "
                        "from vocabulary "
                        "where words = %s;", [word])
    if temp:
        for i in temp:
            chineses.append({'part_of_speech': i[0], 'chinese': i[1]})

    # 取例句，最多10个
    examples = []
    temp = mysql.getMany("select example, chinese "
                         "from example "
                         "where words = %s;", 10, [word])
    if temp:
        for i in temp:
            examples.append({'example': i[0], 'chinese': i[1]})

    # 根据degree，打包信息
    data = {}
    if degree == "study":
        es = []
        for i in examples:
            es.append(i['example'])
        data = {'word': word,
                'examples': es}
    if degree == "detail" or degree == "after_preview":
        data = {'word': word,
                'pronounce': pronounce,
                'chineses': chineses,
                'examples': examples}
    if degree == "preview":
        ex1 = []
        for i in examples:
            example = i['example']
            example = example.replace(word, "_____")
            example = example.replace(word[0].upper() + word[1:], "_____")
            example = example.replace(word.upper(), "_____")
            ex1.append({'example': example, 'chinese': i['chinese']})
        data = {'chineses': chineses,
                'examples': ex1}
    mysql.dispose()
    if debug:
        print()
        print("发送给study页面的data数据包为：")
        for i, j in data.items():
            print(str(i) + ": " + str(j))
    return data


def get_study_progress(user):
    """
    获取当前用户，当天学习的学习进度
    """
    username = user['username']
    mysql = MyPymysql()
    # 获取用户的当前学习的单词本
    word_book = mysql.getOne("select word_book from remember_word where username = %s;", [username])
    word_book = word_book[0]

    plan_num = mysql.getOne("select temp_num from remember_word "
                            "where username = %s;", [username])
    if type(plan_num) != "NoneType":
        plan_num = int(plan_num[0])
        study_num = mysql.getOne("select count(word) from temp_book "
                                 "where username = %s and word_book = %s;", [username, word_book])
        study_num = int(study_num[0])
        progress = (1 - study_num / plan_num) * 100
    else:
        progress = 0

    mysql.dispose()
    return str(math.ceil(progress))


def delete_word_in_temp_book(user, word):
    """
    删除temp_book中的某个单词
    """
    username = user['username']
    mysql = MyPymysql()
    # 获取用户的当前学习的单词本
    word_book = mysql.getOne("select word_book from remember_word where username = %s;", [username])
    word_book = word_book[0]

    mysql.delete("delete from temp_book "
                 "where username = %s and word_book = %s and word = %s;",
                 [username, word_book, word])
    if debug:
        print()
        print("删除用户: " + username + "temp_book的单词 " + word)
    mysql.dispose()


def update_word_in_table(user, table, word, operate):
    """
    更新单词在相应的表中的等级
    :param user: 用户
    :param table: 相应的表格，比如：temp_book, word_book
    :param word: 需要更新的单词
    :param operate: 需要更新的操作，'up', 'down', 'f1', 'finished', 'preview1', 'preview2'
    :return: None
    """
    degrees = ()
    if table == 'word_book':
        degrees = ('not learning', 'f1', 'f2', 'f4', 'f7', 'f15', 'finished')
    if table == 'temp_book':
        degrees = ('study', 'preview1', 'preview2')
    username = user['username']
    mysql = MyPymysql()
    # 获取用户的当前学习的单词本
    word_book = mysql.getOne("select word_book from remember_word where username = %s;", [username])
    word_book = word_book[0]

    if table == 'word_book':
        # 获取当前单词的degree
        degree = mysql.getOne("select degree from word_book "
                              "where username = %s and word_book = %s and words = %s;",
                              [username, word_book, word])
        degree = degree[0]
        if operate == 'up':
            index = degrees.index(degree)
            mysql.update("update word_book "
                         "set degree = %s "
                         "where username = %s and word_book = %s and words = %s;",
                         [degrees[index+1], username, word_book, word])
        if operate == 'down':
            index = degrees.index(degree)
            if index == 0:
                return
            mysql.begin()
            if index == 1:
                mysql.update("update word_book "
                             "set degree = 'f1' "
                             "where username = %s and word_book = %s and words = %s;",
                             [username, word_book, word])
            elif index > 1:
                mysql.update("update word_book "
                             "set degree = %s "
                             "where username = %s and word_book = %s and words = %s;",
                             [degrees[index - 1], username, word_book, word])
            mysql.update("update oblivion "
                         "set forget_number = forget_number+1 "
                         "where username = %s;", [username])
            mysql.end("commit")
        if operate == 'f1':
            index = degrees.index(degree)
            if index == 0:
                return
            mysql.begin()
            mysql.update("update word_book "
                         "set degree = 'f1' "
                         "where username = %s and word_book = %s and words = %s;",
                         [username, word_book, word])
            mysql.update("update oblivion "
                         "set forget_number = forget_number+1 "
                         "where username = %s;", [username])
            mysql.end("commit")
        if operate == 'finished':
            mysql.update("update word_book "
                         "set degree = 'finished' "
                         "where username = %s and word_book = %s and words = %s;",
                         [username, word_book, word])
    if table == 'temp_book':
        if operate == 'preview1':
            mysql.update("update temp_book "
                         "set degree = 'preview1', list = '1' "
                         "where username = %s and word_book = %s and word = %s;",
                         [username, word_book, word])
        if operate == 'preview2':
            mysql.update("update temp_book "
                         "set degree = 'preview2', list = '2' "
                         "where username = %s and word_book = %s and word = %s;",
                         [username, word_book, word])
    mysql.dispose()


def delete_book(user, book_name):
    """
    删除对应的单词本
    """
    username = user['username']
    mysql = MyPymysql()

    mysql.begin()
    try:
        temp = get_current_book(user)
        if temp:
            if book_name == temp[0]:  # 如果正在学习该单词
                mysql.update("update remember_word "
                             "set word_book = null "
                             "where username = %s;", [username])
        mysql.delete("delete from temp_book "
                     "where username = %s and word_book = %s;", [username, book_name])
        mysql.delete("delete from word_book "
                     "where username = %s and word_book = %s;", [username, book_name])
    except:
        mysql.end("rollback")
        return False
    mysql.end("commit")
    mysql.dispose()
    return True


def is_exist_word(word):
    mysql = MyPymysql()
    temp = mysql.getOne("select 1 from vocabulary where words = %s;", [word])
    if temp:
        return True
    else:
        return False
