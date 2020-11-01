import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import *
from .iredadmin import *

# Create your views here.


def get_email_suffix(email):
    suffix = email.split('.')[-1]
    return suffix


@csrf_exempt
def change_user_status(request):
    d = {}
    if request.method == "POST":
        email = request.POST.get('email')
        if get_email_suffix(email) == 'cn':
            status = request.POST.get('status')
            print(email, status, type(status))
            user = IRedAdminUser.objects.get(email=email)
            msg1 = '员工编号: {0}, 姓名: {1}, 邮箱: {2}, 当前状态：{3}，'.format(user.userid, user.name, user.email,
                                                                   user.get_status_display())
            user.status = int(status)
            user.save()
            status, domain, ss, rp = login(user.domain)
            status2 = modify_user(domain, ss, user)
            if status2:
                d['status'] = 1
                if user.status == 1:
                    msg2 = '变更后状态：已启用。'
                else:
                    msg2 = '变更后状态：已禁用。'
            else:
                d['status'] = 0
                msg2 = '禁用/启用：失败！请联系信息技术部排查。'
            msg = msg1 + msg2
            d['msg'] = msg
        else:
            d['status'] = 0
            msg = 'com后缀邮箱自动禁用功能暂未启用，将于近期启用，请等待。'
            d['msg'] = msg
    else:
        d['tips'] = '请使用POST！'
    temp_d = json.dumps(d)
    return HttpResponse(temp_d, content_type="application/json,charset=utf-8")


@csrf_exempt
def reset_user_password(request):
    d = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        if get_email_suffix(email) == 'cn':
            user = IRedAdminUser.objects.get(email=email)
            msg1 = '员工编号: {0}, 姓名: {1}, 邮箱: {2}, 当前状态：{3}，'.format(user.userid, user.name, user.email,
                                                                   user.get_status_display())
            status, domain, ss, rp = login(user.domain)
            status2 = restart_password(domain, ss, user)
            if not status2:
                msg2 = '重置密码：失败。请联系信息技术部排查。'
                d['status'] = 0
            else:
                d['status'] = 1
                d['password'] = status2
                user.password = status2
                msg2 = '重置密码：成功。'
            msg = msg1 + msg2
            d['msg'] = msg
        else:
            d['status'] = 0
            msg = '以 com 结尾的邮箱自动重置密码功能将于近期启用，目前请等待信息技术部手动重置。'
            d['msg'] = msg
    else:
        d['tips'] = '请使用POST！'
    temp_d = json.dumps(d)
    return HttpResponse(temp_d, content_type="application/json,charset=utf-8")


