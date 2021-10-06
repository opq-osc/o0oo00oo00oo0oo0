# 移植于https://github.com/devourbots/word_cloud_bot
import base64
import io
import os
import queue
import re
import time
import threading

import imageio
import jieba
import paddle
import schedule
from botoy import Action, FriendMsg, GroupMsg, EventMsg, MsgTypes, logger, jconfig

__name__ = "词云"
__doc__ = "定时向群发送词云,当日话题统计,当日发言统计"

from botoy.decorators import ignore_botself, these_msgtypes
from jieba import posseg
from wordcloud import wordcloud
from botoy.config import jconfig

import connector

# allow word cloud groups
ALLOW_GROUPS = jconfig.word_cloud_white_group_list or []

task_queue = queue.Queue()

def receive_friend_msg(ctx: FriendMsg):
    Action(ctx.CurrentQQ)


@ignore_botself
@these_msgtypes(MsgTypes.TextMsg)
def receive_group_msg(ctx: GroupMsg):

    # only allow config groups use word cloud
    chat_id = ctx.FromGroupId
    global ALLOW_GROUPS
    if chat_id not in ALLOW_GROUPS:
        return

    try:
        r = connector.get_connection()
        text = ctx.Content
        user_id = ctx.FromUserId

        username = ctx.FromNickName
        logger.info(f"内容{text[:10]} QQ: {str(user_id)} 昵称: {str(username)} 群号码: {str(chat_id)}")
        if "/" in text:
            logger.info("这是一条指令信息，跳过")
            return
        else:
            if text[-1] not in ["，", "。", "！", "：", "？", "!", "?", ",", ":", "."]:
                r.append("{}_chat_content".format(chat_id), text + "。")
            else:
                r.append("{}_chat_content".format(chat_id), text)
            r.incrby("{}_total_message_amount".format(chat_id))
            r.hincrby("{}_user_message_amount".format(chat_id), username)
        if ctx.Content == "今日话题":
            generate(ctx.FromGroupId)
    except Exception as e:
        logger.error(f"用户数据提取、入库错误 {e}")


def receive_events(ctx: EventMsg):
    Action(ctx.CurrentQQ)


def schedule_task():
    try:
        r = connector.get_connection()
        key_list = r.keys()
        group_list = []
        for i in key_list:
            if "chat_content" in i:
                group_list.append(i[:i.find("_")])
        logger.info("运行定时任务，向任务队列中添加任务，任务数量：{}".format(len(group_list)))
        for group in group_list:
            try:
                task_queue.put(group)
            except Exception as e:
                logger.info("群：{} | 词云数据分析生成失败，请查看报错信息".format(group))
                logger.error(e)
                continue
    except Exception as e:
        logger.error("数据库连接失败，请查看报错信息")
        logger.error(e)


def do_task():
    while True:
        group = task_queue.get()
        if not group:
            return
        try:
            logger.info("群: {} | 分析处理中... | 剩余任务数量 {}".format(group, task_queue.qsize()))
            start_time = float(time.time())
            generate(group)
            stop_time = float(time.time())
            logger.info("当前群处理耗时：" + str(stop_time - start_time))
        except Exception as e:
            logger.error("群: {} | 处理失败，可能是机器人已经被移出群，请检查报错！".format(group))
            logger.error(e)
        time.sleep(1)


def add_task(group):
    task_queue.put(group)


def generate(group):
    mk = imageio.imread(os.path.abspath(os.path.dirname(__file__)) + "/img/circle.png")
    w = wordcloud.WordCloud(width=800,
                            height=800,
                            background_color='white',
                            font_path=os.path.abspath(os.path.dirname(__file__)) + '/font/font.ttf',
                            mask=mk,
                            scale=5)
    r = connector.get_connection()
    logger.info("当前处理的群：" + str(group))
    paddle.enable_static()
    jieba.enable_paddle()
    chat_content = r.get("{}_chat_content".format(group))
    if chat_content is None:
        logger.error("数据库中不存在此群数据")
        return
    word_list = []
    words = posseg.cut(chat_content, use_paddle=True)
    for word, flag in words:
        if flag in ["n", "nr", "nz", "PER", "f", "ns", "LOC", "s", "nt", "ORG", "nw"]:
            if re.match(r"^\s+?$", word) is None and len(word) > 1:
                word_list.append(word)
    total_message_amount = r.get("{}_total_message_amount".format(group))
    user_amount = len(r.hkeys("{}_user_message_amount".format(group)))
    user_message_amount = r.hgetall("{}_user_message_amount".format(group))
    user_message_amount = sorted(user_message_amount.items(), key=lambda kv: (int(kv[1])), reverse=True)
    if len(word_list) > 0:
        word_amount = {}
        for word in word_list:
            if re.search(
                    r"[。|，|、|？|！|,|.|!|?|\\|/|+|\-|`|~|·|@|#|￥|$|%|^|&|*|(|)|;|；|‘|’|“|”|'|_|=|•|·|…|\"]",
                    word) is not None:
                continue
            if word_amount.get(word) is not None:
                word_amount[word] = word_amount.get(word) + 1
            else:
                word_amount[word] = 1
        word_amount = sorted(word_amount.items(), key=lambda kv: (int(kv[1])), reverse=True)
        if len(word_amount) > 0:
            hot_word_string = ""
            for i in range(min(5, len(word_amount))):
                hot_word_string += "\t" + "" + str(word_amount[i][0]) + "" + ": " + str(
                    word_amount[i][1]) + "\n"
            Action(jconfig.qq).sendGroupText(int(group), "🎤 今日话题榜 🎤\n"
                                                         "📅 {}\n"
                                                         "⏱ 截至今天{}\n"
                                                         "🗣️ 本群{}位朋友共产生{}条发言\n"
                                                         "🤹‍ 大家今天讨论最多的是：\n\n"
                                                         "{}\n"
                                                         "看下有没有你感兴趣的话题? 👏".format(
                time.strftime("%Y年%m月%d日", time.localtime()),
                time.strftime("%H:%M", time.localtime()),
                user_amount,
                total_message_amount,
                hot_word_string))

    else:
        logger.info("当前聊天数据量过小，嗨起来吧~")

    if len(user_message_amount) > 0:
        top_5_user = ""
        # 默认展示前5位，少于5个则全部展示
        for i in range(min(5, len(user_message_amount))):
            dis_name = str(user_message_amount[i][0])
            top_5_user += "\t" + "🎖" + dis_name[:min(8, len(dis_name))] + "" + " 贡献: " + str(
                user_message_amount[i][1]) + "\n"
        Action(jconfig.qq).sendGroupText(int(group), "🏵 今日活跃用户排行榜 🏵\n"
                                                     "📅 {}\n"
                                                     "⏱ 截至今天{}\n\n"
                                                     "{}\n"
                                                     "感谢这些朋友今天的分享! 👏 \n"
                                                     "遇到问题,向他们请教说不定有惊喜😃".format(
            time.strftime("%Y年%m月%d日", time.localtime()),
            time.strftime("%H:%M", time.localtime()),
            top_5_user))
    else:
        logger.info("当前聊天数据量过小，嗨起来吧~")

    try:
        string = " ".join(word_list)
        w.generate(string)
        buffer = io.BytesIO()
        img = w.to_image()
        img.save(buffer, format='JPEG')
        Action(jconfig.qq).sendGroupPic(group=int(group), picBase64Buf=base64.b64encode(buffer.getvalue()).decode())
    except Exception as e:
        logger.error("词云图片生成失败", e)


def flush_redis():
    r = connector.get_connection()
    r.flushall()
    logger.info("已清空数据库")


def check_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


schedule.every().day.at('11:00').do(schedule_task)
schedule.every().day.at('18:00').do(schedule_task)
schedule.every().day.at('23:30').do(schedule_task)
schedule.every().day.at('23:59').do(flush_redis)

threading.Thread(target=do_task).start()
threading.Thread(target=check_schedule).start()
