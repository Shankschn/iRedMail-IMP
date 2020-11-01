import requests
from bs4 import BeautifulSoup
import bs4
import re
import datetime

# from .HTMLTools import *
from .models import *


def encoding_readable(request_response):
    try:
        request_response.raise_for_status()
        request_response.encoding = request_response.apparent_encoding
    except Exception as e:
        msg = "encoding_readable faild, Exception: {}".format(e)
        print(msg)
        return False
    else:
        msg = 'HTML Encoding：{}'.format(request_response.encoding)
        print(msg)
    return request_response


def html_post(ss, url, data):
    print(url)
    rp = ss.post(url, timeout=30, data=data)
    rp = encoding_readable(rp)
    return ss, rp


def html_get(ss, url):
    print(url)
    rp = ss.get(url, timeout=30)
    rp = encoding_readable(rp)
    return ss, rp


def list_create_user(ss, list):
    status = False

    return status


def login(domain=None):
    print(domain)
    ss = requests.Session()
    status = False
    rp = None
    msg = 'login 未获取到 Domain'
    if domain:
        try:
            ss, rp = html_get(ss, domain.url_admin)
            data = {
                'username': domain.admin_zh,
                'password': domain.admin_mm,
                'login': 'Login',
                'lang': 'zh_CN',
            }
            ss, rp = html_post(ss, domain.url_login, data)
            if rp.status_code == 200:
                status = True
            return status, domain, ss, rp
        except Exception as e:
            msg = "login_iredmail faild: {}".format(e)
    print(msg)
    return status, domain, ss, rp


def findulist(ulist, html):
    soup = BeautifulSoup(html, "html.parser")
    # print(soup.prettify)
    for tr in soup.find('tbody').children:
        # print(tr.children.name)
        if isinstance(tr, bs4.element.Tag):
            tds = tr('td')
            no = tds[3].string
            name = tds[1].contents[4].replace(" ", "").replace("\n", "")
            if 'enable' in tds[1]('img')[1].attrs['src']:
                enable = '已启用'
            else:
                enable = '已禁用'
            email = tds[2].find('strong').string + tds[2].find('em').string
            rl = tds[4].find('span').string
            print(no, name, email, rl, enable)
            ulist.append([no, name, email, rl, enable])


def printulist(ulist, num=0):
    print("{:^10}{:^10}\t{:^25}\t{:^5}\t{:^5}".format("员工编号", "姓名", "邮箱地址", "容量", "状态"))
    if num != 0:
        for i in range(num):
            u = ulist[i]
            print("{:^10}\t{:^25}\t{:^5}\t{:^5}".format(u[0], u[1], u[2], u[3], u[4]))
    else:
        for u in ulist:
            print("{:^10}\t{:^25}\t{:^5}\t{:^5}".format(u[0], u[1], u[2], u[3], u[4]))


def get_page_list(html, pagelist):
    soup = BeautifulSoup(html, 'html.parser')
    lastpage = soup('a', attrs={'class': 'last'})
    zz = re.search(r'\d+', str(lastpage[0]))
    page = zz.group()
    domain = IRedAdminDomain.objects.first()
    for i in range(int(page)):
        pagelist.append(domain.url_page + str(i + 1))
    return pagelist


def get_token(html):
    jg = re.search(r'<input type="hidden" name="csrf_token" value="(.*?)"/>', html)
    csrf_token = jg.groups()[0]
    msg = 'iredmail get_token: {}'.format(csrf_token)
    print(msg)
    return csrf_token


def get_mail_quota(html):
    # print(html)
    jg = re.search(r'<input type="text" name="mailQuota" value="(\d+)" size="10" class="text fl-space" />', html)
    mail_quota = jg.groups()[0]
    msg = 'iredmail get_mail_quota: {}'.format(mail_quota)
    print(msg)
    return mail_quota


def get_password(html):
    jg = re.search(r'<p class="clean-padding clean-padding bt-space10">(.*?)</p>', html)
    password = jg.groups()[0]
    msg = 'iredmail get_password: {}'.format(password)
    print(msg)
    return password


def is_create(html):
    jg = re.search(r'用户已建立', html)
    if jg:
        msg = 'is_create: 成功'
        status = True
    else:
        msg = 'is_create: 失败'
        status = False
    print(msg)
    return status


def is_update(html):
    jg = re.search(r'属性已更新。', html)
    if jg:
        msg = 'is_update: 成功'
        status = True
    else:
        msg = 'is_update: 失败'
        status = False
    print(msg)
    return status


def restart_password(domain, ss, user):
    url = domain.url_modify_user + user.email
    ss, rp = html_get(ss, url)
    html = rp.text
    password = get_password(html)
    csrf_token = get_token(html)
    data = {
        'csrf_token': csrf_token,
        'newpw': password,
        'confirmpw': password,
    }
    url = domain.url_restart_password + user.email
    ss, rp = html_post(ss, url, data)
    if is_update(rp.text):
        msg = 'restart_password: 成功, email: {}, password: {}'.format(user.email, password)
        print(msg)
        user.restart_password_count = user.restart_password_count + 1
        now1 = datetime.datetime.now()
        now2 = now1.strftime('%Y-%m-%d %H:%M:%S')
        if not user.restart_password_time:
            user.restart_password_time = str(now2)
        else:
            user.restart_password_time = str(now2) + ',' + str(user.restart_password_time)
        user.save()
        return password
    else:
        msg = 'restart_password: 失败, email: {}'.format(user.email)
        print(msg)
        return False


def create_user(domain, ss, user):
    status = False
    url = domain.url_create_user
    ss, rp = html_get(ss, url)
    html = rp.text
    csrf_token = get_token(html)
    password = get_password(html)
    data = {
        'csrf_token': csrf_token,
        'username': user.email.split('@')[0],
        'domainName': domain.domain,
        'newpw': password,
        'confirmpw': password,
        'cn': user.name,
        'mailQuota': user.mailbox_quota
    }
    ss, rp = html_post(ss, url, data)
    # print(rp.text)
    if is_create(rp.text):
        user.password = password
        user.save()
        status = True
    return status


def modify_user(doamin, ss, user, data=None):
    status = False
    url = doamin.url_modify_user + user.email
    # print(url)
    ss, rp = html_get(ss, url)
    html = rp.text
    csrf_token = get_token(html)
    old_mail_quota = get_mail_quota(html)
    if not data:
        if user.status == 0:
            data = {
                'csrf_token': csrf_token,
                'cn': user.name,
                'preferredLanguage': user.language,
                'mailQuota': user.mailbox_quota,
                'oldMailQuota': user.mailbox_quota,
                'employeeNumber': user.userid
            }
        else:
            data = {
                'csrf_token': csrf_token,
                'accountStatus': 'active',
                'cn': user.name,
                'preferredLanguage': user.language,
                'mailQuota': user.mailbox_quota,
                'oldMailQuota': old_mail_quota,
                'employeeNumber': user.userid
            }
        print(data)
    else:
        data['csrf_token'] = csrf_token
        data['oldMailQuota'] = old_mail_quota
    ss, rp = html_post(ss, url, data)
    if is_update(rp.text):
        status = True
    return status


def main():

    pagelist = []
    uinfo = []

    # print(ss)
    status, iredadmin, ss, rp = login()
    domain = IRedAdminDomain.objects.first()
    url = domain.url_page
    ss, rp = html_get(ss, url)
    html = rp.rext
    pagelist = get_page_list(html, pagelist)
    for url in pagelist:
       ss, rp = html_get(ss, url)
       html = rp.text
       findulist(uinfo, html)
    printulist(uinfo)
    print(html)
# main()

# if __name__ == "__main__":
#     main()
