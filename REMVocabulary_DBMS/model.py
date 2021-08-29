import hashlib

import pymysql

from tool.MySQLConn import MyPymysql
import datetime

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
    if debug:
        print("展示签到最近记录：username: " + target[1]
              + "\tid: " + str(target[0])
              + "\tconsecutive_check: " + str(target[2])
              + "\tupdate_time: " + str(target[3]))
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
        diff = int((today.day - target[3].day))
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
                                 "where 'word-book' = %s and username = %s;", [book_name, username])
        study_word_num = mysql.getOne("select count(words) from word_book "
                                      "where 'word-book' = %s and username = %s and degree <> 'not learning';"
                                      , [book_name, username])
        # 计算进度，并且换算成百分制
        progress = '0'
        if total_num[0] == 0:
            data['progress'] = progress
        else:
            progress = str(int(study_word_num[0] / total_num[0] * 100))
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
    register_time = mysql.getOne('select register_time from user where username = %s;', [username])
    timedelta = int(datetime.datetime.now().day - register_time[0].day)
    avg_study = '0'
    if timedelta == 0:
        data['avg_study'] = avg_study
    else:
        avg_study = format(total_study_num[0] / timedelta, '.2f')
    if debug:
        print("取出平均学习单词的数量: " + avg_study)
    data['avg_study'] = avg_study

    # 取出平均复习单词的数量
    total_preview_num = mysql.getOne('select preview_number from remember_word where username = %s;', [username])
    avg_preview = '0'
    if timedelta == 0:
        data['avg_preview'] = avg_preview
    else:
        avg_preview = format(total_preview_num[0] / timedelta, '.2f')
    if debug:
        print("取出平均复习单词的数量: " + avg_preview)
    data['avg_preview'] = avg_preview

    return data
