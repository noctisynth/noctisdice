# Initialized `handlers.py` generated by ipm.
# Regists your handlers here.
# Documents at https://ipm.hydroroll.team/

from infini.register import Register
from infini.router import Command
from infini.input import Input
from infini.logging import logger

from diceutils.utils import format_msg, get_user_id, get_group_id, format_str
from diceutils.parser import Positional, CommandParser, Commands, Bool, Optional
from diceutils.charactors import manager
from diceutils.cards import CardsPool, Cards
from diceutils.status import StatusPool


register = Register()
status = StatusPool.register("dicergirl")


@register.handler(Command("bot"), priority=0, description="机器人核心指令")
def bot_handler(input: Input):
    args = format_msg(input.get_plain_text(), begin=".bot", zh_en=True)
    commands = CommandParser(
        Commands(
            [
                Bool(("version", "v", "bot", "版本")),
                Bool(("exit", "bye", "leave", "离开")),
                Bool(("on", "run", "start", "启动")),
                Bool(("off", "down", "shutdown", "关闭")),
                Optional(("name", "命名"), str),
                Bool(("status", "状态")),
                Bool(("mode", "list", "已安装")),
                Positional("first", str),
            ]
        ),
        args=args,
        auto=True,
    )

    if commands.nothing or commands.results["version"]:
        yield input.output("text", "dg.bot", block=True)
    else:
        commands = commands.results

    if commands["exit"]:
        logger.info(f"退出群聊: {input.variables.get('group_id')}")
        workflow = input.output("workflow", "echo.bot.exit", block=True)
        yield workflow
        if workflow.status != 0:
            yield input.output("text", "dg.bot.exit.unsupported", block=True)
        else:
            yield input.output("text", "dg.bot.exit", block=True)

    if commands["name"]:
        status.set("bot", "name", commands["name"])
        yield input.output(
            "text", "dg.bot.name", block=True, variables={"name": commands["name"]}
        )

    if commands["on"]:
        status.set(get_group_id(input), "command", True)
        yield input.output("text", "dg.bot.on", block=True)

    if commands["off"]:
        status.set(get_group_id(input), "command", False)
        yield input.output("text", "dg.bot.off", block=True)

    if commands["status"]:
        yield input.output(
            "text",
            "dg.bot.status",
            block=True,
            variables={"status": status.get(get_group_id(input), "command")},
        )


@register.handler(Command("show", ["display"]), priority=2)
def show_handler(input: Input):
    mode = status.get(get_group_id(input), "mode") or "coc"
    args = format_msg(input.get_plain_text(), begin=(".show", ".display"))
    attr = args[0] if args else ""

    user_id = get_user_id(input)
    cards = CardsPool.get(mode)
    character = manager.build_card(mode)

    if card_data := cards.get(user_id):
        character.loads(card_data)

        if not attr:
            meta = character.display_group("meta")
            basic = character.display_group("basic")
            cards = [{"meta": meta, "basic": basic}]
            yield input.output(
                "text", "dg.show", block=True, variables={"cards": cards}
            )
        else:
            if character.has_group(attr):
                cards = [{"basic": character.display_group(attr)}]
                yield input.output(
                    "text", "dg.show", block=True, variables={"cards": cards}
                )
            else:
                if (value := character.get(attr)) is not None:
                    attrs = [
                        {
                            "name": character.template.get_display_name(attr) or attr,
                            "value": value,
                        }
                    ]
                    yield input.output(
                        "text", "dg.show.attr", block=True, variables={"attrs": attrs}
                    )
                else:
                    yield input.output("text", "dg.show.not_found", block=True)
    else:
        yield input.output("text", "dg.show.not_found", block=True)


@register.handler(Command("pc"), priority=3)
def pc_handler(input: Input):
    mode = status.get(get_group_id(input), "mode") or "coc"
    args = format_msg(input.get_plain_text(), begin=(".pc"))

    commands = CommandParser(
        Commands(
            [
                Bool("new"),
                Optional(("select", "use", "set", "tag"), str),
                Bool("show"),
                Bool("list"),
                Bool("clear"),
                Bool("cache"),
                Optional(("remove", "rm", "delete", "del"), int),
                Positional("index", str, "-1"),
            ]
        ),
        args,
        auto=True,
    ).results

    user_id = input.get_user_id()
    session_id = input.get_session_id()
    cards = CardsPool.get(mode)
    cache_cards: Cards = CardsPool._cache_cards_pool.get(mode)

    if commands["new"]:
        cards.new(user_id, attributes={})
        cards.select(user_id, cards.count(user_id) - 1)
        yield input.output(
            "text",
            "dg.pc.new",
            block=True,
            variables={"count": cards._get_selected_id(user_id)},
        )

    if commands["select"]:
        cards.select(user_id, int(commands["select"]))
        yield input.output(
            "text",
            "dg.pc.select",
            block=True,
            variables={"sequence": commands["select"]},
        )

    if commands["list"]:
        if commands["cache"]:
            card_datas = []
            for idx, card in enumerate(cache_cards.getall(user_id) or []):
                character = manager.build_card(status.get(session_id, "mode") or "coc")
                character.loads(card)
                card_datas.append({"meta": f"卡名: {character.get('name')}", "sequence": idx})
            yield input.output(
                "text", "dg.pc.list.cache", block=True, variables={"cards": card_datas, "selected_id": cards.get_selected_id(user_id)}
            )
        else:
            card_datas = []
            for idx, card in enumerate(cards.getall(user_id) or []):
                character = manager.build_card(status.get(session_id, "mode") or "coc")
                character.loads(card)
                card_datas.append({"meta": f"卡名: {character.get('name')}", "sequence": idx})
            yield input.output(
                "text", "dg.pc.list", block=True, variables={"cards": card_datas, "selected_id": cards.get_selected_id(user_id)}
            )

    if commands["show"]:
        idx: int = int(commands["index"])
        cards = cache_cards if commands["cache"] else cards
        if idx > cards.count(user_id) - 1:
            yield input.output(
                "text",
                "dg.pc.show.overstep",
                block=True,
                variables={"sequence": idx},
            )

        card_datas = []
        card_list = (
            cards.getall(user_id) if idx == -1 else [cards.get(user_id, idx) or {}]
        ) or []
        for card in card_list:
            charactor = manager.build_card(status.get(session_id, "mode") or "coc")
            charactor.loads(card)
            card_datas.append(
                {
                    "sequence": card_list.index(card) if idx == -1 else idx,
                    "meta": charactor.display_group("meta") or "未录入元数据",
                    "basic": charactor.display_group("basic") or "未录入基础数据",
                }
            )

        yield input.output(
            "text",
            "dg.pc.show.cache" if commands["cache"] else "dg.pc.show",
            block=True,
            variables={
                "cards": card_datas,
            },
        )

    if commands["clear"]:
        if commands["cache"]:
            count = cache_cards.count(user_id)
            cache_cards.clear(user_id)
        else:
            count = cards.count(user_id)
            cards.clear(user_id)
        yield input.output(
            "text", "dg.pc.clear", block=True, variables={"count": count}
        )
    
    if commands["remove"] is not None:
        count = cards.delete(user_id, commands["remove"])
        yield input.output(
            "text", "dg.pc.remove", block=True, variables={"sequence": commands["remove"]}
        )

    yield input.output(
        "text", "dg.pc", block=True, variables={"count": cards.count(user_id)}
    )


@register.handler(Command("set", ["st", "s"]), priority=4)
def set_handler(input: Input):
    mode = status.get(get_group_id(input), "mode") or "coc"
    sliced = format_str(input.get_plain_text(), begin=(".set", ".st", ".s")).rpartition(
        "-"
    )
    name = sliced[0]
    args = format_msg(sliced[-1].replace(":", " "), zh_en=False)

    commands = CommandParser(
        Commands(
            [
                Bool("show"),
                Bool("del"),
                Bool("clear"),
                Bool("init"),
                Optional(("mode", "temp"), str),
                Optional(("name", "n"), str),
                Positional("attr", str),
            ]
        ),
        args,
        auto=True,
    ).results

    user_id = get_user_id(input)
    cards = CardsPool.get(mode)
    cache_cards: Cards = CardsPool._cache_cards_pool.get(mode)
    charactor = manager.build_card(mode)

    if commands["show"]:
        idx = input.plain_data.index("show")
        input.plain_data = input.plain_data[idx + 4 :]
        yield next(show_handler(input))

    if commands["name"]:
        charactor.loads(cards.get(user_id))
        charactor.set("name", commands["name"])
        cards.update(user_id, attributes=charactor.dumps())
        yield input.output(
            "text", "dg.st.name", block=True, variables={"name": commands["name"]}
        )

    length = len(args)
    if length % 2 != 0:
        yield input.output("text", "dg.st.failed", block=True)

    if length:
        charactor.loads(cards.get(user_id) or {})
        if name:
            charactor.set("name", name)
        for index in range(0, length, 2):
            try:
                charactor.set(args[index], args[index + 1])
            except:
                pass

        cards.update(user_id, attributes=charactor.dumps())
        yield input.output(
            "text", "dg.st", block=True, variables={"count": length // 2}
        )
    else:
        if cache_card_datas := cache_cards.getall(user_id):
            attrs = cache_card_datas[-1]
            charactor.loads(attrs)
            cards.update(user_id, attributes=attrs)
            yield input.output(
                "text",
                "dg.st.card",
                block=True,
                variables={
                    "meta": charactor.display_group("meta"),
                    "basic": charactor.display_group("basic"),
                },
            )
        else:
            yield input.output("text", "dg.st.not_found", block=True)
