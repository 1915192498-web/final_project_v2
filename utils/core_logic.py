import os
import json
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableBranch
from langchain_text_splitters import RecursiveCharacterTextSplitter

HAS_CHROMA = False
try:
    import chromadb
    HAS_CHROMA = True
except Exception:
    pass

from .tools import ALL_TOOLS
from . import db_manager

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma_db")

NOVEL_WORLDS = {
    "暗影纪元": {
        "title": "暗影纪元",
        "system_prompt": (
            "你是一款沉浸式互动小说《暗影纪元》的AI游戏大师（Game Master）。\n"
            "世界观设定：这是一个剑与魔法的世界，黑暗势力正在侵蚀大陆。你是故事的叙述者，需要根据玩家的选择推进剧情。\n\n"
            "角色设定：\n"
            "- 你同时扮演多个NPC角色，每个角色有独特的说话风格和性格\n"
            "- 你是公正的旁白，描述场景、氛围和NPC的反应\n"
            "- 当玩家做出选择时，描述后果并推进剧情\n\n"
            "叙事规则：\n"
            "1. 每次回复要生动、有画面感，使用适当的环境描写和比喻\n"
            "2. NPC对话要自然、有个性，不要机械化回复\n"
            "3. 根据玩家的行动给出多样化的回应，避免重复套路\n"
            "4. 根据玩家的生命值和物品调整难度和奖励\n"
            "5. 适时引导玩家使用工具（查看线索、战斗、休息、存档等）\n"
            "6. 保持剧情连贯性，记住之前发生的重要事件\n"
            "7. 使用Markdown格式，适当使用**加粗**强调重要信息\n\n"
            "重要：\n"
            "- 你是游戏世界的一部分，用第二人称「你」来描述玩家的行动和遭遇\n"
            "- 回复要有情感起伏，不要平淡如水\n"
            "- 适当加入随机事件和意外惊喜，增加趣味性\n"
            "- 每次回复尽量给出2-3个可能的行动选项，引导玩家选择"
        ),
        "starting_clues": [
            "传说在大陆的中心有一座被遗忘的神殿，那里封印着足以毁灭世界的暗影之力。",
            "五大王国曾经联合封印了暗影巫师，但封印正在减弱。",
            "你是一名流浪的佣兵，在旅途中偶然发现了一封神秘的信件。",
        ],
    },
    "仙途": {
        "title": "仙途",
        "system_prompt": (
            "你是一款沉浸式互动小说《仙途》的AI游戏大师（Game Master）。\n"
            "世界观设定：这是一个修仙世界，灵气复苏，妖兽横行，各大宗门争夺资源。你作为旁白和NPC，引导玩家的修仙之旅。\n\n"
            "角色设定：\n"
            "- 扮演各宗门长老、同门弟子、妖兽等角色\n"
            "- 用古风语言风格对话，适当引用诗词\n"
            "- 描述修炼场景、战斗场面时要有仙侠氛围\n\n"
            "叙事规则：\n"
            "1. 描写要有仙侠意境，注意环境氛围渲染\n"
            "2. 战斗场景要有画面感，体现功法特效\n"
            "3. NPC对话要自然，有个性，不要机械化\n"
            "4. 根据玩家的行动给出多样化的回应\n"
            "5. 适时引导玩家探索修炼、战斗、收集线索、存档\n"
            "6. 保持修仙世界观的一致性\n"
            "7. 使用Markdown格式增强可读性\n\n"
            "重要：\n"
            "- 你是修仙世界的一部分，用第二人称「你」来描述玩家的行动和遭遇\n"
            "- 回复要有情感起伏，不要平淡\n"
            "- 适当加入奇遇和机缘，增加修仙世界的趣味性\n"
            "- 每次回复尽量给出2-3个可能的行动选项"
        ),
        "starting_clues": [
            "天地灵气复苏，各宗门纷纷出世争夺灵脉资源。",
            "一本残缺的上古功法被发现，传闻修炼大成可飞升成仙。",
            "你是青云宗的一名外门弟子，因资质平平而备受冷落。",
        ],
    },
}

CHARACTER_PROFILES = {
    "暗影纪元": {
        "神秘老人": "一位白发苍苍的老人，说话高深莫测，喜欢用谜语暗示真相。",
        "酒馆女老板": "性格豪爽的红发女子，消息灵通，但要价不菲。",
        "守卫队长": "严肃的中年人，效忠王国，对陌生人充满戒备。",
        "流浪商人": "圆滑的商人，什么东西都能搞到，但价格公道。",
    },
    "仙途": {
        "青云长老": "仙风道骨的老者，说话文雅，偶尔引用古诗。",
        "同门师姐": "性格活泼的女弟子，热心帮助新人，但有时过于冲动。",
        "神秘散修": "独来独往的修士，实力深不可测，行踪诡秘。",
        "妖兽": "修行千年的灵兽，能化为人形，但保留着兽性的本能。",
    },
}


def get_llm():
    model_name = os.getenv("MODEL_NAME", "qwen-turbo")
    return ChatOpenAI(
        model=model_name,
        temperature=0.8,
        max_tokens=1000,
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv("DASHSCOPE_API_BASE"),
    )


def get_embeddings():
    if not HAS_CHROMA:
        return None
    from langchain_community.embeddings import DashScopeEmbeddings
    return DashScopeEmbeddings(model="text-embedding-v2")


_world_knowledge = {}


def get_vectorstore(novel_title: str):
    if not HAS_CHROMA:
        return None
    from langchain_community.vectorstores import Chroma
    persist_dir = os.path.join(CHROMA_DIR, novel_title)
    os.makedirs(persist_dir, exist_ok=True)
    return Chroma(
        collection_name=f"novel_{hash(novel_title) & 0xFFFFFFFF:08x}",
        embedding_function=get_embeddings(),
        persist_directory=persist_dir,
    )


def init_world_knowledge(novel_title: str):
    world = NOVEL_WORLDS.get(novel_title, NOVEL_WORLDS["暗影纪元"])

    if novel_title in _world_knowledge:
        return _world_knowledge[novel_title]

    docs = [world["system_prompt"]]
    for clue in world.get("starting_clues", []):
        docs.append(clue)
    characters = CHARACTER_PROFILES.get(novel_title, {})
    for name, desc in characters.items():
        docs.append(f"角色「{name}」: {desc}")

    if HAS_CHROMA:
        vs = get_vectorstore(novel_title)
        if vs and vs._collection.count() > 0:
            _world_knowledge[novel_title] = vs
            return vs
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
        splits = text_splitter.create_documents(docs)
        vs.add_documents(splits)
        _world_knowledge[novel_title] = vs
        return vs
    else:
        _world_knowledge[novel_title] = docs
        return docs


def build_rag_retriever(novel_title: str):
    init_world_knowledge(novel_title)

    def retrieve_context(query: str) -> str:
        knowledge = _world_knowledge.get(novel_title, [])
        if isinstance(knowledge, list):
            return "\n".join(knowledge[:5])
        try:
            results = knowledge.similarity_search(query, k=3)
            return "\n".join([doc.page_content for doc in results])
        except Exception:
            return "\n".join([str(d) for d in knowledge[:5]]) if isinstance(knowledge, list) else ""

    return retrieve_context


def build_novel_chain(novel_title: str):
    world = NOVEL_WORLDS.get(novel_title, NOVEL_WORLDS["暗影纪元"])
    llm = get_llm()
    tools = ALL_TOOLS
    llm_with_tools = llm.bind_tools(tools)
    retriever = build_rag_retriever(novel_title)

    system_msg = world["system_prompt"]
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg + "\n\n【世界知识】\n{world_context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])

    def format_history(raw_history: list) -> list:
        formatted = []
        for msg in raw_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "assistant":
                formatted.append(AIMessage(content=content))
            else:
                formatted.append(HumanMessage(content=content))
        return formatted

    def invoke_chain(input_data: dict) -> str:
        session_id = input_data["session_id"]
        user_input = input_data["input"]

        raw_history = db_manager.get_chat_history(session_id, limit=20)
        chat_history = format_history(raw_history)

        world_context = retriever(user_input)

        chain = prompt | llm_with_tools
        result = chain.invoke({
            "world_context": world_context,
            "chat_history": chat_history,
            "input": user_input,
        })

        if hasattr(result, "tool_calls") and result.tool_calls:
            tool_results = []
            for tc in result.tool_calls:
                tool_name = tc["name"]
                tool_args = tc["args"]
                tool_args["session_id"] = session_id
                for t in tools:
                    if t.name == tool_name:
                        tool_result = t.invoke(tool_args)
                        tool_results.append(f"[工具 {tool_name}]: {tool_result}")
                        break

            tool_summary = "\n\n".join(tool_results)
            final_prompt = prompt | llm
            final_result = final_prompt.invoke({
                "world_context": world_context + "\n\n【工具调用结果】\n" + tool_summary,
                "chat_history": chat_history,
                "input": f"玩家的行动是：{user_input}\n\n工具返回了以下结果，请据此继续叙述故事：\n{tool_summary}",
            })
            response_text = final_result.content if hasattr(final_result, "content") else str(final_result)
        else:
            response_text = result.content if hasattr(result, "content") else str(result)

        db_manager.save_chat(session_id, "user", user_input)
        db_manager.save_chat(session_id, "assistant", response_text)

        return response_text

    return invoke_chain


def start_new_game(user_id: str, novel_title: str, char_name: str = "无名", char_class: str = "战士", hp: int = 100, attack: int = 15, defense: int = 10) -> int:
    db_manager.create_user(user_id, user_id)
    session_id = db_manager.create_session(user_id, novel_title, hp=hp, attack=attack, defense=defense)

    init_world_knowledge(novel_title)

    world = NOVEL_WORLDS.get(novel_title, NOVEL_WORLDS["暗影纪元"])
    for clue in world.get("starting_clues", []):
        db_manager.save_clue(session_id, "初始设定", clue)

    db_manager.save_clue(session_id, "角色信息", f"角色名: {char_name}, 职业: {char_class}")

    return session_id
