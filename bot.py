# -*- coding:utf-8 -*-

from iotbot import IOTBOT, Action, GroupMsg

bot_qq = 12345678

bot = IOTBOT(
    qq = bot_qq,
    host = 'http://127.0.0.1', 
    port = 8888,
    use_plugins = True
)
action = Action(bot)


@bot.on_group_msg
def on_group_msg(ctx: GroupMsg):
    # 不处理自身消息
    if ctx.FromUserId == ctx.CurrentQQ:
        return


if __name__ == "__main__":
    bot.run()