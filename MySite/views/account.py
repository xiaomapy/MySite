import os
import json
from uuid import uuid4
import markdown
from flask import Blueprint, render_template, request, redirect, session, jsonify

from settings import Base
from ..utils import Sql_hander
from ..utils import article_safe

account = Blueprint('account', __name__)


@account.before_request
def process_request():
    if not session.get('user_info'):
        return redirect("/login/")
    return None


@account.route('/backstage/')
def backstage():
    data_list = Sql_hander.select_all('SELECT id,title,create_time FROM article', [])
    return render_template('BackStage/BackStage.html', data_list=data_list)


@account.route('/write_article/', methods=['POST', 'GET'])
def write_article():
    if request.method == 'GET':
        cate_list = Sql_hander.select_all('SELECT id,title FROM category', [])
        return render_template('BackStage/write-article.html', cate_list=cate_list)

    title = request.form.get('title')
    content = request.form.get('editormd-html-code')
    content = markdown.markdown(content,extensions=Base.exts)

    cate_id = request.form.get('cate')
    desc = article_safe.article_desc(content)
    Sql_hander.insert_one('INSERT INTO ARTICLE (title,des,content,category_id) VALUE (%s,%s,%s,%s)',
                          (title, desc, content, cate_id))
    return redirect('/backstage/')


@account.route('/backstage/delete_article/', methods=['POST'])
def delect_article():
    data = json.loads(request.get_data().decode())
    del_id = int(data.get('article_id'))
    Sql_hander.insert_one('DELETE FROM article WHERE id=%s', (del_id,))
    return '删除成功'


@account.route('/backstage/edit_article/<int:nid>', methods=['POST', 'GET'])
def edit_article(nid):
    if request.method == "GET":
        article_obj = Sql_hander.select_one(
            'SELECT A.id,A.title,A.create_time,A.des,A.content,CATEGORY.title as title2 FROM (SELECT id,title,create_time,des,content,category_id FROM article WHERE id=%s) as A LEFT JOIN CATEGORY ON A.category_id=CATEGORY.ID',
            (nid,))
        cate_list = Sql_hander.select_all('SELECT id,title FROM category', [])
        return render_template('backstage/edit_article.html', article_obj=article_obj, cate_list=cate_list)

    title = request.form.get('title')
    content = request.form.get('editormd-html-code')
    content = markdown.markdown(content, extensions=Base.exts)

    cate_id = request.form.get('cate')
    desc = article_safe.article_desc(content)
    Sql_hander.insert_one('UPDATE article set title=%s,des=%s,content=%s,category_id=%s WHERE id=%s',
                          (title, desc, content, cate_id, nid))
    return redirect('/backstage/')


@account.route('/upload/', methods=['POST', 'GET'])
def upload():
    obj = request.files.get('editormd-image-file')
    name = str(uuid4())
    path = os.path.join(Base.BASE_DIR, 'blog', "static", "upload", name)
    print(path)
    with open(path, 'wb') as f:
        for line in obj:
            f.write(line)

    res = {
        'success': 1,
        'message': u'图片上传成功',
        'url': "/static/upload/" + name
    }
    return jsonify(res)
