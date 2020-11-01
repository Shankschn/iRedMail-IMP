from django.db import models

# Create your models here.

from django.db import models


class IRedAdminDomain(models.Model):

    domain = models.CharField(verbose_name='域', max_length=50, null=True, blank=True)

    admin_zh = models.CharField(verbose_name='管理员账号', max_length=50, null=True, blank=True)
    admin_mm = models.CharField(verbose_name='管理员密码', max_length=50, null=True, blank=True)

    special_emails = models.TextField(verbose_name='特殊电子邮箱', max_length=1000, null=True, blank=True,
                                      help_text='以英文逗号分隔，此处的邮箱将不会在此平台管理。建议将所有管理员邮箱填入此处。'
                                                '例如：postmaster@domain.com')
    url_admin = models.CharField(verbose_name='iRedAdmin 后台 URL', max_length=200, null=True, blank=True)
    url_login = models.CharField(verbose_name='iRedAdmin 登陆 URL', max_length=200, null=True, blank=True)
    url_user = models.CharField(verbose_name='iRedAdmin 用户 URL', max_length=200, null=True, blank=True)
    url_page = models.CharField(verbose_name='iRedAdmin 分页 URL', max_length=200, null=True, blank=True)
    url_create_user = models.CharField(verbose_name='iRedAdmin 创建用户 URL', max_length=200, null=True, blank=True)
    url_modify_user = models.CharField(verbose_name='iRedAdmin 修改用户 URL', max_length=200, null=True, blank=True)
    url_restart_password = models.CharField(verbose_name='iRedAdmin 重置密码 URL', max_length=200, null=True, blank=True)

    class Meta:
        # 数据库中表名称 默认app_表名
        # db_table = ''
        # Django Admin 中显示名名称
        verbose_name = '域'  # 单数
        verbose_name_plural = '域管理'  # 复数

    def __str__(self):
        return self.domain


class IRedAdminUser(models.Model):
    domain = models.ForeignKey(IRedAdminDomain, verbose_name='域', null=True, on_delete=models.CASCADE)
    userid = models.CharField(verbose_name='员工编号', max_length=20, null=True, blank=True,
                              help_text='一般：员工编号<br>'
                                        '特殊申请的邮箱：T + 4位顺序数字<br>'
                                        '邮箱经过更换的员工，原邮箱：OLD + "-" + 员工编号 + "-两位顺序数字"，新邮箱：员工编号')
    email = models.CharField(verbose_name='Email', max_length=50, unique=True)
    password = models.CharField(verbose_name='密码', max_length=50, null=True, blank=True)
    statuss = (
        (0, '禁用'),
        (1, '启用')
    )
    status = models.IntegerField(verbose_name='状态', choices=statuss, default=1)
    name = models.CharField(verbose_name='显示名称', max_length=50, null=True)
    languages = (
        ('zh_CN', '简体中文'),
        ('zh_TW', '繁體中文'),
        ('en_US', 'English'),
        ('ja_JP', 'Japanese (日本語)'),
    )
    language = models.CharField(verbose_name='偏好语言', max_length=10, choices=languages, default='zh_CN')
    mailbox_quota = models.IntegerField(verbose_name='邮箱容量（M）', default=10240)
    restart_password_count = models.IntegerField(verbose_name='重置密码次数', default=0)
    restart_password_time = models.TextField(verbose_name='重置密码时间', null=True, blank=True)
    remark = models.TextField(verbose_name='备注', null=True, blank=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        # 数据库中表名称 默认app_表名
        # db_table = ''
        # Django Admin 中显示名名称
        verbose_name = '用户管理'  # 单数
        verbose_name_plural = '用户管理'  # 复数

    def __str__(self):
        return str(self.userid) + " | " + str(self.name)


