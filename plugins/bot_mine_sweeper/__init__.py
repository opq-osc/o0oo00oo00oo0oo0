# 移植于https://github.com/mzdluo123/MineSweeper
from io import BytesIO
from time import time
from typing import Dict

from botoy import GroupMsg, Text, S
from botoy.decorators import ignore_botself

from plugins.bot_mine_sweeper.minesweeper import MineSweeper, GameState

HELP = """
欢迎游玩扫雷小游戏
输入 【m 开始】 即可开始游戏
输入 【m 中级或高级】 即可开始不同难度游戏
输入 【m 自定义 长 宽 雷数】 即可开始自定义游戏
使用 【m d 位置1 位置2】 来挖开多个方快
使用 【m t 位置1 位置2】 来标记多个方块
使用 【m show】 来重新查看游戏盘
使用 【m help】 来查看帮助
使用 【m exit】 退出游戏
"""

in_gaming_list: Dict[int, MineSweeper] = {}


@ignore_botself
def receive_group_msg(ctx: GroupMsg):
    plain = ctx.Content
    if plain == "扫雷":
        Text(HELP)
    if len(plain) > 2 and plain[:1] == "m":
        commands = plain.split(" ")
        if commands[1] == "开始":
            new_game(ctx, 10, 10, 10)
        if commands[1] == "中级":
            new_game(ctx, 16, 16, 40)
        if commands[1] == "高级":
            new_game(ctx, 20, 20, 90)
        if commands[1] == "自定义" and len(commands) == 5:
            try:
                new_game(ctx, int(commands[2]), int(commands[3]), int(commands[4]))
            except ValueError as e:
                Text(f"错误 {e}")
        if commands[1] == "help":
            Text(HELP)
            # 以下命令只有在游戏中才可以使用
        if ctx.FromUserId not in in_gaming_list:
            return
        if commands[1] == "show":
            send_panel(ctx)

        if commands[1] == "exit":
            if ctx.FromUserId in in_gaming_list:
                Text("退出成功")
                del in_gaming_list[ctx.FromUserId]
            else:
                Text("请输入 m 开始 开始游戏")
        # 命令长度大于3才可以使用
        if len(commands) < 3:
            return
        if commands[1] == "d":
            try:
                for i in range(2, len(commands)):
                    print(i, len(commands), commands[i])
                    location = MineSweeper.parse_input(commands[i])
                    print(location)
                    in_gaming_list[ctx.FromUserId].mine(location[0], location[1])
                    if in_gaming_list[ctx.FromUserId].state != GameState.GAMING:
                        break
            except ValueError as e:
                Text(f"错误: {e}")
            send_panel(ctx)
            if in_gaming_list[ctx.FromUserId].state != GameState.GAMING:
                send_game_over(ctx)

        if commands[1] == "t":
            try:
                for i in range(2, len(commands)):
                    location = MineSweeper.parse_input(commands[i])
                    in_gaming_list[ctx.FromUserId].tag(location[0], location[1])
                    send_panel(ctx)
            except ValueError as e:
                Text(f"错误: {e}")


def new_game(app: GroupMsg, row: int, column: int, mines: int):
    if app.FromUserId in in_gaming_list:
        S.bind(app).text("你已经在游戏中了")
        return
    in_gaming_list[app.FromUserId] = MineSweeper(row=row, column=column, mines=mines)
    send_panel(app)


def send_panel(app: GroupMsg):
    byte_io = BytesIO()
    in_gaming_list[app.FromUserId].draw_panel().save(byte_io, format="jpeg")
    byte_io.flush()
    S.bind(app).image(byte_io)
    byte_io.close()


def send_game_over(app: GroupMsg):
    minesweeper = in_gaming_list[app.FromUserId]
    if minesweeper.state == GameState.WIN:
        S.bind(app).text(f"恭喜你赢了，再来一次吧！耗时{time() - minesweeper.start_time}秒 操作了{minesweeper.actions}次")
    if minesweeper.state == GameState.FAIL:
        S.bind(app).text(f"太可惜了，就差一点点，再来一次吧！耗时{time() - minesweeper.start_time}秒 操作了{minesweeper.actions}次")
    del in_gaming_list[app.FromUserId]
