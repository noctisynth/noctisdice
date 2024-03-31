from pathlib import Path
from nonebot.plugin import on_message, on_startswith
from nonebot.rule import Rule
from nonebot.adapters import Event, Bot
from nonebot.matcher import Matcher
from nonebot.log import logger
from infini.input import Input
from infini.injector import Injector
from diceutils.utils import format_msg
from diceutils.parser import CommandParser, Commands, Optional, Bool
from git import Repo
from ipm import api

from .utils import get_packages, hmr, get_core
from .workflow import put, workflows

import json
import shutil


class Interceptor:
    __slots__ = ("msg", "ignorecase")

    def __init__(self, msg: str = "", ignorecase: bool = False):
        self.msg = msg
        self.ignorecase = ignorecase

    def __repr__(self) -> str:
        return f"Interceptor(msg={self.msg}, ignorecase={self.ignorecase})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Interceptor)
            and frozenset(self.msg) == frozenset(other.msg)
            and self.ignorecase == other.ignorecase
        )

    def __hash__(self) -> int:
        return hash((frozenset(self.msg), self.ignorecase))

    async def __call__(self) -> bool:
        return True


injector = Injector()
interceptor = on_message(Rule(Interceptor()), priority=1, block=True)
ipm_command = on_startswith((".ipm", "。ipm", "/ipm"), priority=0, block=True)

hmr()


@ipm_command.handle()
async def ipm_handler(event: Event, matcher: Matcher):
    args = format_msg(event.get_plaintext(), begin=".ipm")
    commands = CommandParser(
        Commands(
            [
                Bool("hmr"),
                Optional(("add", "require"), str),
                Optional(("remove", "rm", "unrequire"), str),
                Bool("clear"),
                Bool("show"),
                Optional("adapter", str),
                Bool("sync"),
                Bool("install"),
            ]
        ),
        args=args,
        auto=True,
    ).results

    packages = get_packages()

    if commands["hmr"]:
        hmr()
        return await matcher.send("Infini 热重载完毕！")

    if commands["add"]:
        if commands["add"] in packages:
            return await matcher.send(
                f"规则包[{commands['add']}]已经被挂载，如果你需要重新挂载规则包，请使用[.ipm hmr]进行重新挂载。"
            )

        try:
            api.require(Path.cwd(), commands["add"], echo=True)  # type: ignore
            hmr()
        except Exception as e:
            return await matcher.send(f"适配器错误: 挂载规则包时出现错误: {e}")
        return await matcher.send(f"规则包[{commands['add']}]挂载完成")

    if commands["clear"]:
        for package in packages:
            try:
                api.unrequire(Path.cwd(), package, echo=True)
                hmr()
            except Exception as e:
                return await matcher.send(f"适配器错误: 卸载规则包时出现异常: {e}")

        return await matcher.send(f"挂载规则包已清空")

    if commands["show"]:
        return await matcher.send(f"挂载规则包: {[package for package in packages]!r}")

    if commands["remove"]:
        if commands["remove"] in packages:
            try:
                api.unrequire(Path.cwd(), commands["remove"], echo=True)
                hmr()
            except Exception as e:
                return await matcher.send(f"适配器错误: 卸载规则包时出现异常: {e}")

            return await matcher.send(f"规则包[{commands['remove']}]卸载完成")
        return await matcher.send(f"规则包[{commands['remove']}]未挂载")

    if commands["adapter"]:
        if commands["adapter"] == "update":
            if not shutil.which("git"):
                return await matcher.send("未检测到 Git 安装，指令忽略。")
            else:
                try:
                    repo = Repo(str(Path.cwd()))
                    repo.remote().pull()
                except Exception as e:
                    return await matcher.send(
                        f"适配器错误: 拉取适配器更改时出现异常: {e}"
                    )

            return await matcher.send("适配器更新成功！")

    if commands["sync"]:
        try:
            api.sync(Path.cwd())
        except Exception as e:
            return await matcher.send(f"适配器错误: 同步规则包时出现异常: {e}")
        return await matcher.send("规则包同步完成！")

    if commands["install"]:
        try:
            api.install(Path.cwd(), echo=True)
        except Exception as e:
            return await matcher.send(f"适配器错误: 安装规则包时出现异常: {e}")
        return await matcher.send("规则包安装完成！")

    await matcher.send(
        "Infini Package Manager 版本 1.0.0-beta.3 [IPM for Infini v2.0.6]\n"
        "欢迎使用 IPM, 使用`.help ipm`查看 IPM 使用帮助."
    )


@interceptor.handle()
async def handler(bot: Bot, event: Event, matcher: Matcher):
    nb_event_name = event.get_event_name()
    nb_event_type = event.get_type()
    nb_event_description = event.get_event_description()
    nb_event_json: dict = json.loads(event.json())

    nickname = (nb_event_json.get("user", {})).get("nickname") or (
        nb_event_json.get("sender", {})
    ).get("nickname")
    user_id = str(event.get_user_id())
    self_id = str(nb_event_json.get("self_id"))
    group_id = str(getattr(event, "group_id")) if hasattr(event, "group_id") else None
    session_id = event.get_session_id()

    plain_text = event.get_plaintext()
    message = [{"type": msg.type, "data": msg.data} for msg in event.get_message()]
    if "original_message" in nb_event_json:
        mentions = [
            mention["data"]["qq"]
            for mention in nb_event_json["original_message"]
            if mention["type"] == "at"
        ]
    elif "message" in nb_event_json:
        mentions = [
            mention["data"]["qq"]
            for mention in nb_event_json["message"]
            if mention["type"] == "at"
        ]
    else:
        mentions = [self_id]

    is_tome = False
    if self_id in mentions:
        is_tome = True
    elif not mentions:
        is_tome = True
    else:
        if mentions:
            if nb_event_json["original_message"][0]["type"] != "at":
                is_tome = True

    input = Input(
        plain_text,
        variables={
            "nickname": nickname,
            "user_id": user_id,
            "self_id": self_id,
            "group_id": group_id,
            "session_id": session_id,
            "message": message,
            "mentions": mentions,
            "is_tome": is_tome,
            "nb_event_name": nb_event_name,
            "nb_event_type": nb_event_type,
            "nb_event_description": nb_event_description,
            "nb_event_json": nb_event_json,
            "platform": "Nonebot2",
        },
    )

    for output in get_core().input(input):
        if isinstance(output, str):
            logger.info(f"发送消息: {output}")
            await matcher.send(output)
        else:
            parameters = {"output": output, "bot": bot, "matcher": matcher}
            parameters.update(output.variables)
            if workflow := workflows.get(output.name):
                put(injector.inject(workflow, parameters=parameters))
            else:
                await matcher.send(f"适配器错误: 工作流[{output.name}]不存在！")
