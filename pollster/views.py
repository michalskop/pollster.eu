from pollster import app
from flask import redirect, render_template, send_from_directory, url_for
from flask_cache import Cache

import server_settings

locale = "cs_CZ"

cache = Cache(app)

@app.route('/<page>/<subpage>/pictures/<path:filename>')
def get_picture(page,subpage,filename):
    #print(server_settings.app_dir + "blocks/" + subpage)
    # return send_from_directory("/home/michal/project/pollster.eu/application/blocks/cz_president_2018/pictures", filename)
    return send_from_directory(server_settings.app_dir + "blocks/" + subpage + "/pictures/", filename, as_attachment=False)

@app.route('/blocks/<block>/<path:filename>')
def get_file(block,filename):
    return send_from_directory(server_settings.app_dir + "blocks/" + block + "/", filename, as_attachment=False)

@app.route('/')
def redirect_frontpage():
    return redirect(url_for('subpage',page='cz',subpage='1'))

@app.route('/<page>/')
def redirect_page(page):
    return redirect(url_for('subpage',page=page,subpage='1'))

@app.route('/<page>/<subpage>/')
@cache.cached(timeout=1)
def subpage(page,subpage):
    import yaml
    with open(server_settings.app_dir + "../app_settings.yaml",encoding='utf-8') as fin:
        app_settings = yaml.load(fin)
    with open(server_settings.app_dir + "pages/" + page + "/settings.yaml",encoding='utf-8') as fin:
        page_settings = yaml.load(fin)

    # load texts
    with open(server_settings.app_dir + "languages/texts." + locale + ".yaml",encoding='utf-8') as fin:
        texts = yaml.load(fin)
    with open(server_settings.app_dir + "pages/" + page + "/texts." + locale + ".yaml",encoding='utf-8') as fin:
        localtexts = yaml.load(fin)
    for k in localtexts:
        texts[k] = localtexts[k]

    # load blocks
    blocks = []
    for block in page_settings['subpages']:
        with open(server_settings.app_dir + "blocks/" + block + "/block." + locale + ".html",encoding='utf-8') as fin:
            html = fin.read()
        with open(server_settings.app_dir + "blocks/" + block + "/block." + locale + ".yaml",encoding='utf-8') as fin:
            meta = yaml.load(fin)
        block = {
            "html": html,
            "meta": meta
        }
        blocks.append(block)


    return render_template('page.html',
                            server_settings = server_settings,
                            app_settings = app_settings,
                            settings = page_settings,
                            texts = texts,
                            locale = locale,
                            blocks = blocks)
