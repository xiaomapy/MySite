from flask import Flask

from MySite.views.index import ind
from MySite.views.account import account


def create_app():
    """
    创建app应用
    :return:
    """
    app = Flask(__name__)

    # 引入配置文件并应用
    app.config.from_object("settings.Development")

    # 注册蓝图
    app.register_blueprint(ind)
    app.register_blueprint(account)

    return app
