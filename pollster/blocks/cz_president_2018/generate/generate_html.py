'''generates html for screenshot'''
langs = ["en_US","cs_CZ"]

from babel.dates import format_date, format_datetime, format_time
from datetime import date, datetime, time
import jinja2
import json
import os
import shlex
import subprocess
import yaml

# get path
try:
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
except:
    dir_path = ""

# load settings.json
with open(dir_path + "../settings.yaml") as fin:
    settings = yaml.load(fin)
with open(dir_path + settings['block_reverse_path_dir'] + "../server_settings.json") as fin:
    server_settings = json.load(fin)

templateLoader = jinja2.FileSystemLoader( searchpath=[dir_path + "./templates", server_settings['app_dir'] + "templates"] )
templateEnv = jinja2.Environment( loader=templateLoader )

# app = Flask(__name__)

with open(dir_path + "../estimate/candidates_estimated.json") as fin:
    candidates = json.load(fin)

# date
stats = os.stat(dir_path + "../estimate/candidates_estimated.json")

# images
image_path = server_settings['app_url'] + settings['block_path_url'] + "images/"

for lang in langs:
    # load texts
    with open(server_settings['app_dir'] + "languages/texts." + lang + ".yaml") as fin:
        texts = yaml.load(fin)
    with open(dir_path + "../texts." + lang + ".yaml") as fin:
        localtexts = yaml.load(fin)
    for k in localtexts:
        texts[k] = localtexts[k]

    date = format_date(datetime.fromtimestamp(stats.st_mtime), locale=lang)

    # block
    template = templateEnv.get_template('core.html')
    core = template.render(candidates=candidates,image_path=image_path,server_settings=server_settings, settings=settings,texts=texts,date=date)
    html = core
    with open(dir_path + "../block." + lang + ".html","w") as fout:
        fout.write(html)

    # picture
    template = templateEnv.get_template('picture.html')
    core = template.render(candidates=candidates,image_path=image_path,server_settings=server_settings, settings=settings,texts=texts,date=date)

    html = core
    # print(html[:100])
    with open(dir_path + "../pictures/picture." + lang + ".html","w") as fout:
        fout.write(html)

    # generate png
    cmd = 'xvfb-run --server-args="-screen 0, 1200x800x24" --auto-servernum /usr/bin/cutycapt --min-width=780 --min-height=528 --url=' + server_settings['app_url'] + settings['block_path_url'] + 'pictures/picture.' + lang + '.html --out=' + server_settings['app_dir'] + settings['block_path_url'] + 'pictures/picture.' + lang + '.' + str(stats.st_mtime) + '.png'
    call_params = shlex.split(cmd)
    proc = subprocess.Popen(call_params)

    # thumbnail
    template = templateEnv.get_template('thumbnail.html')
    html = template.render(candidates=candidates,image_path=image_path,server_settings=server_settings, settings=settings,texts=texts,date=date)
    with open(dir_path + "../pictures/thumbnail." + lang + ".html","w") as fout:
        fout.write(html)
    # generate png
    cmd = '/usr/bin/xvfb-run --server-args="-screen 0, 1200x800x24" --auto-servernum /usr/bin/cutycapt --min-width=780 --min-height=528 --url=' + server_settings['app_url'] + settings['block_path_url'] + 'pictures/thumbnail.' + lang + '.html --out=' + server_settings['app_dir'] + settings['block_path_url'] + 'pictures/bigthumbnail.' + lang + '.' + str(stats.st_mtime) + '.png'
    call_params = shlex.split(cmd)
    proc = subprocess.Popen(call_params)
    proc.communicate()
    cmd = '/usr/bin/convert ' + server_settings['app_dir'] + settings['block_path_url'] + 'pictures/bigthumbnail.' + lang + '.' + str(stats.st_mtime) + '.png -resize 238x158 ' + server_settings['app_dir'] + settings['block_path_url'] + 'pictures/thumbnail.' + lang + '.' + str(stats.st_mtime) + '.png'
    call_params = shlex.split(cmd)
    proc = subprocess.Popen(call_params)
    proc.communicate()

    # block
    block = {
        'code': 'cz_president_2018',
        'language': lang,
        'name': texts['name'],
        'subname': texts['subname'],
        'timestamp':stats.st_mtime,
        'date': date,
        'description': texts['description'],
        'fb': texts['fb'].format(first_candidate=candidates[0]['name'], second_candidate=candidates[1]['name'], first_candidate_percents=round(candidates[0]['probability']*100), second_candidate_percents=round(candidates[1]['probability']*100)),
        'twitter': texts['twitter'].format(first_candidate=candidates[0]['name'], second_candidate=candidates[1]['name'], first_candidate_percents=round(candidates[0]['probability']*100), second_candidate_percents=round(candidates[1]['probability']*100)),
        'thumbnail': 'pictures/thumbnail.' + lang + '.' + str(stats.st_mtime) + '.png',
        'picture': 'pictures/picture.' + lang + '.' + str(stats.st_mtime) + '.png',
        'content': 'index.' + lang + '.html',
        'tags': texts['tags'],
        'data': 'estimate/candidates_estimated.json',
        'slug': texts['slug']
    }

    with open(dir_path + "../block." + lang + ".yaml", "w") as fout:
        yaml.dump(block,fout)
