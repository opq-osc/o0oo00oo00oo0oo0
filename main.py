import threading

import schedule
from botoy import Botoy

from plugins.bot_word_cloud import schedule_task, do_task, check_schedule, flush_redis

bot = Botoy(use_plugins=True)

schedule.every().day.at('11:00').do(schedule_task)
schedule.every().day.at('18:00').do(schedule_task)
schedule.every().day.at('23:30').do(schedule_task)
schedule.every().day.at('23:59').do(flush_redis)
# schedule.every(1).minutes.do(schedule_task)
threading.Thread(target=do_task).start()
threading.Thread(target=check_schedule).start()

if __name__ == "__main__":
    bot.run()
