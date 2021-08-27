import hashlib
from tool.MySQLConn import MyPymysql

debug = False
# default data
success = 0  # proceed successfully
plan_number = 50  # the default data of remember_word table
study_number = 0  # the default data of remember_word table
preview_number = 0  # the default data of remember_word table


def getAlias(username):
    mysql = MyPymysql()
    result = mysql.getOne('select alias from user where username = %s', [username])
    return result


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
    temp = temp[0]
    if debug:
        print('username: ' + username + "\npassword: "
              + password + "\npassword_m: " + password_m)
        print("password_db: " + temp)
    mysql.dispose()
    # 不存在用户名或者密码不正确
    if not temp or temp != password_m:
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
    mysql.end("commit")
    if debug:
        print("if the number of the affected rows is 2, commit successfully! now, is" + str(a))
    print("register successfully!")
    return success
