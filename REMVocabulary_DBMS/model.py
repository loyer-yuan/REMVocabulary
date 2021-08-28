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
    else:
        # 已经有了记录, 判断是否是昨天的记录
        today = datetime.datetime.today()
        diff = (today - target[3]).days
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
                print("昨天没签到，新建连续签到记录，影响行数：", state)
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
    mysql.end("commit")
    mysql.dispose()
