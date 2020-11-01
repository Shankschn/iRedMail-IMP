# Blog
https://yudelei.com/171.html
# 描述
通过一个在 iRedMail-IMP / iRedAdmin 间接管理平台配置 iRedMail 相关信息及管理员帐号，iRedMail-IMP 间接通过管理员帐号登录 iRedAdmin 后台，从而实现管理帐号。本项目未实现与 iRedAdmin 开源版后台一样的功能。 目前只实现了 创建/修改/删除/禁用/搜索 帐号等基础功能。
# 适用于
iRedMail 0.9.9
# 环境
Python 3.7
# 依赖包
~~~
pip install django==2.2.*
pip install django-simpleui
pip install django-import-export
pip install beautifulsoup4
pip install mysqlclient # 若使用 MySql 或 MariaDB 需安装，默认使用 SQLite3 数据库。
~~~
# 使用
在 iRedAdmin 管理及设置中，配置"域"，"管理员账号"，"管理员密码"，"特殊电子邮箱"等基础信息后，即可使用。
