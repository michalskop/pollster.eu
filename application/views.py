from application import app
from flask import render_template, send_from_directory


locale = "cs_CZ"

@app.route('/<page>/<subpage>/pictures/<path:filename>')
def get_picture(page,subpage,filename):
    import json
    with open("server_settings.json") as fin:
        server_settings = json.load(fin)

    print(server_settings['app_dir'] + "blocks/" + subpage)
    # return send_from_directory("/home/michal/project/pollster.eu/application/blocks/cz_president_2018/pictures", filename)
    return send_from_directory(server_settings['app_dir'] + "blocks/" + subpage + "/pictures/", filename, as_attachment=False)

@app.route('/<page>/<subpage>')
def subpage(page,subpage):
    import yaml
    import json
    with open("server_settings.json") as fin:
        server_settings = json.load(fin)
    with open("app_settings.yaml") as fin:
        app_settings = yaml.load(fin)
    with open(server_settings['app_dir'] + "pages/" + page + "/settings.yaml") as fin:
        page_settings = yaml.load(fin)

    # load texts
    with open(server_settings['app_dir'] + "languages/texts." + locale + ".yaml") as fin:
        texts = yaml.load(fin)
    with open(server_settings['app_dir'] + "pages/" + page + "/texts." + locale + ".yaml") as fin:
        localtexts = yaml.load(fin)
    for k in localtexts:
        texts[k] = localtexts[k]

    # load blocks
    blocks = []
    for block in page_settings['subpages']:
        with open(server_settings['app_dir'] + "blocks/" + block + "/block." + locale + ".html") as fin:
            html = fin.read()
        with open(server_settings['app_dir'] + "blocks/" + block + "/block." + locale + ".yaml") as fin:
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
