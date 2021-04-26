import json
import os

from botoy import Botoy

with open("botoy.json") as f:
    config = json.load(f)

qq = config["qq"]
os.environ["BOTQQ"] = str(qq)
bot = Botoy(qq=qq, use_plugins=True)

if __name__ == "__main__":
    bot.run()
