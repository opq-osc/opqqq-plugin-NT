# -*- coding:utf-8 -*-

"""
    插件打包工具
"""

import os
import shutil

dir = '../plugins'

# 打包全部插件
ls = os.listdir('../plugins')

# 打包单个插件
# ls = ['bot_image_custom.py']

lsn = []
for l in ls:
    resource_name = l.replace('bot_', '').replace('_', '-').replace('.py', '')
    lsn.append({'old': l, 'r': resource_name})

base_dir = './out'
os.mkdir(base_dir)

for l in lsn:
    p_old_name = dir + '/' + l['old']
    dir_name = l['r']
    p = f'{base_dir}/{dir_name}/plugins'
    r = f'{base_dir}/{dir_name}/resources'
    os.makedirs(p)
    os.makedirs(r)

    shutil.copyfile(p_old_name, p + '/' + l['old'])

    bot = '../bot.py'
    o_bot = f'{base_dir}/{dir_name}/bot.py'
    shutil.copyfile(bot, o_bot)

    readme = '../readme.md'
    o_readme = f'{base_dir}/{dir_name}/readme.md'
    shutil.copyfile(readme, o_readme)

    i = '../botoy.json'
    o_i = f'{base_dir}/{dir_name}/botoy.json'
    shutil.copyfile(i, o_i)

    dir1 = f'../resources/{dir_name}'
    shutil.copytree(dir1, f'{r}/{dir_name}')
