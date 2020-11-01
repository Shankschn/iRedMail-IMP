from django.contrib import admin
from django.contrib import messages

# Register your models here.
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

admin.site.site_title = 'iRedAdmin 间接管理后台'
admin.site.site_header = 'iRedAdmin 间接管理后台'
admin.site.index_title = 'iRedAdmin 间接管理后台'

from .iredadmin import *


admin.site.site_title = 'iRedAdmin 间接管理后台'
admin.site.site_header = 'iRedAdmin 间接管理后台'
admin.site.index_title = 'iRedAdmin 间接管理后台'


def str_in_list(a_str, a_list):
    is_in = False
    for lt in a_list:
        if a_str == lt:
            is_in = True
            break
    return is_in


@admin.register(IRedAdminDomain)
class IRedAdminDomainAdmin(ImportExportModelAdmin):
    list_display = ['id', 'domain']
    list_display_links = ['domain']
    actions = ['flush_users']

    def flush_users(self, request, queryset):
        for q in queryset:
            messages_status = 0
            pagelist = []
            uinfo = []
            msg = '登陆不成功，请排查。'
            status, iredadmin, ss, rp = login(q)
            if status:
                ss, rp = html_get(ss, q.url_user)
                pagelist = get_page_list(rp.text, pagelist)
                for url in pagelist:
                    ss2, rp2 = html_get(ss, url)
                    findulist(uinfo, rp2.text)
                try:
                    for u in uinfo:
                        print(u)
                        special_emails_str = q.special_emails
                        special_emails_list = special_emails_str.split(',')
                        if str_in_list(u[2], special_emails_list):
                            continue
                        if u[4] == "已禁用":
                            status = 0
                        else:
                            status = 1
                        temp_str = u[3].string
                        temp_list = temp_str.split(" ")
                        rl = int(temp_str.split(" ")[0])
                        if temp_list[1] == "GB":
                            rl = rl * 1024
                        # print(type(u[0]), u[0])
                        userid = None
                        if u[0]:
                            userid = u[0]
                            IRedAdminUser.objects.update_or_create(
                                email=u[2],
                                defaults={
                                    'userid': userid,
                                    'name': u[1],
                                    'status': status,
                                    'mailbox_quota': rl
                                }
                            )
                except Exception as e:
                    msg = '从iRedAdmin刷新用户至本地 Exception: %s' % e
                else:
                    messages_status = 1
                    msg = '从iRedAdmin刷新用户至本地：成功。'
                finally:
                    if messages_status == 1:
                        messages.success(request, msg)
                    else:
                        messages.error(request, msg)
                    # return
                # printulist(uinfo)
            print(msg)
    flush_users.short_description = "从iRedAdmin刷新用户至本地"


@admin.register(IRedAdminUser)
class IRedAdminUserAdmin(ImportExportModelAdmin):
    list_display = ['userid', 'name', 'email', 'color_status', 'display_mailbox_quota', 'language', 'create_time']
    list_display_links = ['userid', 'name', 'email']
    actions = ['restart_password', 'get_user_info' ,'change_status', 'update_users']
    search_fields = ['userid', 'name', 'email', ]
    readonly_fields = ['password', 'restart_password_count', 'restart_password_time']
    # list_editable = ['userid']
    ordering = ['email']

    # def display_mailbox_quota(self, obj):
    #     # print(type(obj), obj)
    #     return colour_is_or_no(obj.is_mail_success, obj.get_is_mail_success_display())
    # display_mailbox_quota.short_description = "是否成功发送邮件"
    # display_mailbox_quota.admin_order_field = 'is_mail_success'
    #

    def display_mailbox_quota(self, obj):
        mailbox_quota = obj.mailbox_quota

        if mailbox_quota / 1024 >= 1:
            return str(obj.mailbox_quota/1024) + ' G'
        else:
            return str(obj.mailbox_quota) + ' M'
    display_mailbox_quota.short_description = '容量'
    display_mailbox_quota.admin_order_field = 'mailbox_quota'

    def restart_password(self, request, queryset):
        for user in queryset:
            messages_status = 0
            msg = '登录不成功，请排查。'
            status, domain, ss, rp = login(user.domain)
            if status:
                msg1 = '员工编号: {0}, 姓名: {1}, 邮箱: {2}, '.format(user.userid, user.name, user.email)
                msg2 = '重置密码：失败。'
                password = restart_password(domain, ss, user)
                if password:
                    msg2 = '重置密码为：{}'.format(password)
                    user.password = password
                    user.save()
                    messages_status = 1
                msg = msg1 + msg2
            if messages_status == 1:
                messages.success(request, msg)
            else:
                messages.error(request, msg)
    restart_password.short_description = "重置密码"

    def get_user_info(self, request, queryset):
        for user in queryset:
            try:
                msg = '员工编号：{0}，姓名：{1}，Email：{2}，密码：{3}。'.format(user.userid, user.name, user.email, user.password)
            except Exception as e:
                msg = '获取用户信息失败，Exception: %s' % e
                messages_status = 0
            else:
                messages_status = 1
            if messages_status == 1:
                messages.success(request, msg)
            else:
                messages.error(request, msg)
    get_user_info.short_description = "获取用户信息"

    def change_status(self, request, queryset):
        for user in queryset:
            messages_status = 0
            status, iredadmin, ss, rp = login(user.domain)
            msg = '登录不成功，请排查。'
            if status:
                msg1 = '员工编号: {0}, 姓名: {1}, 邮箱: {2}, '.format(user.userid, user.name, user.email)
                msg2 = '禁用/启用：失败！请排查问题。'
                if user.status == 1:
                    user.status = 0
                else:
                    user.status = 1
                status2 = modify_user(iredadmin, ss, user)
                if status2:
                    user.save()
                    messages_status = 1
                    if user.status == 1:
                        msg2 = '已启用。'
                    else:
                        msg2 = '已禁用。'
                msg = msg1 + msg2
            if messages_status == 1:
                messages.success(request, msg)
            else:
                messages.error(request, msg)
    change_status.short_description = "禁用/启用"

    def save_model(self, request, obj, form, change):
        is_save = False
        messages_status = 0
        msg = '登录不成功，请排查。'
        status, domain, ss, rp = login(obj.domain)
        if status:
            if '@' in obj.email:
                obj.email = obj.email.split('@')[0]
            obj.email = obj.email + '@' + obj.domain.domain
            msg1 = '员工编号: {0}, 姓名: {1}, 邮箱: {2}, '.format(obj.userid, obj.name, obj.email)
            msg2 = '保存/修改失败。'
            if change:
                status = modify_user(domain, ss, obj)
                if status:
                    msg2 = '修改成功。'
                    is_save = True
            else:
               #if '@' in obj.email:
               #    obj.email = obj.email.split('@')[0]
               #obj.email = obj.email + '@' + obj.domain.domain
                create_status = create_user(domain, ss, obj)
                if create_status:
                    msg2 = '第一步，创建成功。第二步，设置属性失败。'
                    data = {
                        'accountStatus': 'active',
                        'cn': obj.name,
                        'preferredLanguage': obj.language,
                        'mailQuota': obj.mailbox_quota,
                        'employeeNumber': obj.userid
                    }
                    modify_status = modify_user(domain, ss, obj, data)
                    if modify_status:
                        msg2 = '保存成功。'
                        is_save = True
            msg = msg1 + msg2
        print(msg)
        if is_save:
            # obj.status = 1
            messages_status = 1
            obj.save()
        if messages_status == 1:
            messages.success(request, msg)
        else:
            messages.ERROR(request, msg)

    def color_status(self, obj):
        # print(type(obj), obj)
        if obj.status == 0:
            return format_html('<span style="color:red">{}</span>', obj.get_status_display())
        else:
            return format_html('<span style="color:green">{}</span>', obj.get_status_display())
    color_status.short_description = "状态"
    color_status.admin_order_field = 'status'

    def update_users(self, request, queryset):
        for user in queryset:
            messages_status = 0
            status, doamin, ss, rp = login(user.domain)
            msg = '登陆不成功，请排查。'
            if status:
                msg1 = '员工编号: {0}, 姓名: {1}, 邮箱: {2}, '.format(user.userid, user.name, user.email)
                status2 = modify_user(doamin, ss, user)
                if status2:
                    messages_status = 1
                    msg2 = '更新：成功。'
                else:
                    msg2 = '更新：失败。'
                msg = msg1 + msg2
            print(msg)
            if messages_status == 1:
                messages.success(request, msg)
            else:
                messages.error(request, msg)
    update_users.short_description = "更新用户至iRedAdmin"




