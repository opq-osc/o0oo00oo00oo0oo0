import base64
import os
import random
import time
from copy import copy
from io import BytesIO
from typing import Union

import httpx
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from botoy import GroupMsg, MsgTypes, Text, S, Action, jconfig
from botoy.decorators import these_msgtypes, ignore_botself

import connector


def get_avator(image: Union[int, str]):
    if isinstance(image, int):
        image = f'https://q1.qlogo.cn/g?b=qq&nk={image}&s=640'
        print(image)
    content = httpx.get(image, timeout=20).content
    return Image.open(BytesIO(content)).convert("RGBA")


font_size = 40
font_path = os.path.join('.', 'font', 'font.ttf')
font = ImageFont.truetype(font_path, font_size)

HELP = '''
- [加入游戏] 上桌
- [退出游戏] 下桌
- [出牌] 出xxx | 不要 | 过
- [指令] 叫地主 | 抢地主 | 不抢 | 不叫
- PS:5分钟无人加入将自动结束
'''

CARDS = list([
    {'id': 1, 'val': 20, 'name': '大王'},
    {'id': 2, 'val': 19, 'name': '小王'},
    {'id': 3, 'val': 16, 'name': '黑桃2'},
    {'id': 4, 'val': 16, 'name': '红心2'},
    {'id': 5, 'val': 16, 'name': '梅花2'},
    {'id': 6, 'val': 16, 'name': '方片2'},
    {'id': 7, 'val': 14, 'name': '黑桃A'},
    {'id': 8, 'val': 14, 'name': '红心A'},
    {'id': 9, 'val': 14, 'name': '梅花A'},
    {'id': 10, 'val': 14, 'name': '方片A'},
    {'id': 11, 'val': 13, 'name': '黑桃K'},
    {'id': 12, 'val': 13, 'name': '红心K'},
    {'id': 13, 'val': 13, 'name': '梅花K'},
    {'id': 14, 'val': 13, 'name': '方片K'},
    {'id': 15, 'val': 12, 'name': '黑桃Q'},
    {'id': 16, 'val': 12, 'name': '红心Q'},
    {'id': 17, 'val': 12, 'name': '梅花Q'},
    {'id': 18, 'val': 12, 'name': '方片Q'},
    {'id': 19, 'val': 11, 'name': '黑桃J'},
    {'id': 20, 'val': 11, 'name': '红心J'},
    {'id': 21, 'val': 11, 'name': '梅花J'},
    {'id': 22, 'val': 11, 'name': '方片J'},
    {'id': 23, 'val': 10, 'name': '黑桃10'},
    {'id': 24, 'val': 10, 'name': '红心10'},
    {'id': 25, 'val': 10, 'name': '梅花10'},
    {'id': 26, 'val': 10, 'name': '方片10'},
    {'id': 27, 'val': 9, 'name': '黑桃9'},
    {'id': 28, 'val': 9, 'name': '红心9'},
    {'id': 29, 'val': 9, 'name': '梅花9'},
    {'id': 30, 'val': 9, 'name': '方片9'},
    {'id': 31, 'val': 8, 'name': '黑桃8'},
    {'id': 32, 'val': 8, 'name': '红心8'},
    {'id': 33, 'val': 8, 'name': '梅花8'},
    {'id': 34, 'val': 8, 'name': '方片8'},
    {'id': 35, 'val': 7, 'name': '黑桃7'},
    {'id': 36, 'val': 7, 'name': '红心7'},
    {'id': 37, 'val': 7, 'name': '梅花7'},
    {'id': 38, 'val': 7, 'name': '方片7'},
    {'id': 39, 'val': 6, 'name': '黑桃6'},
    {'id': 40, 'val': 6, 'name': '红心6'},
    {'id': 41, 'val': 6, 'name': '梅花6'},
    {'id': 42, 'val': 6, 'name': '方片6'},
    {'id': 43, 'val': 5, 'name': '黑桃5'},
    {'id': 44, 'val': 5, 'name': '红心5'},
    {'id': 45, 'val': 5, 'name': '梅花5'},
    {'id': 46, 'val': 5, 'name': '方片5'},
    {'id': 47, 'val': 4, 'name': '黑桃4'},
    {'id': 48, 'val': 4, 'name': '红心4'},
    {'id': 49, 'val': 4, 'name': '梅花4'},
    {'id': 50, 'val': 4, 'name': '方片4'},
    {'id': 51, 'val': 3, 'name': '黑桃3'},
    {'id': 52, 'val': 3, 'name': '红心3'},
    {'id': 53, 'val': 3, 'name': '梅花3'},
    {'id': 54, 'val': 3, 'name': '方片3'},
])

ITEM_CARD = copy(CARDS)

card_list = [3, 3, 3, 3,  # 3
             4, 4, 4, 4,  # 4
             5, 5, 5, 5,  # 5
             6, 6, 6, 6,  # 6
             7, 7, 7, 7,  # 7
             8, 8, 8, 8,  # 8
             9, 9, 9, 9,  # 9
             10, 10, 10, 10,  # 10
             11, 11, 11, 11,  # J
             12, 12, 12, 12,  # Q
             13, 13, 13, 13,  # K
             14, 14, 14, 14,  # A
             16, 16, 16, 16,  # 2
             19,  # 小王
             20]  # 大王

r = connector.get_connection()

# width += int(w / 3)
# result.paste(img, box=(int(width / 3.5), round(height / 3 - h / 3)))
#
# width += int(w / 2.5)
# result.paste(img, box=(int(width / 2.8), round(height / 3 - h / 3))

# r.lpush("{}_dou_dizhu_user".format(858734573), "11703975")
# r.lpush("{}_dou_dizhu_user".format(858734573), "464606682")
# r.lpush("{}_dou_dizhu_user".format(858734573), "1982890538")


# ddz_handler = SessionHandler(
#     ignore_botself,
#     these_msgtypes(MsgTypes.TextMsg)
# ).receive_group_msg()


@ignore_botself
@these_msgtypes(MsgTypes.TextMsg)
def receive_group_msg(ctx: GroupMsg):
    content = ctx.Content
    if content == "斗地主":
        Text(HELP)
    if content == "上桌":
        if r.get("{}_dou_dizhu_IsOn".format(ctx.FromGroupId)) == "True":
            Text("当前对局一开始,请结束后重新创建")
        else:
            r.set("{}_dou_dizhu_IsOn".format(ctx.FromGroupId), "False")
            if str(ctx.FromUserId) not in r.lrange("{}_dou_dizhu_user".format(ctx.FromGroupId), 0, -1):
                r.rpush("{}_dou_dizhu_user".format(ctx.FromGroupId), str(ctx.FromUserId))
                start(ctx)
    if content == '开始':
        if str(ctx.FromUserId) in r.lrange("{}_dou_dizhu_user".format(ctx.FromGroupId), 0, -1):
            start(ctx)
    if content == '结束斗地主':
        if str(ctx.FromUserId) in r.lrange("{}_dou_dizhu_user".format(ctx.FromGroupId), 0, -1):
            for i in r.keys("{}_dou_dizhu_*".format(ctx.FromGroupId)):
                r.delete(i)
            for root, dirs, files in os.walk(os.path.dirname(__file__) + "/cache"):
                for name in files:
                    if name.startswith("{}_".format(ctx.FromGroupId)):
                        os.remove(os.path.join(root, name))
        Text("已结束本局游戏")
    if content[:1] == "出":
        # TODO:出牌
        print(content)


def start(ctx: GroupMsg):
    user_num = r.llen("{}_dou_dizhu_user".format(ctx.FromGroupId))
    S.bind(ctx).text("当前斗地主人数({}/3)".format(user_num))
    if user_num == 3:
        # 生成一副牌
        for i in CARDS:
            r.lpush("{}_{}_dou_dizhu_card".format(ctx.FromGroupId, i["val"]), i["val"])
        # 本局已开始
        r.set("{}_dou_dizhu_IsOn".format(ctx.FromGroupId), "True")
        # 开始洗牌
        random.shuffle(card_list)
        first_cards = sort(card_list[3:20])
        second_cards = sort(card_list[20:37])
        third_cards = sort(card_list[37:54])
        landholder_cards = sort(card_list[0:3])
        # 给到每个玩家发牌
        # dou_dizhu_user = r.blpop("{}_dou_dizhu_user".format(ctx.FromGroupId))[1]
        dou_dizhu_user = r.lrange("{}_dou_dizhu_user".format(ctx.FromGroupId), 0, -1)
        for i in anti_replace(first_cards):
            item = 0
            for j in reversed(range(len(CARDS))):
                if item == 0 and str(CARDS[j]['val']) == str(i):
                    item += 1
                    r.blpop("{}_{}_dou_dizhu_card".format(ctx.FromGroupId, i), timeout=2)
                    r.lpush("{}_dou_dizhu_user_{}_card".format(ctx.FromGroupId, dou_dizhu_user[0]), CARDS[j]["name"])
                    r.lpush("{}_dou_dizhu_user_{}_card_val".format(ctx.FromGroupId, dou_dizhu_user[0]), CARDS[j]["val"])
                    del CARDS[j]
        for i in anti_replace(second_cards):
            item = 0
            for j in reversed(range(len(CARDS))):
                if item == 0 and str(CARDS[j]['val']) == str(i):
                    item += 1
                    r.lpush("{}_dou_dizhu_user_{}_card".format(ctx.FromGroupId,
                                                               dou_dizhu_user[1]), CARDS[j]["name"])
                    r.blpop("{}_{}_dou_dizhu_card".format(ctx.FromGroupId, i), timeout=2)
                    r.lpush("{}_dou_dizhu_user_{}_card_val".format(ctx.FromGroupId, dou_dizhu_user[1]), CARDS[j]["val"])
                    del CARDS[j]
        for i in anti_replace(third_cards):
            item = 0
            for j in reversed(range(len(CARDS))):
                if item == 0 and str(CARDS[j]['val']) == str(i):
                    item += 1
                    r.lpush("{}_dou_dizhu_user_{}_card".format(ctx.FromGroupId,
                                                               dou_dizhu_user[2]),
                            CARDS[j]["name"]
                            )
                    r.blpop("{}_{}_dou_dizhu_card".format(ctx.FromGroupId, i), timeout=2)
                    r.lpush("{}_dou_dizhu_user_{}_card_val".format(ctx.FromGroupId, dou_dizhu_user[2]), CARDS[j]["val"])
                    del CARDS[j]
        # TODO:抢地主逻辑
        # 先随机整个地主出来
        landholder = random.choice(dou_dizhu_user)
        S.bind(ctx).text("[ATUSER({})]天选之子,没错你就是我随机选出来的地主".format(landholder))
        r.set("{}_dou_dizhu_landholder".format(ctx.FromGroupId), str(landholder))
        im_list = []
        for i in anti_replace(landholder_cards):
            item = 0
            for j in reversed(range(len(CARDS))):
                if item == 0 and str(CARDS[j]['val']) == str(i):
                    item += 1
                    r.blpop("{}_{}_dou_dizhu_card".format(ctx.FromGroupId, i), timeout=2)
                    r.lpush("{}_dou_dizhu_user_{}_card".format(ctx.FromGroupId,
                                                               landholder),
                            CARDS[j]["name"]
                            )
                    im_list.append(Image.open(os.path.dirname(__file__) + "/card/" + str(CARDS[j]["id"]) + ".png"))
                    r.lpush("{}_dou_dizhu_user_{}_card_val".format(ctx.FromGroupId, landholder), CARDS[j]["val"])
                    del CARDS[j]
        # 地主底牌
        width = 0
        height = 0
        for img in im_list:
            w, h = img.size
            width += w
            height = max(height, h)
        result = Image.new(im_list[0].mode, (width, height), 0xffffff)
        width = 0
        for img in im_list:
            w, h = img.size
            result.paste(img, box=(width, round(height / 3 - h / 3)))
            width += w
        size = result.size

        im = Image.open(os.path.dirname(__file__) + "/bg.png")
        im = im.resize((620, 380), Image.ANTIALIAS)
        width, height = im.size
        bg = Image.new('RGB', (width, height), color=(255, 255, 0))
        bg.paste(im, (0, 0))
        draw = ImageDraw.Draw(bg)

        avatar_size = (55, 55)
        mask = Image.new('RGBA', avatar_size, color=(0, 0, 0, 0))
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, avatar_size[0], avatar_size[1]), fill=(0, 0, 0, 255))

        for i in range(len(dou_dizhu_user)):
            avatar = get_avator(int(dou_dizhu_user[i]))
            avatar = avatar.resize(avatar_size, Image.ANTIALIAS)
            if dou_dizhu_user[i] == landholder:
                # 中间部分【中间部分暂时固定为地主
                x, y = int((width - avatar_size[0]) / 12), int((height - avatar_size[1]) / 2)
                box = (x, y, (x + avatar_size[0]), (y + avatar_size[1]))
                bg.paste(avatar, box, mask)
                text = "地主(剩20张)"
                text_coordinate = int((width - font.getsize(text)[0]) / 12), (
                    int((height - font.getsize(text)[1]) / 2 + 55))
                draw.text(text_coordinate, text, "#ffb7da", font=ImageFont.truetype(font_path, 18))
            else:
                if i % 2 == 0:
                    # 上边
                    x, y = int((width - avatar_size[0]) / 12), int((height - avatar_size[1]) / 2 - 108)
                    box = (x, y, (x + avatar_size[0]), (y + avatar_size[1]))
                    bg.paste(avatar, box, mask)
                    text = "农民(剩17张)"
                    text_coordinate = int((width - font.getsize(text)[0]) / 12), (
                        int((height - font.getsize(text)[1]) / 2 - 108 + 55))
                    draw.text(text_coordinate, text, "#ffb7da", font=ImageFont.truetype(font_path, 18))
                else:
                    # 下边
                    x, y = int((width - avatar_size[0]) / 12), int((height - avatar_size[1]) / 2 + 108)
                    box = (x, y, (x + avatar_size[0]), (y + avatar_size[1]))
                    bg.paste(avatar, box, mask)
                    text = "农民(剩17张)"
                    text_coordinate = int((width - font.getsize(text)[0]) / 12), (
                        int((height - font.getsize(text)[1]) / 2 + 108 + 55))
                    draw.text(text_coordinate, text, "#ffb7da", font=ImageFont.truetype(font_path, 18))
        # 底牌或出牌内容区 if 地主 /2 else /3
        x, y = int((width - size[0]) / 2), int((height - size[1]) / 2)
        box = (x, y, (x + size[0]), (y + size[1]))
        bg.paste(result, box, result)
        text = "【地主底牌】"
        text_coordinate = int((width - font.getsize(text)[0]) / 2), (int((height - font.getsize(text)[1]) / 2 - 108))
        draw.text(text_coordinate, text, "#00c37d", font=font)

        buffer = BytesIO()
        bg.save(buffer, format="jpeg")
        S.bind(ctx).image(buffer)
        for i in r.lrange("{}_dou_dizhu_user".format(ctx.FromGroupId), 0, -1):
            # if r.get("{}_dou_dizhu_landholder".format(ctx.FromGroupId)) != i:
            print(i, ctx.FromGroupId, r.lrange("{}_dou_dizhu_user_{}_card".format(ctx.FromGroupId, i), 0, -1))
            privately(i, ctx.FromGroupId, r.lrange("{}_dou_dizhu_user_{}_card".format(ctx.FromGroupId, i), 0, -1))
        S.bind(ctx).text("已向玩家私发牌，若未收到请打开群私聊权限")


def privately(uid, gid, cards):
    im_list = []
    for i in cards:
        for j in ITEM_CARD:
            print(j)
            if i == j['name']:
                im_list.append(Image.open(os.path.dirname(__file__) + "/card/" + str(j["id"]) + ".png"))
    width = 0
    height = 0
    for img in im_list:
        w, h = img.size
        width += int(w / 2.5)
        height = max(height, h)
    result = Image.new(im_list[0].mode, (width, height), 0xffffff)
    width = 0
    for img in im_list:
        w, h = img.size
        result.paste(img, box=(int(width / 2.8), round(height / 3 - h / 3)))
        width += w
    size = result.size
    im = Image.open(os.path.dirname(__file__) + "/bg.png")
    im = im.resize((620, 380))
    width, height = im.size
    bg = Image.new('RGB', (width, height), color=(255, 255, 0))
    bg.paste(im, (0, 0))
    x, y = int((width - size[0]) / 2), int((height - size[1]) / 2)
    box = (x, y, (x + size[0]), (y + size[1]))
    bg.paste(result, box, result)
    bg.save(os.path.dirname(__file__) + "/cache/{}_{}.png".format(gid, uid))
    with open(os.path.dirname(__file__) + "/cache/{}_{}.png".format(gid, uid), 'rb') as f:
        content = f.read()

    Action(jconfig.qq).post("SendMsgV2", {
        "GroupID": int(gid),
        "ToUserUid": int(uid),
        "SendToType": 3,
        "SendMsgType": "PicMsg",
        "PicBase64Buf": base64.b64encode(content).decode()
    })


def replace(lst):
    """此函数是将数字替换成现实中的牌面"""
    while 11 in lst:
        lst[lst.index(11)] = 'J'
    while 12 in lst:
        lst[lst.index(12)] = 'Q'
    while 13 in lst:
        lst[lst.index(13)] = 'K'
    while 14 in lst:
        lst[lst.index(14)] = 'A'
    while 16 in lst:
        lst[lst.index(16)] = 2
    while 19 in lst:
        lst[lst.index(19)] = '小王'
    while 20 in lst:
        lst[lst.index(20)] = '大王'
    return lst


def anti_replace(lst):
    """将牌面还原为数字"""
    while 'J' in lst:
        lst[lst.index('J')] = 11
    while 'Q' in lst:
        lst[lst.index('Q')] = 12
    while 'K' in lst:
        lst[lst.index('K')] = 13
    while 'A' in lst:
        lst[lst.index('A')] = 14
    while 2 in lst:
        lst[lst.index(2)] = 16
    while '小王' in lst:
        lst[lst.index('小王')] = 19
    while '大王' in lst:
        lst[lst.index('大王')] = 20
    return lst


def sort(lst):
    for i in range(1, len(lst)):
        key = lst[i]
        j = i - 1
        while j >= 0 and lst[j] < key:
            lst[j + 1] = lst[j]
            j -= 1
        lst[j + 1] = key
    return lst
