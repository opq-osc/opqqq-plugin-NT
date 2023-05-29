# -*- coding:utf-8 -*-

import base64
import random
from enum import Enum
from io import BytesIO

import httpx
from botoy import ctx, S, mark_recv, jconfig
from PIL import Image, ImageDraw

try:
	import ujson as json
except Exception:
	import json

# ==========================================
RESOURCES_BASE_PATH = "./resources/throw-creep"

# ==========================================

# 屏蔽群 例：[12345678, 87654321]
blockGroupNumber = []
# 触发命令列表
creepCommandList = ["爬", "爪巴", "给爷爬", "爬啊", "快爬"]
throwCommandList = ["丢", "我丢"]
# 爬的概率 越大越容易爬 取值区间 [0, 100]
creep_limit = 80
# bot的QQ号，默认从botoy.json读取
botQQ = jconfig.qq


# ==========================================


async def Pa():
	if m := ctx.group_msg:
		if m.text_match('给爷爬帮助'):
			Info = '给爷爬插件命令列表如下：\n['
			for cmd in creepCommandList:
				Info += cmd + '，'
			Info += ']\n['
			for cmd in throwCommandList:
				Info += cmd + '，'
			Info += ']'
			await S.text(Info)
		if not Tools.atOnly(m):
			return
		if Tools.commandMatch(m, blockGroupNumber):
			return
		if img := match(m):
			await S.image(img)


class Status(Enum):
	SUCCESS = "_success"
	FAILURE = "_failure"


class Model(Enum):
	ALL = "_all"
	BLURRY = "_blurry"
	SEND_AT = "_send_at"
	SEND_DEFAULT = "_send_default"


class Tools:
	@staticmethod
	def atOnly(msg) -> bool:
		At = msg.msg_body.AtUinLists
		if At:
			if not At[0].Uin == botQQ and len(At) == 1:  # 只艾特一个人且不是bot
				return True
		else:
			return False

	@staticmethod
	def commandMatch(msg, commandList, model=Model.ALL) -> bool:
		if model == Model.ALL:
			for c in commandList:
				if c == msg:
					return True
		if model == Model.BLURRY:
			for c in commandList:
				if c in msg:
					return True
		return False

	@staticmethod
	def identifyAt(msg):
		try:
			return msg.msg_body.AtUinLists[0].Uin
		except Exception:
			return Status.FAILURE


def match(msg):
	# creep features
	result = Tools.commandMatch(msg.text, creepCommandList, model=Model.BLURRY)
	if result:
		# Parsing parameters
		ToUser = Tools.identifyAt(msg)
		if ToUser != Status.FAILURE:
			qq = int(ToUser)
			img = ThrowAndCreep.creep(qq)
			return img
	# throe features
	result = Tools.commandMatch(msg.text, throwCommandList, model=Model.BLURRY)
	if result:
		# Parsing parameters
		ToUser = Tools.identifyAt(msg)
		if ToUser != Status.FAILURE:
			qq = int(ToUser)
			img = ThrowAndCreep.throw(qq)
			return img


class Network:
	@staticmethod
	def getBytes(url, headers="", timeout=10):
		if headers == "":
			headers = {
				"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
			}
		try:
			return httpx.get(url=url, headers=headers, timeout=timeout).read()
		except:
			return Status.FAILURE


class ThrowAndCreep:
	_avatar_size = 139
	_center_pos = (17, 180)

	@staticmethod
	def getAvatar(url):
		img = Network.getBytes(url)
		return img

	@staticmethod
	def randomClimb():
		randomNumber = random.randint(1, 100)
		if randomNumber < creep_limit:
			return True
		return False

	@staticmethod
	def get_circle_avatar(avatar, size):
		avatar.thumbnail((size, size))

		scale = 5
		mask = Image.new("L", (size * scale, size * scale), 0)
		draw = ImageDraw.Draw(mask)
		draw.ellipse((0, 0, size * scale, size * scale), fill=255)
		mask = mask.resize((size, size), Image.ANTIALIAS)

		ret_img = avatar.copy()
		ret_img.putalpha(mask)

		return ret_img

	@classmethod
	def creep(cls, qq) -> str:
		creeped_who = qq
		id = random.randint(0, 53)

		whetherToClimb = cls.randomClimb()

		if not whetherToClimb:
			return f"{RESOURCES_BASE_PATH}/不爬.jpg"

		avatar_img_url = "https://q1.qlogo.cn/g?b=qq&nk={QQ}&s=640".format(
			QQ=creeped_who
		)
		res = cls.getAvatar(avatar_img_url)
		avatar = Image.open(BytesIO(res)).convert("RGBA")
		avatar = cls.get_circle_avatar(avatar, 100)

		creep_img = Image.open(f"{RESOURCES_BASE_PATH}/pa/爬{id}.jpg").convert("RGBA")
		creep_img = creep_img.resize((500, 500), Image.ANTIALIAS)
		creep_img.paste(avatar, (0, 400, 100, 500), avatar)
		temp = BytesIO()
		# dirPath = f"{RESOURCES_BASE_PATH}/avatar"
		# Tools.checkFolder(dirPath)
		# creep_img.save(f"{RESOURCES_BASE_PATH}/avatar/{creeped_who}_creeped.png")
		creep_img.save(temp, format="png")

		return base64.b64encode(temp.getvalue()).decode('utf-8')  # 返回base64编码的图片

	@classmethod
	def throw(cls, qq) -> str:
		threw_who = qq

		avatar_img_url = "http://q1.qlogo.cn/g?b=qq&nk={QQ}&s=640".format(
			QQ=threw_who
		)

		res = cls.getAvatar(avatar_img_url)
		avatar = Image.open(BytesIO(res)).convert("RGBA")
		avatar = cls.get_circle_avatar(avatar, cls._avatar_size)

		rotate_angel = random.randrange(0, 360)

		throw_img = Image.open(f"{RESOURCES_BASE_PATH}/throw.jpg").convert("RGBA")
		throw_img.paste(
			avatar.rotate(rotate_angel), cls._center_pos, avatar.rotate(rotate_angel)
		)
		temp = BytesIO()
		# dirPath = f"{RESOURCES_BASE_PATH}/avatar"
		# Tools.checkFolder(dirPath)
		# throw_img.save(f"{RESOURCES_BASE_PATH}/avatar/{threw_who}.png")
		throw_img.save(temp, format="png")

		return base64.b64encode(temp.getvalue()).decode('utf-8')


mark_recv(Pa, name="给爷爬", author="@xiyaowong", usage="发送 爬+@某人\n完整命令请发送 给爷爬帮助")
