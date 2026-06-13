from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from . import db_manager
import json
import random


@tool
def push_plot(session_id: int, direction: str) -> str:
    """推进剧情发展。输入要推进的剧情方向（如：探索、对话、战斗、逃离）。返回新的剧情描述。"""
    scene = db_manager.get_session(session_id)
    if not scene:
        return "错误：未找到游戏会话，请重新开始。"

    chapter = scene.get("current_chapter", 1)
    flags = scene.get("flags", {})
    inventory = scene.get("inventory", [])

    plot_templates = {
        "探索": [
            "你小心翼翼地向前推进，穿过一片幽暗的森林。树影婆娑间，你发现了一处隐藏的洞穴入口。洞口散发着微弱的蓝光...",
            "沿着蜿蜒的小路前行，你来到了一座废弃的古堡前。巨大的铁门半掩着，里面传来低沉的回声...",
            "你在一片迷雾中前行，突然脚下踩到了什么硬物。低头一看，是一枚古老的徽章，上面刻着神秘的符文...",
            "穿过一条狭窄的峡谷后，你眼前豁然开朗——一座繁华的小镇出现在眼前，街道上行人来来往往...",
        ],
        "对话": [
            "一位身穿灰色长袍的老者缓步走来，他的眼神深邃而智慧。「年轻人，你看起来不像是本地人。你从哪里来？」",
            "酒馆的吧台后面，一位红发女子正在擦拭酒杯。她抬头看了你一眼：「需要来点什么？还是说...你在找什么人？」",
            "城墙上的守卫叫住了你：「站住！报上你的身份和来意。最近这片区域不太平，我们对陌生人格外警惕。」",
        ],
        "战斗": [
            "一只浑身漆黑的狼人从暗处扑出！它的双眼泛着血红色的光芒，锋利的爪子在月光下闪着寒光。战斗开始！",
            "前方的路上出现了一群哥布林，它们手持简陋的武器，发出刺耳的笑声。「嘿！又来一个送死的！」",
            "一只巨大的石像鬼挡住了去路，它缓缓睁开石质的眼睛，身上的石块开始剥落，露出了里面的暗红色光芒...",
        ],
        "逃离": [
            "你转身飞奔，身后的追赶声越来越近。穿过几条小巷后，你终于甩掉了追踪者，躲进了一间废弃的木屋中喘息。",
            "你纵身跳入河中，冰冷的河水浸透了衣物。你奋力游向对岸，终于在精疲力竭前爬上了岸。",
        ],
    }

    directions = list(plot_templates.keys())
    direction_key = direction if direction in plot_templates else random.choice(directions)

    new_scene = random.choice(plot_templates[direction_key])
    new_hp = scene.get("hp", 100)

    if direction_key == "战斗":
        damage = random.randint(5, 20)
        new_hp = max(0, new_hp - damage)
        new_scene += f"\n\n[你受到了 {damage} 点伤害！当前生命值: {new_hp}]"

    if random.random() < 0.3:
        clues_pool = [
            "古老的文献提到，这片大陆曾经被一位强大的暗影巫师统治。",
            "镇上的居民似乎在隐瞒着什么，每到夜晚都会紧闭门窗。",
            "有人传言，在北方的雪山中藏着一把传说中的圣剑。",
            "酒馆中的吟游诗人唱到：「当五星连珠之时，封印将被打破...」",
            "你在一本破旧的日记中发现了一段密文：「真相就在钟楼之下。」",
        ]
        clue = random.choice(clues_pool)
        db_manager.save_clue(session_id, "剧情线索", clue)
        new_scene += f"\n\n[你获得了一条线索！]"

    db_manager.update_session(
        session_id,
        current_chapter=chapter + 1,
        current_scene=direction_key,
        hp=new_hp,
    )

    return new_scene


@tool
def get_clues(session_id: int) -> str:
    """获取当前已收集的所有线索。返回所有已发现的剧情线索和世界观信息。"""
    clues = db_manager.get_clues(session_id)
    if not clues:
        return "你还没有收集到任何线索。继续探索吧！"

    result = "=== 已收集的线索 ===\n"
    for i, c in enumerate(clues, 1):
        result += f"{i}. [{c['clue_type']}] {c['clue_content']}\n"
    return result


@tool
def battle(session_id: int, enemy_name: str = "怪物") -> str:
    """与敌人进行战斗。输入敌人名称，返回战斗结果。"""
    scene = db_manager.get_session(session_id)
    if not scene:
        return "错误：未找到游戏会话。"

    player_hp = scene.get("hp", 100)
    player_atk = scene.get("attack", 15)
    player_def = scene.get("defense", 10)

    enemy_hp = random.randint(30, 80)
    enemy_atk = random.randint(8, 25)
    enemy_def = random.randint(3, 12)

    battle_log = f"=== 战斗开始: 你 vs {enemy_name} ===\n"
    battle_log += f"你的状态: HP={player_hp}, ATK={player_atk}, DEF={player_def}\n"
    battle_log += f"敌人状态: HP={enemy_hp}, ATK={enemy_atk}, DEF={enemy_def}\n\n"

    round_num = 0
    while player_hp > 0 and enemy_hp > 0 and round_num < 10:
        round_num += 1
        p_dmg = max(1, player_atk - enemy_def + random.randint(-3, 3))
        enemy_hp -= p_dmg
        battle_log += f"第{round_num}回合: 你对{enemy_name}造成 {p_dmg} 点伤害！"

        if enemy_hp <= 0:
            battle_log += f" → {enemy_name}被击败！\n"
            break

        e_dmg = max(1, enemy_atk - player_def + random.randint(-3, 3))
        player_hp -= e_dmg
        battle_log += f" {enemy_name}对你造成 {e_dmg} 点伤害！\n"

    if player_hp <= 0:
        battle_log += "\n你被击败了...但你凭借顽强的意志勉强站了起来。"
        player_hp = 10
    elif enemy_hp <= 0:
        exp = random.randint(10, 30)
        battle_log += f"\n战斗胜利！你获得了 {exp} 点经验值。"
        if random.random() < 0.4:
            items = ["回复药水", "神秘卷轴", "古老钥匙", "暗影宝石"]
            item = random.choice(items)
            inventory = scene.get("inventory", [])
            inventory.append(item)
            db_manager.update_session(session_id, inventory=inventory)
            battle_log += f"\n你从敌人身上搜到了: {item}"
    else:
        battle_log += "\n战斗陷入僵局，双方暂时停手。"

    db_manager.update_session(session_id, hp=max(10, player_hp))
    return battle_log


@tool
def check_status(session_id: int) -> str:
    """查看角色当前状态，包括生命值、攻击力、防御力、物品栏等信息。"""
    scene = db_manager.get_session(session_id)
    if not scene:
        return "错误：未找到游戏会话。"

    inventory = scene.get("inventory", [])
    inv_str = "、".join(inventory) if inventory else "空"

    return (
        f"=== 角色状态 ===\n"
        f"生命值: {scene.get('hp', 100)}/100\n"
        f"攻击力: {scene.get('attack', 15)}\n"
        f"防御力: {scene.get('defense', 10)}\n"
        f"当前章节: 第{scene.get('current_chapter', 1)}章\n"
        f"物品栏: {inv_str}"
    )


@tool
def rest(session_id: int) -> str:
    """原地休息恢复生命值。"""
    scene = db_manager.get_session(session_id)
    if not scene:
        return "错误：未找到游戏会话。"

    current_hp = scene.get("hp", 100)
    heal = random.randint(10, 25)
    new_hp = min(100, current_hp + heal)
    db_manager.update_session(session_id, hp=new_hp)
    return f"你找了一处安全的地方休息了一会儿，恢复了 {heal} 点生命值。当前HP: {new_hp}/100"


@tool
def save_game(session_id: int, save_name: str = "手动存档") -> str:
    """保存当前游戏进度。输入存档名称，返回保存结果。"""
    result = db_manager.save_game_snapshot(session_id, save_name)
    if result:
        return f"游戏进度已保存为「{save_name}」！你可以随时通过存档系统加载这个进度。"
    return "存档失败，请稍后再试。"


ALL_TOOLS = [push_plot, get_clues, battle, check_status, rest, save_game]
