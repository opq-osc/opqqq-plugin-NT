# -*- coding:utf-8 -*-
import base64
import os
from enum import Enum
from io import BytesIO

from botoy import ctx, S, mark_recv, jconfig
from PIL import Image, ImageDraw, ImageFont
from prettytable import PrettyTable

try:
	import ujson as json
except ImportError:
	import json

# ==========================================

RESOURCES_BASE_PATH = "./resources/image-custom"

# ==========================================

# 屏蔽群 例：[12345678, 87654321]
blockGroupNumber = []
# 是否自动制作表情列表图 默认是
qrListOpen = True
# 表情包字体
fontPath = f"{RESOURCES_BASE_PATH}/font/simhei.ttf"
# 最小字体限制
fontMin = 15
# 列表文字间距
space = 5
# 显示表情包底图列表命令
pictureListCommand = ["img list", "表情包模板"]
# 表情包生成命令
primaryMatchingSuffix = [".jpg", ".JPG", ".png", '.PNG']
# 更换背景图命令
switchEmojiCommandPrefix = ["img ", "换图 "]  # 注意命令后一定要有个空格用于区分


# ==========================================


async def main():
	if m := ctx.group_msg:
		if Tools.commandMatch(m, blockGroupNumber):
			return
		if not Tools.textOnly(m):
			return
		if not Tools.isNotBot(m):
			return
		if m.text_match('表情包帮助'):
			Help = '表情包生成插件帮助：\n1.全部表情包模板列表【img list】或【表情包模板】\n2.更换表情包模板：【img [更换模板名称]】或【换图 [更换模板名称]】\n3.生成表情包：[文字内容]+【.jpg】或【.png】'
			await S.text(Help)
			return
		if img := mainEntrance(m, m.msg_head.SenderUin):
			try:
				await S.image(img)
			except Exception:
				await S.text(text=img)


mark_recv(main, name='自定义表情包', author='@xiyaowong', usage='发送 表情包帮助 获取完整菜单')


class Model(Enum):
	ALL = "_all"
	BLURRY = "_blurry"
	SEND_AT = "_send_at"
	SEND_DEFAULT = "_send_default"


class Status(Enum):
	SUCCESS = "_success"
	FAILURE = "_failure"


class Tools:
	@staticmethod
	def textOnly(msg) -> bool:
		if msg.text:
			return True
		else:
			return False

	@staticmethod
	def isNotBot(msg) -> bool:
		if msg.msg_head.SenderUin != jconfig.get('qq'):
			return True
		else:
			return False

	@staticmethod
	def writeFile(p, content):
		with open(p, "w", encoding="utf-8") as f:
			f.write(content)

	@staticmethod
	def readFileByLine(p):
		if not os.path.exists(p):
			return Status.FAILURE
		with open(p, "r", encoding="utf-8") as f:
			return f.readlines()

	@staticmethod
	def readJsonFile(p):
		if not os.path.exists(p):
			return Status.FAILURE
		with open(p, "r", encoding="utf-8") as f:
			return json.loads(f.read())

	@staticmethod
	def readFileContent(p):
		if not os.path.exists(p):
			return Status.FAILURE
		with open(p, "r", encoding="utf-8") as f:
			return f.read().strip()

	@staticmethod
	def commandMatch(msg, commandList, model=Model.ALL) -> bool:
		msg = msg.text
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
	def checkFolder(dir):
		if not os.path.exists(dir):
			os.makedirs(dir)


def mainEntrance(msg, userQQ):
	# Emoticon list function
	if Tools.commandMatch(msg, pictureListCommand, Model.ALL):
		makeList()
		listFilePath = f"{RESOURCES_BASE_PATH}/list.jpg"
		if os.path.exists(listFilePath):
			# Tools.sendPictures(userGroup=userGroup, picPath=listFilePath, bot=bot)
			return listFilePath
	# Render emoji function
	if Tools.commandMatch(msg, primaryMatchingSuffix, Model.BLURRY):
		msg = msg.text
		text = msg[: msg.rfind(".")]
		emoticonId = getEmojiId(userQQ)
		result, img = drawing(emoticonId, text)
		if result == Status.SUCCESS:
			# Tools.sendPictures(userGroup=userGroup, picPath=resultPath, bot=bot)
			return img
	# Change emoji function
	if Tools.commandMatch(msg, switchEmojiCommandPrefix, Model.BLURRY):
		msg = msg.text
		emoticonAlias = msg[msg.find(" ") + 1:]
		result = changeEmoji(userQQ, emoticonAlias)
		if result == Status.SUCCESS:
			sendMsg = f"表情已更换为 [{emoticonAlias}] 喵~"
			# Tools.sendText(userGroup=userGroup,msg=sendMsg,bot=bot,model=Model.SEND_AT,atQQ=userQQ)
			return sendMsg


def changeEmoji(userQQ, emoticonAlias):
	emojiConfiguration = f"{RESOURCES_BASE_PATH}/image_data/bieming/name.ini"
	if not os.path.exists(emojiConfiguration):
		raise Exception(f"表情配置 {emojiConfiguration} 不存在！")
	emoticonId = queryEmoticonId(emoticonAlias)
	currentEmoji = getEmojiId(userQQ)
	if emoticonId != Status.FAILURE and emoticonId != currentEmoji:
		p = f"{RESOURCES_BASE_PATH}/image_data/qqdata/{userQQ}.ini"
		Tools.writeFile(p, emoticonId)
		return Status.SUCCESS
	return Status.FAILURE


def queryEmoticonId(emoticonAlias):
	emojiConfiguration = f"{RESOURCES_BASE_PATH}/image_data/bieming/name.ini"
	if not os.path.exists(emojiConfiguration):
		raise Exception(f"表情配置 {emojiConfiguration} 不存在！")
	for line in Tools.readFileByLine(emojiConfiguration):
		line = line.strip()
		alias = line.split(" ")[0]
		codename = line.split(" ")[1]
		if alias == emoticonAlias:
			return codename
	return Status.FAILURE


def getEmojiId(userQQ):
	p = f"{RESOURCES_BASE_PATH}/image_data/qqdata/{userQQ}.ini"
	c = Tools.readFileContent(p)
	return "initial" if c == Status.FAILURE else c


def drawing(emoticonId, text):
	picPathJPG = f"{RESOURCES_BASE_PATH}/image_data/{emoticonId}/{emoticonId}.jpg"
	picPathPNG = f"{RESOURCES_BASE_PATH}/image_data/{emoticonId}/{emoticonId}.png"
	picPath = ""
	# Check that the file exists
	if os.path.exists(picPathJPG):
		picPath = picPathJPG
	elif os.path.exists(picPathPNG):
		picPath = picPathPNG
	else:
		return Status.FAILURE
	configPath = f"{RESOURCES_BASE_PATH}/image_data/{emoticonId}/config.ini"
	if not os.path.exists(configPath):
		return Status.FAILURE

	# Drawing
	config = Tools.readJsonFile(configPath)
	img = Image.open(picPath)
	draw = ImageDraw.Draw(img)
	color = config["color"]
	fontSize = config["font_size"]
	fontMax = config["font_max"]
	imageFontCenter = (config["font_center_x"], config["font_center_y"])
	imageFontSub = config["font_sub"]
	# 设置字体暨字号
	ttfront = ImageFont.truetype(fontPath, fontSize)
	fontLength = ttfront.getsize(text)
	while fontLength[0] > fontMax:
		fontSize -= imageFontSub
		ttfront = ImageFont.truetype(fontPath, fontSize)
		fontLength = ttfront.getsize(text)
	if fontSize <= fontMin:
		return Status.FAILURE
	# 自定义打印的文字和文字的位置
	if fontLength[0] > 5:
		draw.text(
			(
				imageFontCenter[0] - fontLength[0] / 2,
				imageFontCenter[1] - fontLength[1] / 2,
			),
			text,
			fill=color,
			font=ttfront,
		)

	dirPath = f"{RESOURCES_BASE_PATH}/cache"
	Tools.checkFolder(dirPath)
	temp = BytesIO()
	img.save(temp, format="JPEG")
	return Status.SUCCESS, base64.b64encode(temp.getvalue()).decode('utf-8')


def makeList():
	if qrListOpen:
		p = f"{RESOURCES_BASE_PATH}/image_data/bieming/name.ini"
		lines = Tools.readFileByLine(p)
		if lines == Status.FAILURE:
			raise Exception(f"{p} 表情包配置不存在！")
		temp_out = []
		tab = PrettyTable()
		i = 0
		for line in lines:
			i += 1
			name = line.strip().split()[0]
			temp_out.append(name)
			if not i % 5:
				i = 0
				tab.add_row(temp_out)
				temp_out = []
		if len(temp_out):
			i = 5
			Len = len(temp_out)
			while i - Len:
				i -= 1
				temp_out.append('')
		tab.add_row(temp_out)
		info = str(tab)[108:]
		font = ImageFont.truetype(fontPath, 15, encoding='utf-8')
		im = Image.new('RGB', (10, 10), (0, 0, 0, 0))
		draw = ImageDraw.Draw(im, 'RGB')
		img_size = draw.multiline_textsize(info, font=font)
		im_new = im.resize((img_size[0] + space * 2, img_size[1] + space * 2))
		draw = ImageDraw.Draw(im_new, 'RGB')
		draw.multiline_text((space, space), info, fill=(255, 255, 255), font=font)
		im_new.save(f"{RESOURCES_BASE_PATH}/list.jpg", 'jpeg')
