import hashlib
from MySQLConn import MyPymysql


debug = False


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
    sql = "select password from user where username = %s"
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
    return 0
