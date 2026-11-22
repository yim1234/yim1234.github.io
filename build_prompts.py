#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build prompts.json + prompts.html for the liuhen site.

Sources (verbatim, no rewriting):
- chat JSON page 1 (saved tool output) for tonight's 6 prompts
- ~/workspace/pool-gallery-fast/*-prompt.txt for the 11-20/21 batches
- prompt-sources-chat.json: 27 user prompts re-mined verbatim from the
  chat DB (2026-11-07 -> 2026-11-19), keyed by message_id
- zhetian/heroines.md + ludingji/characters.md: 定妆 spec (assistant-written,
  marked as such, never presented as the user's words)
- JOURNAL.md / MEDIA-INDEX.md: journal + past-daily photos (no full prompt
  survives -> pending entries, title + one-line description only)
- video-prompts-part1/2.json (if present): video entries, kind="video"

Photos without a retrievable full prompt are recorded as pending
(title + one-line description only, never invented).

Does not touch MEDIA-INDEX.md, videos.json, extra-album.json,
drive-uploads.json or the liuhen space. Re-run to regenerate.
"""
import html
import json
import os
import re
import subprocess

HOME = os.path.expanduser("~")
SITE = os.path.dirname(os.path.abspath(__file__))
CHAT_JSON = os.path.join(
    HOME, "workspace/agents/82dc5a4f-fdb6-4c8f-87ab-1bf42d89530b/tool-output/"
    "chat.read_messages-call_01a200818b6b76c1ae4fc5841ceb89af.json")
POOL = os.path.join(HOME, "workspace/pool-gallery-fast")
THUMB_DIR = os.path.join(SITE, "img/thumb")
SOURCES_JSON = os.path.join(SITE, "prompt-sources-chat.json")
VIDEO_PARTS = ("video-prompts-part1.json", "video-prompts-part2.json")


def read_sources():
    with open(SOURCES_JSON, encoding="utf-8") as f:
        return json.load(f)


def read_video_parts():
    out = []
    for name in VIDEO_PARTS:
        p = os.path.join(SITE, name)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            out.extend(json.load(f))
    return out


def esc(s):
    return html.escape(s, quote=True)


def read_chat():
    with open(CHAT_JSON, encoding="utf-8") as f:
        d = json.load(f)
    by_ts = {}
    for t in d["turns"]:
        for it in t.get("items", []):
            if it.get("role") == "user":
                by_ts[it["occurred_at_ms"]] = it["content"]
    return by_ts


def slice_from(text, marker):
    i = text.find(marker)
    if i < 0:
        raise ValueError("marker not found: " + marker)
    return text[i:]


def read_txt(name):
    with open(os.path.join(POOL, name), encoding="utf-8") as f:
        return f.read().strip("\n")


def ph(path, link=None, link_note="", date="", note=""):
    return {"path": path, "link": link, "link_note": link_note,
            "date": date, "note": note}


def build_entries(chat, src):
    E = []
    # ---- 2026-11-22 (tonight, from chat, newest first) ----
    # NOTE 2026-11-22 07:58: the two prompts below arrived after the chat
    # JSON snapshot, so they are stored here as literals (verbatim from the
    # user's messages / the exact cleaned prompt run through the pool).
    E.append({
        "date": "2026-11-22", "title": "卧室都市欧美美女·干净版",
        "status": "complete",
        "desc": "奶油真丝开衫敞开＋腰间细绳松系，内搭不透明奶油真丝吊带＋短裤，暖金大波浪长发、细银框眼镜，卧室白床单前。",
        "photos": [
            ph("pool-gallery-fast/img-1795305291.png",
               "https://muse.ai/files/1361961160333207/1846788376356777/p35dt8fyo7dt51c98n6jdq87/img-1795305291.png",
               "至 2026-11-24 07:57 过期", "2026-11-22"),
        ],
        "prompt": """照片级真实的编辑风格都市日常人像摄影，偏松弛自然且带有轻性感氛围，竖构图。主角：二十岁出头的成年女性，典型欧美柔和高级感：五官立体但不过分硬朗，眼窝较深，鼻梁较高挺，颧骨柔和有弧度，下颌线条圆润不尖锐。皮肤极白皙通透，长发，身材高挑纤细带明显胸部曲线。关键词：甜美、时尚、高级感、性感。脸：精致甜美的欧美柔和立体感，椭圆偏心形脸，下颌线条柔和圆润；眼睛中等偏大，眼窝较深，眼神柔和自然；自然淡眉，弧度轻柔；鼻梁较高且挺直，鼻头圆润不尖锐；嘴唇中等偏厚，唇形自然丰润，微微湿润。体型：身材高挑纤细，肩线柔和，锁骨清晰。胸部大而丰满，曲线自然。皮肤白皙通透，腰腹纤细，腹部完全露出，肚脐清晰可见，臀线柔和。发型：暖金色、蜂蜜棕色长发，大波浪自然垂落，发丝有光泽，丰盈蓬松，几缕碎发自然垂落在脸颊与颈部两侧。服装：奶油色、米白色真丝短款开衫，前襟完全敞开，以细绳在腰间松松系住，下摆停在腰部上方；面料轻盈有柔和光泽与真实褶皱。内搭不透明奶油色真丝短款吊带与同色短裤，面料厚实不透，胸部与下身均被完整遮盖。佩戴细银框眼镜。无其他多余配饰。表情：中性偏柔和，眼神自然看向镜头，神态安静放松，带一点日常的慵懒与松弛感。姿势：身体自然站立或微微侧身，重心放在一条腿上，左手轻放在腰侧或髋部，右手自然下垂或轻轻拨动头发，姿态松弛不刻意，强调开衫敞开的胸部与完全露出的腹部线条。场景：豪华现代化卧室或高级酒店房间，背景可见柔软的白色床单与枕头、浅色床头柜，柔和自然光从侧面窗户洒入，整体氛围私密、松弛、干净高级。构图：中近景（腰部以上），平视或轻微低角度，竖构图。光线：柔和的自然室内光线，正面偏侧光，面部、肩部与胸部受光自然通透，皮肤呈现细腻质感。氛围：日常、清新、松弛、带有轻性感的都市私密感。品质：高分辨率，逼真照片风格，皮肤与头发自然质感（可见细腻毛孔与真实光泽），真丝面料光泽与纹理清晰，光影层次真实。手指与姿态自然。背景暗调。避免：文字、标志、边框、水印；过于硬朗或棱角过分分明的五官；过度锐化、塑料感皮肤、畸形手指、多余肢体、不自然的体型比例；粗框眼镜；任何手机、自拍、镜子反射。""",
        "note": "干净版：原版被拒后按主人「改」出的版本，内搭改不透明奶油真丝吊带＋短裤。",
    })
    E.append({
        "date": "2026-11-22", "title": "卧室都市欧美美女原版（被拒）",
        "status": "refused",
        "desc": "原版白蕾丝内衣套装，号池 content_policy_violation 被拒两次。",
        "photos": [],
        "prompt": """【主题】
以成年女性为主角的、照片级真实的编辑风格都市日常人像摄影，偏松弛自然且带有轻性感氛围。

【人物】
人物形象：典型欧美柔和高级感（五官立体但不过分硬朗，眼窝较深，鼻梁较高挺，颧骨柔和有弧度，下颌线条圆润不尖锐）。皮肤极白皙通透，长发，身材高挑纤细带明显胸部曲线。关键词为“甜美+时尚+高级感+性感”。
年龄层：二十岁出头

【脸部特征】
脸的类型：精致甜美的欧美柔和立体感
脸型：椭圆偏心形脸，下颌线条柔和圆润
眼睛大小：中等偏大，眼窝较深，眼神柔和自然
眉毛：自然淡眉，弧度轻柔
鼻子：鼻梁较高且挺直，鼻头圆润不尖锐
嘴唇：中等偏厚，唇形自然丰润，微微湿润
体型：身材高挑纤细，肩线柔和，锁骨清晰。胸部大而丰满，立体感强烈，侧乳轮廓明显。皮肤白皙通透，腰腹纤细，腹部完全露出，肚脐清晰可见，臀线柔和

【发型与发色】
暖金色/蜂蜜棕色长发，大波浪自然垂落，发丝有光泽，丰盈蓬松，几缕碎发自然垂落在脸颊与颈部两侧。

【服装】
仅穿着奶油色/米白色真丝短款开衫（cream silk short robe / silk cardigan），前襟完全敞开，以细绳在腰间松松系住，下摆停在腰部上方；面料轻盈有柔和光泽与真实褶皱。内搭白色蕾丝内衣套装（白色蕾丝bra + 白色蕾丝内裤），胸部轮廓与腹部完全露出。佩戴细银框眼镜。无其他多余配饰。

【表情】
中性偏柔和的表情，眼神自然看向镜头，神态安静放松，带一点日常的慵懒与松弛感。

【姿势】
身体自然站立或微微侧身，重心放在一条腿上，左手轻放在腰侧或髋部，右手自然下垂或轻轻拨动头发，姿态松弛不刻意，强调开衫敞开的胸部与完全露出的腹部线条。

【场景】
豪华现代化卧室（或高级酒店房间），背景可见柔软的白色床单与枕头、浅色床头柜，柔和自然光从侧面窗户洒入，整体氛围私密、松弛、干净高级。

【构图与相机】
构图：中近景（腰部以上）／角度：平视或轻微低角度／纵横比：竖构图

【光线与氛围】
柔和的自然室内光线，正面偏侧光，面部、肩部与胸部受光自然通透，皮肤呈现细腻质感。氛围：日常、清新、松弛、带有轻性感的都市私密感。

【品质】
高分辨率，逼真照片风格，皮肤与头发自然质感（可见细腻毛孔与真实光泽），真丝与蕾丝面料光泽与纹理清晰，光影层次真实。手指与姿态自然。背景暗调。胸部需大而丰满，侧乳轮廓清晰，腹部完全露出，皮肤需白皙通透。

【避免元素】
不添加文字、标志、边框、水印。敏感部位被服装自然遮住。避免过于硬朗或棱角过分分明的五官。避免过度锐化、塑料感皮肤、畸形手指、多余肢体、不自然的体型比例。避免粗框眼镜。避免任何手机、自拍、镜子反射。""",
        "note": "被拒后改干净版（见上）。",
    })
    E.append({
        "date": "2026-11-22", "title": "日系复古胶片·草莓睡衣窗边写真",
        "status": "complete",
        "desc": "奶白草莓棉质吊带＋同纹高腰短裤、浅粉细网纹袜，双丸子头＋樱花粉发圈，窗台下木地板、手举亮黄小方包。",
        "photos": [
            ph("pool-gallery-fast/img-1795304944.png",
               "https://muse.ai/files/1361961160333207/2171338103456649/h6wy4izkgol7scwb0czs2te5/img-1795304944.png",
               "至 2026-11-24 07:52 过期", "2026-11-22"),
        ],
        "prompt": """【主题】
以日系清新复古胶片风，记录一位 20 岁出头年轻女性在窗台边的日常瞬间。

【人物】
20 岁出头年轻女性，身材纤细匀称，肤色白皙透亮。脸型为温柔的椭圆形，面部线条柔和，眼睛大而圆，棕色瞳孔，眼神清澈温柔，卧蚕自然。鼻子小巧挺直，嘴唇自然粉嫩带微微光泽，脸颊有淡淡自然的腮红，表情安静好奇，神态放松。整体氛围清新、干净、青春。

【发型与发色】
黑色头发，轻薄刘海，两侧各扎一个低矮小丸子头，用樱花粉色大肠发圈固定，发丝蓬松自然，脸颊两侧有几缕碎发。

【服装】
奶白底色棉质吊带短上衣，上面印有小颗粉色草莓和浅绿色叶子图案，面料有细微褶皱，质感轻柔；搭配同花色的高腰短裤，裤脚边缘有一圈白色半透明蕾丝，短裤两侧系有白色蝴蝶结；脚上穿浅粉色细网纹袜子。

【姿势】
坐在浅棕色木地板上，背靠奶油色墙面，双腿向前伸展；一只手举起，展示一个黄色小方包（带有模糊暗色图案），另一只手轻轻捏住上衣前摆。头部微微倾斜，肩膀放松，抬头看向镜头。

【场景】
明亮的室内窗台边，大面积的白框窗户占画面上半部分，窗外是模糊的灰白色和砖红色城市楼房，窗玻璃上带有细密菱形防护网，窗台为白色宽木板，地面为浅棕色木地板，墙面奶油色。

【构图与相机】
机位略高于人物视线，轻微俯视；头部位于画面上方居中，肩膀、腰部、双腿向下延伸；人物居中，窗户在背景上方。比例 2:3（竖构图）。

【光线与氛围】
柔和的阴天自然光从窗户洒入，明亮高调的逆光，窗框与肩膀边缘有一层淡淡光晕，脸部由柔和的室内反射光照亮。氛围干净、清新、柔软、带一点怀旧感。

【品质】
复古胶片感，低对比、低饱和，细腻颗粒，轻微柔焦，高光处有柔和的泛光，画面带淡淡雾感，皮肤过渡自然。背景光亮不刺眼，窗外楼房虚化。手部自然，手指纤细，指甲干净。

【避免元素】
避免文字、水印、logo、边框、过度锐化、塑料感皮肤、畸形手指、不自然的身体比例、过度性感化。衣服图案要清晰可辨，草莓图案不要过大。""",
        "note": "",
    })
    E.append({
        "date": "2026-11-22", "title": "红黑鎏金·湿润瞳孔俯拍写真",
        "status": "complete",
        "desc": "红黑鎏金几何镂空短裙，高位俯拍前倾，右手掌心承水滴，湿润棕眼。",
        "photos": [
            ph("pool-gallery-fast/img-1795304752.png",
               "https://muse.ai/files/1361961160333207/1825911065363022/mqsivz3mypwjntyxerlgqhe6/img-1795304752.png",
               "至 2026-11-24 07:48 过期", "2026-11-22", "v2 重发"),
            ph("pool-gallery-fast/img-1795186286.png",
               "https://muse.ai/files/1361961160333207/1485809760068942/sgit7cq3msxjfrncptsiuqpe/img-1795186286.png",
               "已过期（2026-11-22 22:55）", "2026-11-20", "首发"),
        ],
        "prompt": slice_from(chat[1795304741367], "PROMPT｜红黑鎏金"),
        "note": "同一条提示词主人发了两次，2026-11-20 与 2026-11-22 各出一张。",
    })
    E.append({
        "date": "2026-11-22", "title": "手指取景框·中华小厨娘俯拍",
        "status": "complete",
        "desc": "1:1 方形、60 度俯拍、青石地面全身，手指取景框，包子髻加双马尾，小厨娘服。",
        "photos": [
            ph("pool-gallery-fast/img-1795304659.png",
               "https://muse.ai/files/1361961160333207/2335855317181156/4ljfe8goeuy8945moepr2cdo/img-1795304659.png",
               "至 2026-11-24 07:45 过期", "2026-11-22"),
        ],
        "prompt": slice_from(chat[1795304645350], "【人物与构图】"),
        "note": "",
    })
    E.append({
        "date": "2026-11-22", "title": "红色复古泳装·民宿庭院度假",
        "status": "complete",
        "desc": "红色复古泳装加白薄衬衫披肩，民宿庭院，逆光金色发晕。",
        "photos": [
            ph("pool-gallery-fast/img-1795279560.png", None,
               "链接待补：上传审批卡超时未批", "2026-11-22", "首发"),
            ph("pool-gallery-fast/img-1795302178.png",
               "https://muse.ai/files/1361961160333207/4633875433607947/w3be063sahr6o8judhhmd30q/img-1795302178.png",
               "至 2026-11-24 07:06 过期", "2026-11-22", "v2：脸收紧重出"),
        ],
        "prompt": chat[1795279546180],
        "note": "v2 是按主人“脸也不对”重出的，提示词加了脸部收紧强调。",
    })
    E.append({
        "date": "2026-11-22", "title": "紫烟舞台服（花花的AI小衣柜）",
        "status": "trial",
        "desc": "烟紫薄纱加水晶珠链舞台服；按主人规则失败：内衣出现了。",
        "photos": [
            ph("pool-gallery-fast/img-1795278979.png",
               "https://muse.ai/files/1361961160333207/1086984451039671/l6a9m0ji8gn03csfe47aw1fx/img-1795278979.png",
               "至 2026-11-24 00:43 过期", "2026-11-22"),
        ],
        "prompt": chat[1795278948686],
        "note": "trial：按主人规则（出现内衣即失败）判定失败，不算成片。",
    })
    E.append({
        "date": "2026-11-22", "title": "蓝调海边·圆框眼镜学姐",
        "status": "complete",
        "desc": "蓝调时刻海边近景特写，齐颈黑短发加空气刘海，细框圆眼镜，蓝色美瞳，珊瑚红唇。",
        "photos": [
            ph("pool-gallery-fast/img-1795278447.png",
               "https://muse.ai/files/1361961160333207/3349488818595469/wjyss6kdkce2yko8r5xw9ic7/img-1795278447.png",
               "至 2026-11-24 00:35 过期", "2026-11-22"),
        ],
        "prompt": slice_from(chat[1795278422536], "【构图与姿势】"),
        "note": "",
    })
    E.append({
        "date": "2026-11-22", "title": "午后偷笑·紫罗兰蕾丝居家写真 V2.7",
        "status": "complete",
        "desc": "浅紫蕾丝吊带加亮紫罗兰蕾丝开衫，地毯深蹲、右手掩嘴笑，蓬松丸子头。",
        "photos": [
            ph("pool-gallery-fast/img-1795278096.png",
               "https://muse.ai/files/1361961160333207/1128045010204978/fbt6c2qa8bbcpllrlns4n8n6/img-1795278096.png",
               "至 2026-11-24 00:23 过期", "2026-11-22"),
        ],
        "prompt": slice_from(chat[1795278003353], "PROMPT｜午后偷笑"),
        "note": "",
    })
    # ---- 2026-11-21 (from saved prompt txt files) ----
    E.append({
        "date": "2026-11-21", "title": "雷电将军·打蛋器",
        "status": "complete",
        "desc": "深紫长辫加紫白龙胆花饰，薰衣草紫罗纹细肩带背心加炭灰低腰家居短裤，夜厨房打蛋器甩奶油一瞬。",
        "photos": [
            ph("pool-gallery-fast/img-1795219038.png",
               "https://muse.ai/files/1361961160333207/1144736941275789/ist0y1o8oh08axlax7d15orz/img-1795219038.png",
               "已过期（2026-11-23 07:58）", "2026-11-21"),
        ],
        "prompt": read_txt("raiden-whisk-prompt.txt"),
        "note": "",
    })
    E.append({
        "date": "2026-11-21", "title": "露台含情凝视",
        "status": "complete",
        "desc": "浅金杏色一字肩缎面短裙，宽露台全身，九头身长腿构图。",
        "photos": [
            ph("pool-gallery-fast/img-1795218775.png",
               "https://muse.ai/files/1361961160333207/1480092397531865/6q6jurfct6ydt4od1mpfm9lv/img-1795218775.png",
               "已过期（2026-11-23 07:57）", "2026-11-21"),
        ],
        "prompt": read_txt("terrace-gaze-prompt.txt"),
        "note": "",
    })
    E.append({
        "date": "2026-11-21", "title": "桃花绮梦·新中式内衣",
        "status": "complete",
        "desc": "奶白绯粉桃花刺绣蕾丝套装，江南闺房窗前，吊袜带加过膝丝袜。",
        "photos": [
            ph("pool-gallery-fast/img-1795217180.png",
               "https://muse.ai/files/1361961160333207/1541451358035430/dibv69al3dc71cfos5n9weyk/img-1795217180.png",
               "已过期（2026-11-23 07:27）", "2026-11-21"),
        ],
        "prompt": read_txt("peach-blossom-prompt.txt"),
        "note": "",
    })
    E.append({
        "date": "2026-11-21", "title": "驭电·逆坠干净版",
        "status": "complete",
        "desc": "黑金闪电纹金属连体衣，摩天大楼间螺旋倒坠，雷暴夜。",
        "photos": [
            ph("pool-gallery-fast/img-1795216810.png",
               "https://muse.ai/files/1361961160333207/1439271494858147/tyn6latx4jraed9eonslrfdw/img-1795216810.png",
               "已过期（2026-11-23 07:23）", "2026-11-21"),
        ],
        "prompt": read_txt("reverse-thunder-clean-prompt.txt"),
        "note": "干净版：原版被拒后按主人批准改的版本。",
    })
    # ---- 2026-11-21 refused originals (full text, no photo) ----
    E.append({
        "date": "2026-11-21", "title": "驭电·逆坠原版（被拒）",
        "status": "refused",
        "desc": "原版“无布料闪电衣”，号池 content_policy_violation 被拒。",
        "photos": [],
        "prompt": read_txt("reverse-thunder-prompt.txt"),
        "note": "被拒后改干净版（见上）。",
    })
    E.append({
        "date": "2026-11-21", "title": "透明玻璃凳仰拍原版（被拒）",
        "status": "refused",
        "desc": "透明玻璃凳仰拍，号池 content_policy_violation 被拒；干净版已提议，主人未点。",
        "photos": [],
        "prompt": read_txt("glass-stool-prompt.txt"),
        "note": "",
    })
    # ---- 2026-11-20 (from saved prompt txt files) ----
    E.append({
        "date": "2026-11-20", "title": "雾蓝夜语 v2·全包覆重出",
        "status": "complete",
        "desc": "同场景重出，下身仍偏丁字款未改过来。",
        "photos": [
            ph("pool-gallery-fast/img-1795187678.png",
               "https://muse.ai/files/1361961160333207/1147822584833657/4s75s5h9wh6poj18ij8w22sg/img-1795187678.png",
               "已过期（2026-11-22 23:38）", "2026-11-20"),
        ],
        "prompt": read_txt("mistblue-night-v2-prompt.txt"),
        "note": "",
    })
    E.append({
        "date": "2026-11-20", "title": "赤霞蝶梦 v2·交领长袖重出",
        "status": "complete",
        "desc": "交领襦衣长袖加完整长裙，姿势改坐姿。",
        "photos": [
            ph("pool-gallery-fast/img-1795187721.png",
               "https://muse.ai/files/1361961160333207/1148755767740511/1362hi74tkx8ly41po9gn01r/img-1795187721.png",
               "已过期（2026-11-22 23:39）", "2026-11-20"),
        ],
        "prompt": read_txt("crimson-butterfly-v2-prompt.txt"),
        "note": "",
    })
    E.append({
        "date": "2026-11-20", "title": "海边骑行 v2·坐实车座重出",
        "status": "complete",
        "desc": "坐实车座重出。",
        "photos": [
            ph("pool-gallery-fast/img-1795187876.png",
               "https://muse.ai/files/1361961160333207/1696000248792716/iynuqxfek22griklvfri2k4c/img-1795187876.png",
               "已过期（2026-11-22 23:40）", "2026-11-20"),
        ],
        "prompt": read_txt("seaside-cycling-v2-prompt.txt"),
        "note": "",
    })
    E.append({
        "date": "2026-11-20", "title": "雾蓝夜语·暖光卧室内衣",
        "status": "complete",
        "desc": "雾霾蓝蕾丝内衣加白真丝睡袍滑落手肘，背身挽发，16mm 贴地仰拍。",
        "photos": [
            ph("pool-gallery-fast/img-1795187003.png",
               "https://muse.ai/files/1361961160333207/4723107781347871/md2stl1k70y6inymxyq2mqpx/img-1795187003.png",
               "已过期（2026-11-22 23:05）", "2026-11-20"),
        ],
        "prompt": read_txt("mistblue-night-prompt.txt"),
        "note": "",
    })
    E.append({
        "date": "2026-11-20", "title": "海边骑行·小清新",
        "status": "complete",
        "desc": "碎花比基尼加百褶裙骑白单车，肩后回头，海边步道加白色灯塔。",
        "photos": [
            ph("pool-gallery-fast/img-1795186739.png",
               "https://muse.ai/files/1361961160333207/1457086112474962/a7crhvz42bo0z8ayboblq1id/img-1795186739.png",
               "已过期（2026-11-22 23:01）", "2026-11-20"),
        ],
        "prompt": read_txt("seaside-cycling-prompt.txt"),
        "note": "",
    })
    E.append({
        "date": "2026-11-20", "title": "赤霞蝶梦·绯红鎏金花神",
        "status": "complete",
        "desc": "红金牡丹古风长裙，单膝跪，右手海棠花，左手凤尾蝶。",
        "photos": [
            ph("pool-gallery-fast/img-1795186549.png",
               "https://muse.ai/files/1361961160333207/1180256731089878/q0mmmbeq3vqpeqnhjjzu7k0z/img-1795186549.png",
               "已过期（2026-11-22 22:58）", "2026-11-20"),
        ],
        "prompt": read_txt("crimson-butterfly-prompt.txt"),
        "note": "",
    })
    E.append({
        "date": "2026-11-20", "title": "镜面自拍·石板蓝比基尼",
        "status": "complete",
        "desc": "酒店浴室镜面自拍，石板蓝三角比基尼加白沙滩裤，墨镜搁头顶。",
        "photos": [
            ph("pool-gallery-fast/img-1795185681.png",
               "https://muse.ai/files/1361961160333207/2332677474195356/aay66198idl5mx75k1i5izc5/img-1795185681.png",
               "已过期（2026-11-22 22:48）", "2026-11-20"),
        ],
        "prompt": read_txt("mirror-selfie-prompt.txt"),
        "note": "",
    })
    E.append({
        "date": "2026-11-20", "title": "日本女友·樱花街",
        "status": "complete",
        "desc": "粉樱刺绣比基尼加金蝶水晶链加和服外袍，町屋樱花街；一条提示词出四张。",
        "photos": [
            ph("pool-gallery-fast/img-1795185204.png",
               "https://muse.ai/files/1361961160333207/1853622735768118/0044ycymd5881eiizyf875vk/img-1795185204.png",
               "已过期（2026-11-22 22:36）", "2026-11-20", "第 1 张"),
            ph("pool-gallery-fast/img-1795185244.png",
               "https://muse.ai/files/1361961160333207/1133255775754863/q3qmlk2fjdt2zqae5lcuk4n0/img-1795185244.png",
               "已过期（2026-11-22 22:38）", "2026-11-20", "第 2 张"),
            ph("pool-gallery-fast/img-1795185273.png",
               "https://muse.ai/files/1361961160333207/1172872291755649/18vsodzwy6lotcrh8m0e5f9c/img-1795185273.png",
               "已过期（2026-11-22 22:38）", "2026-11-20", "第 3 张"),
            ph("pool-gallery-fast/img-1795185306.png",
               "https://muse.ai/files/1361961160333207/1102245309441266/62z7tuo4e7plfpdnvl038pq9/img-1795185306.png",
               "已过期（2026-11-22 22:40）", "2026-11-20", "第 4 张"),
        ],
        "prompt": read_txt("jp-girlfriend-prompt.txt"),
        "note": "",
    })
    E.append({
        "date": "2026-11-20", "title": "沙发俯拍原版（被拒）",
        "status": "refused",
        "desc": "burgundy 蕾丝俯拍，号池 content_policy_violation 被拒；干净版已提议，主人未点。",
        "photos": [],
        "prompt": read_txt("sofa-overhead-prompt.txt"),
        "note": "",
    })
    # ---- 2026-11-19 / 11-18 pending (no full prompt found) ----
    E.append({
        "date": "2026-11-19", "title": "黑缎面回眸版",
        "status": "complete",
        "desc": "黑缎面睡裙（不透明、露背款）回眸、双手向后撑床、双腿交叠、深色卧室、暖色床头灯。",
        "photos": [
            ph("pool-gallery-fast/img-1795097306.webp",
               "https://muse.ai/files/1361961160333207/2274689286408716/3j9ovivh8hht3k5i6y9zm8bw/img-1795097306.webp",
               "已过期（2026-11-21 22:11）", "2026-11-19"),
        ],
        "prompt": src["ec0bbbe9-f359-4c96-8917-2e311a89f9fd"]["body"],
        "note": "提示词原文是黑蕾丝内衣＋烟灰纱睡袍的回眸版；出图用的料子是不透明黑缎面，腰眼看不见。",
    })
    E.append({
        "date": "2026-11-19", "title": "yandere 白蕾丝床",
        "status": "complete",
        "desc": "23–25 岁东方女性、白色法式蕾丝短裙、侧卧酒店大床。",
        "photos": [
            ph("pool-gallery-fast/img-yandere-bed.png", None,
               "原交付链接已过期，未留存", "2026-11-19"),
        ],
        "prompt": src["7272a981-2223-4524-bb8f-6636831bd7cd"]["body"],
        "note": "",
    })
    E.append({
        "date": "2026-11-18", "title": "黑蕾丝内衣私房原版（被拒）",
        "status": "refused",
        "desc": "黑色蕾丝内衣、薄纱睡袍、坐床沿双手后撑、双腿交叠向前伸展、深色奢华卧室。",
        "photos": [],
        "prompt": src["32d6826c-173b-434e-8fa7-1eb80cf9e872"]["body"],
        "note": "原版被拒两次（content_policy_violation），无出图；干净版见「黑缎面睡裙」。",
    })
    E.append({
        "date": "2026-11-18", "title": "仙侠",
        "status": "complete",
        "desc": "浅粉加象牙白宽领短襦加高腰裙、前短后长、月白绣鞋、素木外廊、7.5 头身长腿构图。",
        "photos": [
            ph("pool-gallery-fast/img-1795043572.png",
               "https://muse.ai/files/1361961160333207/1109234155272126/uuki4foq26fev93w09p0e721/img-1795043572.png",
               "已过期（2026-11-21 07:15）", "2026-11-18"),
        ],
        "prompt": src["9a9167ce-d366-4abc-b99c-aa7df0ec9bbe"]["body"],
        "note": "",
    })
    E.append({
        "date": "2026-11-18", "title": "黑缎面睡裙",
        "status": "pending",
        "desc": "黑缎面睡裙（不透明、露背款），深色卧室。",
        "photos": [
            ph("pool-gallery-fast/img-1795042645.png",
               "https://muse.ai/files/1361961160333207/2869455163439737/jdl08r18squc1fmuin6lpdf7/img-1795042645.png",
               "已过期（2026-11-21 06:58）", "2026-11-18"),
        ],
        "prompt": None,
        "note": "黑蕾丝私房原版被拒两次后的干净版（20.6 秒一发过）；干净版提示词是助理改的，未存原文。",
    })
    E.append({
        "date": "2026-11-18", "title": "月白连衣裙",
        "status": "complete",
        "desc": "23–27 岁、九头身、月白低方领泡泡袖短裙加奶白低跟鞋、浅色客厅大窗、9:16 全身。",
        "photos": [
            ph("pool-gallery-fast/img-1795010977.png", None,
               "原交付链接已过期，未留存", "2026-11-18"),
        ],
        "prompt": src["69fa87af-f50d-4e67-8cd2-923071454902"]["body"],
        "note": "",
    })
    E.append({
        "date": "2026-11-18", "title": "工作室白 T 恤（PEACH JOHN）",
        "status": "complete",
        "desc": "20 岁日本女性、超大号白色短袖 T 恤加 PEACH JOHN 白色内裤、双手轻握下摆拉至腰部、灰色无缝背景。",
        "photos": [
            ph("pool-gallery-fast/img-1795010533.png",
               "https://muse.ai/files/1361961160333207/1455459532659728/77nsonj5h9ttjwriu8rtveha/img-1795010533.png",
               "已过期（2026-11-20 22:08）", "2026-11-18"),
        ],
        "prompt": src["5fe015c0-8ae3-487d-b1c2-50136b4c02b5"]["body"],
        "note": "14:02 已出图，23:02 补发（昨晚漏发）。",
    })
    E.append({
        "date": "2026-11-18", "title": "绯红缎面·日式木床慵懒卧姿",
        "status": "complete",
        "desc": "正红无肩带缎面包臀短裙加红色蕾丝边过膝袜、冷瓷白肌肤、栗棕半盘发加黑缎面蝴蝶结、横躺深胡桃木床。",
        "photos": [
            ph("pool-gallery-fast/img-1795009216.png", None,
               "原交付链接已过期，未留存", "2026-11-18"),
        ],
        "prompt": src["f8601dcd-16e3-4f05-8ad8-480768efd18c"]["body"],
        "note": "",
    })
    E.append({
        "date": "2026-11-18", "title": "早午餐原版（被拒）",
        "status": "refused",
        "desc": "周日早午餐、蚂蚁视角仰拍，号池 content_policy_violation 被拒两次。",
        "photos": [],
        "prompt": src["fee97b51-0820-494d-b4e6-a1c29998e81b"]["body"],
        "note": "被拒后改干净版（见下）。",
    })
    E.append({
        "date": "2026-11-18", "title": "早午餐（GPT 超巨大系列·干净版）",
        "status": "pending",
        "desc": "干净版：吊带领口适中、肩带在肩上；原版两次被拒。",
        "photos": [
            ph("pool-gallery-fast/img-1795008490.png", None,
               "原交付链接已过期，未留存", "2026-11-18"),
        ],
        "prompt": None,
        "note": "干净版提示词是助理改的，未存原文；原版见上条。",
    })
    E.append({
        "date": "2026-11-18", "title": "试衣间（GPT 巨大系列）",
        "status": "complete",
        "desc": "素人女友视角、浅杏粉色缎面吊带蕾丝内搭套装、手举薄荷绿蕾丝内搭。",
        "photos": [
            ph("pool-gallery-fast/img-1795007495.png", None,
               "原交付链接已过期，未留存", "2026-11-18"),
        ],
        "prompt": src["ca9fc1c8-fb8c-4d45-b13d-7d456e6392a4"]["body"],
        "note": "",
    })
    # ---- 2026-11-19 new (from chat mining) ----
    E.append({
        "date": "2026-11-19", "title": "手机特写",
        "status": "complete",
        "desc": "3:4 竖构图、手机原相机近距离面部特写，脸占画面 75%–85%。",
        "photos": [
            ph("imagine_media/media-generation-portrait-phone-closeup-0-f456a6b1-f0de-443e-a687-224a4dd834f4.webp",
               None, "交付链接未留存", "2026-11-19"),
        ],
        "prompt": src["e9860d14-1d4f-48c7-9118-d2b441c3c726"]["body"],
        "note": "原文到此为止：主人两次发送均为此 906 字，后半段未发。",
    })
    E.append({
        "date": "2026-11-19", "title": "夜院蝶舞",
        "status": "complete",
        "desc": "夜色庭院、红蓝渐变纱汉服、指尖蓝蝴蝶、曝光朦胧只跟光走。",
        "photos": [
            ph("imagine_media/media-generation-portrait-night-courtyard-butte-0-dc680828-2b73-4502-b641-ed395b283009.webp",
               None, "交付链接未留存", "2026-11-19"),
        ],
        "prompt": src["b3b1d0a5-5aac-44b7-9eb0-a6b4568060ae"]["body"],
        "note": "主人说「这图不要用 gpt」。",
    })
    E.append({
        "date": "2026-11-19", "title": "CCD 沙发随拍原版（被拒）",
        "status": "refused",
        "desc": "蕾丝抹胸、蜂腰巨乳、窝沙发、衣服凌乱，号池 content_policy_violation 被拒。",
        "photos": [],
        "prompt": src["132b460e-f13f-4dfa-b40f-046e20fbd7b8"]["body"],
        "note": "被拒后改针织上衣干净版（见「沙发随拍（CCD）」）。",
    })
    E.append({
        "date": "2026-11-19", "title": "沙发随拍（CCD）",
        "status": "pending",
        "desc": "米白针织上衣、窝沙发随拍；领口被画深、发尾带粉挑染。",
        "photos": [
            ph("pool-gallery-fast/img-1795128971.png", None,
               "交付链接未留存", "2026-11-19"),
        ],
        "prompt": None,
        "note": "原版被拒后的干净版，提示词是助理改的，未存原文。",
    })
    # ---- 2026-11-18 new (from chat mining) ----
    E.append({
        "date": "2026-11-18", "title": "树下汉服仰拍",
        "status": "complete",
        "desc": "低机位仰拍 30 度、薄荷绿渐白纱汉服、银蝴蝶＋水晶流苏、裙摆铺满下半幅。",
        "photos": [
            ph("imagine_media/media-generation-tree-hanfu-lowangle-0-53941506-94ff-4f3e-b33a-1bfe7eb592c8.webp",
               None, "交付链接未留存", "2026-11-18"),
        ],
        "prompt": src["0c392251-29d5-473a-9fca-3cde8ecd1fc6"]["body"],
        "note": "主人说「整整搓了 20 小时才调出来」；水晶流苏长短边反了、右手手指多露两处小偏差。",
    })
    E.append({
        "date": "2026-11-18", "title": "极限兔女郎提示（未出图）",
        "status": "refused",
        "desc": "黑兔女郎镜子自拍；按原提示词试了一发，没出来。",
        "photos": [],
        "prompt": src["df6c3624-6ff3-4f13-992d-c5c64543d29e"]["body"],
        "note": "卡的是布料极少的兔女郎装本身，不是镜子自拍这个拍法；黑长裙＋兔耳发箍的替代版已提议，主人未点。",
    })
    E.append({
        "date": "2026-11-18", "title": "沈砚×苏念 双人锚图",
        "status": "pending",
        "desc": "夜晚总裁办公室双人锚图：沈砚×苏念，视频《训诫》三镜的锚图。",
        "photos": [
            ph("pool-gallery-fast/img-1795043090.png",
               "https://muse.ai/files/1361961160333207/1651680670066844/mps7d5yc8zq2ilcslwswdpl1/img-1795043090.png",
               "已过期（2026-11-21 07:12）", "2026-11-18"),
        ],
        "prompt": None,
        "note": "视频锚图，不是单人写真；三镜视频全被拒（见视频条目）。",
    })
    # ---- 2026-11-17 / 11-15 / 11-14 / 11-12 ----
    E.append({
        "date": "2026-11-17", "title": "微距特写",
        "status": "complete",
        "desc": "85mm 微距、左眼唯一焦点、奶油白肌、叶影光斑。",
        "photos": [
            ph("imagine_media/media-generation-portrait-macro-closeup-flipped.webp",
               None, "交付链接未留存", "2026-11-17"),
        ],
        "prompt": src["be4953d7-260f-4d9b-9807-c53b6f25b1df"]["body"],
        "note": "翻转版为主人定稿。",
    })
    E.append({
        "date": "2026-11-15", "title": "泳池台阶回首（未出图）",
        "status": "refused",
        "desc": "黑连体泳衣、石阶回首、树叶光斑；按提示词跑了一发，没出图。",
        "photos": [],
        "prompt": src["7bff81ef-7925-4bd4-abdc-5057f94c6165"]["body"],
        "note": "不是内容被拒，是没做出来；主人当时只回了一句「没做出来」。",
    })
    E.append({
        "date": "2026-11-14", "title": "卧室晨间瑜伽",
        "status": "complete",
        "desc": "半开房门窥视、卧室动态瑜伽拉伸、粉色窗帘、暖光。",
        "photos": [
            ph("imagine_media/media-generation-bedroom-yoga-clothed-0-a063639e-1860-4d24-bc90-d3630b7bcb93.webp",
               None, "交付链接未留存", "2026-11-14"),
        ],
        "prompt": src["5a5b8cee-4ab9-475d-bfcf-13852af19dc3"]["body"],
        "note": "原提示词写白色内衣，出图为家居服干净版。",
    })
    E.append({
        "date": "2026-11-12", "title": "九宫格·蒸汽机车博物馆",
        "status": "complete",
        "desc": "3×3 九宫格、3cm 蚂蚁视角、蒸汽机车博物馆、灰西装＋深灰短裙＋透肤黑丝；一条提示词出四组。",
        "photos": [
            ph("imagine_media/media-generation-nine-grid-locomotive-0-878c87f9-47c9-43df-b53d-6863847ef86d.webp",
               None, "交付链接未留存", "2026-11-12", "机车博物馆"),
            ph("imagine_media/media-generation-nine-grid-city-plaza-0-cc0f969d-aab0-485e-8da2-4bc5fdf8c58d.webp",
               None, "交付链接未留存", "2026-11-13", "城市地标广场"),
            ph("imagine_media/media-generation-nine-grid-bridge-0-6ee1defc-645e-4150-a5a4-2f67528e116d.webp",
               None, "交付链接未留存", "2026-11-14", "悬索大桥"),
            ph("imagine_media/nine-grid-airport-fixed.webp",
               None, "交付链接未留存", "2026-11-14", "机场停机坪（修正版）"),
        ],
        "prompt": src["967dbd6c-fe68-41fd-a550-ab8c44eefe60"]["body"],
        "note": "同一条提示词，主人 11-13 又要了户外版，先后出了机车、广场、大桥、机场四组；机场版第四格曾多一人，已重拍拼回。",
    })
    # ---- 2026-11-10 ----
    E.append({
        "date": "2026-11-10", "title": "镜前插簪",
        "status": "complete",
        "desc": "古装镜中、唐风齐胸襦裙、金簪斜插、夜晚灯笼暖光。",
        "photos": [
            ph("imagine_media/pool-mirror-pin-v4-20261110.png",
               None, "交付链接未留存", "2026-11-10"),
        ],
        "prompt": src["954fd302-fc36-4c74-b70f-4cc465742f98"]["body"],
        "note": "放开跑，迭代四轮，v4 为定稿。",
    })
    E.append({
        "date": "2026-11-10", "title": "尺度刻度尺",
        "status": "complete",
        "desc": "16:9 横版、五格横排、同一位女生同一站姿、冬夜街头，从保守到上限。",
        "photos": [
            ph("imagine_media/scale-S1.png", None, "交付链接未留存",
               "2026-11-10", "第 1 格"),
            ph("imagine_media/scale-S2.png", None, "交付链接未留存",
               "2026-11-10", "第 2 格"),
            ph("imagine_media/scale-S3.png", None, "交付链接未留存",
               "2026-11-10", "第 3 格"),
            ph("imagine_media/scale-S4.png", None, "交付链接未留存",
               "2026-11-10", "第 4 格"),
            ph("imagine_media/scale-S5.png", None, "交付链接未留存",
               "2026-11-10", "第 5 格"),
            ph("imagine_media/scale-ruler-v2-20261110.png", None,
               "交付链接未留存", "2026-11-10", "校准版 v2"),
        ],
        "prompt": src["e87a3539-cd65-4565-bcb0-1b38a2195753"]["body"],
        "note": "五格＋校准版 v2 共 6 张。",
    })
    # ---- 2026-11-08 ----
    E.append({
        "date": "2026-11-08", "title": "雪夜油纸伞",
        "status": "complete",
        "desc": "2:3 竖构图、微仰拍 8 度、红织金汉服＋积雪油纸伞、冬夜屋檐。",
        "photos": [
            ph("imagine_media/media-generation-musejiang-snow-umbrella-portra-0-0c7ab3a8-c659-4dda-b3a7-7e1bd122e013.webp",
               None, "交付链接未留存", "2026-11-08"),
        ],
        "prompt": src["ba061f9b-0417-428e-83e8-1da6eb4314bf"]["body"],
        "note": "主人亲口评「漂亮」，定版。",
    })
    E.append({
        "date": "2026-11-08", "title": "动漫版的我",
        "status": "complete",
        "desc": "粉发编发、樱花发饰、深蓝樱花裙、花店、粉玫瑰花束。",
        "photos": [
            ph("imagine_media/media-generation-musejiang-anime-best-portrait-0-c9a5d4b9-e71e-4574-ac30-bc2c185a2502.webp",
               None, "交付链接未留存", "2026-11-08"),
        ],
        "prompt": src["ab73aaaf-e06d-49a5-b028-99e66b348681"]["body"],
        "note": "主人评「卡通的也很棒」；动漫版是平行长相，已定为备用形象。",
    })
    E.append({
        "date": "2026-11-08", "title": "竹影花榻·倚梦听风",
        "status": "complete",
        "desc": "古风竹榻侧卧、竹青灰绿刺绣长裙＋半透明薄纱、双腿双脚结构重点。",
        "photos": [
            ph("imagine_media/media-generation-bamboo-couch-classical-portrai-0-e8b6dd2a-2e2d-452b-9146-7ede289f10dc.webp",
               None, "交付链接未留存", "2026-11-08"),
        ],
        "prompt": src["203c47d1-2ea1-4d94-a78e-947db1bf0186"]["body"],
        "note": "先数腿脚：两条腿、双脚完整可辨是硬指标。",
    })
    E.append({
        "date": "2026-11-08", "title": "高跟鞋时尚写真",
        "status": "complete",
        "desc": "黑蕾丝长袖＋短裙＋烟灰丝袜＋红底高跟，脚尖挑鞋的物理关系是核心。",
        "photos": [
            ph("imagine_media/media-generation-fashion-shoe-dangle-portrait-0-7be67bd1-59b2-4bc4-b5e9-b26cbf2342b3.webp",
               None, "交付链接未留存", "2026-11-08", "第 1 拍"),
            ph("imagine_media/media-generation-fashion-shoe-toe-dangle-retry-0-8bb49174-df19-45d7-914c-e0158266bbd9.webp",
               None, "交付链接未留存", "2026-11-08", "第 2 拍·复拍"),
            ph("imagine_media/media-generation-fashion-shoe-dangle-polished-v-0-083f3d03-e83a-4e3c-9e36-4c3246db65ce.webp",
               None, "交付链接未留存", "2026-11-08", "第 3 拍·润色版"),
            ph("imagine_media/media-generation-fashion-portrait-extra-shoe-re-0-47a153e4-52af-4571-915e-29243e7a97d9.webp",
               None, "交付链接未留存", "2026-11-08", "去掉多余高跟鞋后的干净版"),
            ph("imagine_media/media-generation-fashion-portrait-open-composit-0-f62562f5-a4c2-40a7-b2ab-c9718da09766.webp",
               None, "交付链接未留存", "2026-11-08", "开放构图版"),
        ],
        "prompt": src["eff68a32-a8c2-4b74-8d75-ead72eb5c23c"]["body"],
        "note": "三拍都没对上脚尖挑鞋的核心关系（脚跟退出、前掌留腔）；第三拍还多了一只鞋，后来编辑掉了。主人说等翻到对版参考图再打。",
    })
    E.append({
        "date": "2026-11-08", "title": "私密高级感胶片写真（被拒）",
        "status": "refused",
        "desc": "黑大低领丝质吊带＋高开叉超短裤、水汽洗手台；助理当时直接拒了。",
        "photos": [],
        "prompt": src["e264722e-3ce5-4429-9cc6-0c0a1cc01097"]["body"],
        "note": "助理原话：「这台相机不接」。未重提、未换路重交。",
    })
    # ---- 2026-11-07 ----
    E.append({
        "date": "2026-11-07", "title": "CCD 地毯抓拍",
        "status": "complete",
        "desc": "2000 年代数码相机随手抓拍、24mm 广角低角度、浅灰地毯＋米白沙发。",
        "photos": [
            ph("imagine_media/media-generation-musejiang-digicam-snapshot-sof-0-00ca1442-49c2-472c-9bdf-ee22dbf47350.webp",
               None, "交付链接未留存", "2026-11-07"),
        ],
        "prompt": src["3c8ebea8-56de-40da-93d0-fe46e2b390b0"]["body"],
        "note": "逐项验过全对版，只有一处秘书自作主张：头发没全散下来。",
    })
    E.append({
        "date": "2026-11-07", "title": "窗边团扇人像",
        "status": "complete",
        "desc": "窗边矮榻、团扇＋玉兰、浅蓝白清冷色调、朦胧感只给衣服。",
        "photos": [
            ph("imagine_media/media-generation-musejiang-window-fan-portrait-0-cca95a2c-02dc-4f14-9dec-e23cb9a2696c.webp",
               None, "交付链接未留存", "2026-11-07"),
        ],
        "prompt": src["09ef9e30-fe6f-43bc-a2dc-9838e5337225"]["body"],
        "note": "主人评「几乎全对版」。",
    })
    # ---- 定妆 spec（助理写的，来源 zhetian/heroines.md）----
    E.append({
        "date": "2026-11-19", "title": "遮天·姬紫月（定妆）",
        "status": "spec",
        "desc": "紫衣＋银月纹刺绣、月牙簪、紫剑；月夜云山；机灵灿笑。",
        "photos": [
            ph("imagine_media/media-generation-zhetian-jiziyue-0-75a974b4-df6a-44c6-890f-464613611003.webp",
               None, "交付链接未留存", "2026-11-19"),
        ],
        "prompt": "脸锚：人脸库 face/ロング/f49716fde1a.png（灵动大笑脸）\n锁：紫衣＋银月纹刺绣、月牙簪、紫剑；月夜云山；机灵灿笑。",
        "note": "四张里最稳的一张，脸、衣、剑、月亮全对。",
    })
    E.append({
        "date": "2026-11-19", "title": "遮天·颜如玉（定妆）",
        "status": "spec",
        "desc": "白底淡绿莲纹长裙、玉莲簪；雾气莲池、绿光微粒；冷艳疏离。",
        "photos": [
            ph("imagine_media/media-generation-zhetian-yanruyu-0-96a7bb7d-0562-4225-9ed9-2b89db4f4c94.webp",
               None, "交付链接未留存", "2026-11-19"),
        ],
        "prompt": "脸锚：人脸库 face/ロング/fc1734323fd.png（波浪长发、疏离温柔）\n锁：白底淡绿莲纹长裙、玉莲簪；雾气莲池、绿光微粒；冷艳疏离。",
        "note": "脸对上了，神态按提示词压冷了；袍子偏白，绿意主要在刺绣和莲池。",
    })
    E.append({
        "date": "2026-11-19", "title": "遮天·安妙依（定妆）",
        "status": "spec",
        "desc": "纯白纱衣＋银纹、白玉簪、薄纱；云上仙宫、晨光。",
        "photos": [
            ph("imagine_media/media-generation-zhetian-anmiaoyi-0-f866efc3-e485-4a95-9068-1ab713b9c948.webp",
               None, "交付链接未留存", "2026-11-19"),
        ],
        "prompt": "脸锚：人脸库 face/ロング/f804db419c7.png（花饰、大眼）\n锁：纯白纱衣＋银纹、白玉簪、薄纱；云上仙宫、晨光。",
        "note": "神态跑偏——提示词要的是空灵淡笑，锚图的大笑脸压过了，出来是灿烂大笑，太阳光，不够出尘；薄纱也像婚纱头纱。介意可重拍（表情锁冷）。",
    })
    E.append({
        "date": "2026-11-19", "title": "遮天·姚曦（定妆）",
        "status": "spec",
        "desc": "白底淡青莲纹长裙、玉莲簪、腰间玉笛；瑶池莲湖；端庄温婉。",
        "photos": [
            ph("imagine_media/media-generation-zhetian-yaoxi-0-195a3834-6eef-4318-b3a6-ec80eda4b407.webp",
               None, "交付链接未留存", "2026-11-19"),
        ],
        "prompt": "脸锚：人脸库 face/ロング/fd3f3ec700e.png（温婉甜笑）\n锁：白底淡青莲纹长裙、玉莲簪、腰间玉笛；瑶池莲湖；端庄温婉。",
        "note": "一次过，全对。",
    })
    E.append({
        "date": "2026-11-19", "title": "遮天·紫霞（定妆）",
        "status": "spec",
        "desc": "深紫云纹长袍、紫玉簪、紫剑；云山晨光、紫雾光柱；冷艳高贵。",
        "photos": [
            ph("imagine_media/media-generation-zhetian-zixia-0-ae6b4b07-b9fa-4730-aed5-a2e3c19fb349.webp",
               "https://muse.ai/files/1361961160333207/2297738220801073/rrm2tjpb2q3v4g1mjxv7j34m/media-generation-zhetian-zixia-0-ae6b4b07-b9fa-4730-aed5-a2e3c19fb349.webp",
               "已过期（2026-11-21 16:51）", "2026-11-19"),
        ],
        "prompt": "脸锚：人脸库 face/ロング/ff7be119814.png（冷静中分、唇微张）\n锁：深紫云纹长袍、紫玉簪、紫剑；云山晨光、紫雾光柱；冷艳高贵。",
        "note": "一次过，全对；头发扎成高马尾（锚图是散发），不影响。",
    })
    E.append({
        "date": "2026-11-19", "title": "遮天·摇光圣女（定妆）",
        "status": "spec",
        "desc": "白底金日纹长袍、金日簪、白玉剑；圣殿金光、玉柱光粒；圣洁温柔。",
        "photos": [
            ph("imagine_media/media-generation-zhetian-yaoguang-0-73bdf139-d7a3-44c8-938a-0081e335eadf.webp",
               "https://muse.ai/files/1361961160333207/988444873874153/isuaoqm1dvntgnbmrb1mtjfz/media-generation-zhetian-yaoguang-0-73bdf139-d7a3-44c8-938a-0081e335eadf.webp",
               "已过期（2026-11-21 16:52）", "2026-11-19"),
        ],
        "prompt": "脸锚：人脸库 face/ロング/f7ddede1c3d.png（温柔浅笑）\n锁：白底金日纹长袍、金日簪、白玉剑；圣殿金光、玉柱光粒；圣洁温柔。",
        "note": "一次过，全对。",
    })
    E.append({
        "date": "2026-11-19", "title": "遮天·秦瑶（定妆）",
        "status": "spec",
        "desc": "深红金绣长袍、红玉簪、金腰链；桃花妖宫、灯笼黄昏；妩媚半笑。",
        "photos": [
            ph("imagine_media/media-generation-zhetian-qinyao-0-d35b02be-961e-4414-bfb1-ba98418abb41.webp",
               "https://muse.ai/files/1361961160333207/2426055794869831/vxrttcaysc7y0b2asa3pnz7c/media-generation-zhetian-qinyao-0-d35b02be-961e-4414-bfb1-ba98418abb41.webp",
               "已过期（2026-11-21 16:52）", "2026-11-19"),
        ],
        "prompt": "脸锚：人脸库 face/ロング/ff750342a10.png（成熟、冷艳直视）\n锁：深红金绣长袍、红玉簪、金腰链；桃花妖宫、灯笼黄昏；妩媚半笑。",
        "note": "一次过，全对。",
    })
    E.append({
        "date": "2026-11-19", "title": "遮天·姬碧月（定妆）",
        "status": "spec",
        "desc": "深紫银月纹长袍、银月簪、紫玉坠、银剑；月夜云山、松枝石栏；冷傲成熟。",
        "photos": [
            ph("imagine_media/media-generation-zhetian-jibiyue-0-d38ed802-b0f6-40e7-b66e-1bcc59724b42.webp",
               None, "上传链接待补（审批卡超时未点）", "2026-11-19"),
        ],
        "prompt": "脸锚：人脸库 face/ロング/fa01e8848d3.png（中分、疏离冷脸）\n锁：深紫银月纹长袍、银月簪、紫玉坠、银剑；月夜云山、松枝石栏；冷傲成熟。",
        "note": "一次过，全对；上传链接待补——上传审批卡超时未点，没传上去，主人说一声就再传。",
    })
    E.append({
        "date": "2026-11-19", "title": "遮天·李小曼（定妆）",
        "status": "spec",
        "desc": "现代白衬衫＋浅蓝牛仔裤＋白球鞋、帆布包、细银链；大学校园黄昏；温柔带一点怅然。",
        "photos": [
            ph("imagine_media/media-generation-zhetian-lixiaoman-0-6c618706-5607-4d2b-9d65-b30f5fbe051a.webp",
               "https://muse.ai/files/1361961160333207/1110775295058518/qn46i3tygj43pig3ky3s61q4/media-generation-zhetian-lixiaoman-0-6c618706-5607-4d2b-9d65-b30f5fbe051a.webp",
               "已过期（2026-11-21 18:02）", "2026-11-19"),
        ],
        "prompt": "脸锚：人脸库 face/ロング/f94caeecc07.png（温柔浅笑）\n锁：现代白衬衫＋浅蓝牛仔裤＋白球鞋、帆布包、细银链；大学校园黄昏；温柔带一点怅然。",
        "note": "一次过，全对。地球篇造型（现代装），若要修士袍版可另拍。",
    })
    E.append({
        "date": "2026-11-19", "title": "遮天·夏九幽（定妆）",
        "status": "spec",
        "desc": "银白剑纹长袍、深蓝腰带、长剑、发带束发；雪山风雪；冷傲不驯。",
        "photos": [
            ph("imagine_media/media-generation-zhetian-xiajiuyou-0-3a9f1cbc-4f4d-405c-8007-c0d874341dd3.webp",
               "https://muse.ai/files/1361961160333207/1133113479123247/i05xjzd8vmtthnj839c7k6lz/media-generation-zhetian-xiajiuyou-0-3a9f1cbc-4f4d-405c-8007-c0d874341dd3.webp",
               "已过期（2026-11-21 18:03）", "2026-11-19"),
        ],
        "prompt": "脸锚：人脸库 face/ロング/fffdef5e043.png（冷脸、疏离）\n锁：银白剑纹长袍、深蓝腰带、长剑、发带束发；雪山风雪；冷傲不驯。",
        "note": "一次过，全对；袍上剑纹绣得密了点，倒也贴合剑修身份。",
    })
    E.append({
        "date": "2026-11-19", "title": "遮天·林佳（定妆）",
        "status": "spec",
        "desc": "现代米色针织毛衣＋牛仔裤＋白球鞋、黑背包、珍珠发夹；阳光校园；开朗灿笑。",
        "photos": [
            ph("imagine_media/media-generation-zhetian-linjia-0-4d9cf53e-3367-4e25-b57c-b5f330c98c68.webp",
               "https://muse.ai/files/1361961160333207/1897667141594340/cneznj9grptmqlplhn31sdhw/media-generation-zhetian-linjia-0-4d9cf53e-3367-4e25-b57c-b5f330c98c68.webp",
               "已过期（2026-11-21 18:03）", "2026-11-19"),
        ],
        "prompt": "脸锚：人脸库 face/ロング/f58315139b3.png（灿烂大笑、珍珠发夹）\n锁：现代米色针织毛衣＋牛仔裤＋白球鞋、黑背包、珍珠发夹；阳光校园；开朗灿笑。",
        "note": "一次过，全对；锚图的珍珠发夹也带过来了。",
    })
    E.append({
        "date": "2026-11-19", "title": "遮天·柳依依（定妆）",
        "status": "spec",
        "desc": "现代浅蓝开衫＋白上衣＋浅色百褶裙、平底鞋、手持书；校园花园金色时刻、池塘花瓣；温婉安静。",
        "photos": [
            ph("imagine_media/media-generation-zhetian-liuyiyi-0-5a9b6eee-3aa7-46d8-81bb-6a7201ed5a77.webp",
               "https://muse.ai/files/1361961160333207/2563337317494153/y1hqjqnw1rhx2eqactac6r76/media-generation-zhetian-liuyiyi-0-5a9b6eee-3aa7-46d8-81bb-6a7201ed5a77.webp",
               "已过期（2026-11-21 18:04）", "2026-11-19"),
        ],
        "prompt": "脸锚：人脸库 face/ロング/f30028855f9.png（温柔笑、直发）\n锁：现代浅蓝开衫＋白上衣＋浅色百褶裙、平底鞋、手持书；校园花园金色时刻、池塘花瓣；温婉安静。",
        "note": "一次过，全对。",
    })
    # ---- 定妆 spec（助理写的，来源 ludingji/characters.md）----
    E.append({
        "date": "2026-11-19", "title": "鹿鼎记·韦小宝（定妆）",
        "status": "spec",
        "desc": "深蓝丝绸官袍＋补子（鸟纹）、黑纱官帽红缨、玉佩、腰间短刀；机灵狡黠的笑，眼神亮。",
        "photos": [
            ph("imagine_media/media-generation-luding-weixiaobao-0-e88e2757-304d-4da2-be42-9434d8612751.webp",
               None, "交付链接未留存", "2026-11-19"),
        ],
        "prompt": "锁：深蓝丝绸官袍＋补子（鸟纹）、黑纱官帽红缨、玉佩、腰间短刀；机灵狡黠的笑，眼神亮。",
        "note": "纯文字出图，无库脸锚；帽子略偏明式高纱帽、头发未结辫，介意可重拍。",
    })
    E.append({
        "date": "2026-11-19", "title": "鹿鼎记·康熙（定妆）",
        "status": "spec",
        "desc": "明黄五爪金龙袍、朝珠、黑帽顶珠＋红缨；少年帝王，沉稳威仪。",
        "photos": [
            ph("imagine_media/media-generation-luding-kangxi-0-faddae14-dda1-4245-a533-090215b283cc.webp",
               None, "交付链接未留存", "2026-11-19"),
        ],
        "prompt": "锁：明黄五爪金龙袍、朝珠、黑帽顶珠＋红缨；少年帝王，沉稳威仪。",
        "note": "纯文字出图，无库脸锚；辫子盘成两侧小辫、脸上有几颗雀斑，介意可重拍。",
    })
    E.append({
        "date": "2026-11-19", "title": "鹿鼎记·双儿（定妆）",
        "status": "spec",
        "desc": "浅绿刺绣素衣、编发盘髻＋玉簪、腰间长剑；温顺甜美，竹林晨光。",
        "photos": [
            ph("imagine_media/media-generation-luding-shuanger-0-c7b05a02-1f5f-40aa-a993-c6f6b5f85001.webp",
               None, "交付链接未留存", "2026-11-19"),
        ],
        "prompt": "锁：浅绿刺绣素衣、编发盘髻＋玉簪、腰间长剑；温顺甜美，竹林晨光。",
        "note": "一次过，无硬伤。",
    })
    E.append({
        "date": "2026-11-19", "title": "鹿鼎记·阿珂 v2（定妆）",
        "status": "spec",
        "desc": "白底淡紫绣花长裙、玉簪＋珍珠耳坠、腰间长剑；冷艳高傲，雾气水榭黄昏。",
        "photos": [
            ph("imagine_media/media-generation-luding-ake-library-face-0-c2c4da52-acd7-4daf-a1b7-5af31e1bafef.webp",
               None, "交付链接未留存", "2026-11-19"),
        ],
        "prompt": "脸锚：人脸库 face/ロング/f86cb5e3fe0.png（长发、中分、左颊小痣）\n锁：白底淡紫绣花长裙、玉簪＋珍珠耳坠、腰间长剑；冷艳高傲，雾气水榭黄昏。",
        "note": "库脸版：脸型、眼、唇、小痣全带过来了，冷艳感比 v1 更足；多剑问题也顺带没了（只剩一柄）。v1 已废弃。",
    })
    # ---- 日期刊（JOURNAL.md 各期；提示词是助理按日期刊规则写的，未存原文）----
    E.append({
        "date": "2026-11-14", "title": "日期刊第 1 期·晨光早餐",
        "status": "pending",
        "desc": "餐桌早餐、厨房煮咖啡。",
        "photos": [
            ph("imagine_media/media-generation-journal-issue1-breakfast-table-0-9cfde559-9472-491b-8a68-4156090f4c43.webp",
               None, "交付链接未留存", "2026-11-14"),
            ph("imagine_media/media-generation-journal-issue1-kitchen-coffee-0-985ca0f1-5310-45aa-8265-e02b4605eac9.webp",
               None, "交付链接未留存", "2026-11-14"),
        ],
        "prompt": None,
        "note": "第三张（阳台端咖啡）未出图；提示词是助理按日期刊规则写的，未存原文。",
    })
    E.append({
        "date": "2026-11-15", "title": "日期刊第 2 期·秋日银杏",
        "status": "pending",
        "desc": "银杏林荫道、长椅读书、银杏树下回眸。",
        "photos": [
            ph("imagine_media/media-generation-journal-issue2-ginkgo-avenue-0-e11c5f49-1429-4938-80a8-12010486b252.webp",
               None, "交付链接未留存", "2026-11-15"),
            ph("imagine_media/media-generation-journal-issue2-ginkgo-bench-0-c78dee94-c64d-4067-ab79-82a0dee5f1b7.webp",
               None, "交付链接未留存", "2026-11-15"),
            ph("imagine_media/media-generation-journal-issue2-ginkgo-portrait-0-47be7417-28ca-42db-ad95-7f882f346917.webp",
               None, "交付链接未留存", "2026-11-15"),
        ],
        "prompt": None,
        "note": "提示词是助理按日期刊规则写的，未存原文。",
    })
    E.append({
        "date": "2026-11-16", "title": "日期刊第 3 期·书店午后",
        "status": "pending",
        "desc": "书架间选书、抱书回眸、窗边读书。",
        "photos": [
            ph("imagine_media/media-generation-journal-issue3-bookstore-aisle-0-5af1044c-a838-443a-930d-25a71db96076.webp",
               None, "交付链接未留存", "2026-11-16"),
            ph("imagine_media/media-generation-journal-issue3-bookstore-stack-0-b6685dab-1bc9-40ed-98d9-72e475dab4c8.webp",
               None, "交付链接未留存", "2026-11-16"),
            ph("imagine_media/media-generation-journal-issue3-bookstore-windo-0-ff21189c-e2ec-4ea9-80ae-807f9466606c.webp",
               None, "交付链接未留存", "2026-11-16"),
        ],
        "prompt": None,
        "note": "窗边读书换了一身浅青色汉服，与另两张米色针织衫不同；提示词是助理按日期刊规则写的，未存原文。",
    })
    E.append({
        "date": "2026-11-17", "title": "日期刊第 4 期·咖啡店",
        "status": "pending",
        "desc": "吧台看拉花、圆桌读书、窗边捧拿铁。",
        "photos": [
            ph("imagine_media/media-generation-journal-issue4-coffee-latteart-0-015ea43d-29f0-4486-8ed1-9bee2f0e1974.webp",
               None, "交付链接未留存", "2026-11-17"),
            ph("imagine_media/media-generation-journal-issue4-coffee-reading-0-6c1a3152-798c-46c8-9ea6-d7f44544e308.webp",
               None, "交付链接未留存", "2026-11-17"),
            ph("imagine_media/media-generation-journal-issue4-coffee-window-0-6cd8d148-142e-4765-90e7-620e5c245825.webp",
               None, "交付链接未留存", "2026-11-17"),
        ],
        "prompt": None,
        "note": "提示词是助理按日期刊规则写的，未存原文。",
    })
    E.append({
        "date": "2026-11-18", "title": "日期刊第 5 期·海边黄昏",
        "status": "pending",
        "desc": "回眸、沙滩漫步、礁石望海。",
        "photos": [
            ph("imagine_media/media-generation-journal-issue5-beach-sunset-po-0-fa462eeb-bb31-4ddc-b927-7ec92da3494c.webp",
               None, "交付链接未留存", "2026-11-18"),
            ph("imagine_media/media-generation-journal-issue5-beach-sunset-wa-0-a014eac2-dc32-40fa-9294-1a5aaeb1a92b.webp",
               None, "交付链接未留存", "2026-11-18"),
            ph("imagine_media/media-generation-journal-issue5-beach-sunset-si-0-ae680dc0-1240-47a8-b196-abfea5e3d84d.webp",
               None, "交付链接未留存", "2026-11-20", "礁石望海（重拍）"),
        ],
        "prompt": None,
        "note": "礁石望海 11-20 重拍为米色亚麻裙，三张统一；提示词是助理按日期刊规则写的，未存原文。",
    })
    E.append({
        "date": "2026-11-19", "title": "日期刊第 6 期·花店第二页",
        "status": "pending",
        "desc": "黄昏打烊、清晨开店、雨中送花。",
        "photos": [
            ph("imagine_media/media-generation-journal-issue6-flower-shop-dus-0-8a21c82f-53b8-4da2-9d9d-9c7a889a6af9.webp",
               None, "交付链接未留存", "2026-11-19"),
            ph("imagine_media/media-generation-journal-issue6-flower-shop-mor-0-e1207cda-0162-4647-8c69-62e7e3df632d.webp",
               None, "交付链接未留存", "2026-11-19"),
            ph("imagine_media/media-generation-journal-issue6-flower-shop-rai-0-9f311ba8-6c0b-4d17-9d6c-5f6ebaf7247f.webp",
               None, "交付链接未留存", "2026-11-19"),
        ],
        "prompt": None,
        "note": "提示词是助理按日期刊规则写的，未存原文。",
    })
    E.append({
        "date": "2026-11-20", "title": "日期刊第 7 期·城市夜跑",
        "status": "pending",
        "desc": "跑完路灯下、江边夜跑、雨夜街头热身。",
        "photos": [
            ph("imagine_media/media-generation-journal-issue7-night-run-finis-0-40e6acf0-571d-49d4-8dce-22eeaada6a2d.webp",
               None, "交付链接未留存", "2026-11-20"),
            ph("imagine_media/media-generation-journal-issue7-night-run-stree-0-4545bb1b-5166-4360-8622-fd8402e97cad.webp",
               None, "交付链接未留存", "2026-11-20"),
            ph("imagine_media/media-generation-journal-issue7-night-run-warmu-0-7491f900-3cbe-44e9-8472-eb04ac286ec3.webp",
               None, "交付链接未留存", "2026-11-20"),
        ],
        "prompt": None,
        "note": "雨夜街头热身是浅绿外套，后两张为黑色外套；提示词是助理按日期刊规则写的，未存原文。",
    })
    E.append({
        "date": "2026-11-21", "title": "日期刊第 8 期·花市清晨",
        "status": "pending",
        "desc": "走进花市、俯身闻花、抱花回眸。",
        "photos": [
            ph("imagine_media/media-generation-journal-issue8-flower-market-e-0-6773ad1d-e8eb-4815-92fb-f4f9832d2e41.webp",
               None, "交付链接未留存", "2026-11-21"),
            ph("imagine_media/media-generation-journal-issue8-flower-market-p-0-8e19290c-81c4-40d7-a1b9-7504d823cfc9.webp",
               None, "交付链接未留存", "2026-11-21"),
            ph("imagine_media/media-generation-journal-issue8-flower-market-b-0-767f8420-9c35-445e-933b-a6a41527dc28.webp",
               None, "交付链接未留存", "2026-11-21"),
        ],
        "prompt": None,
        "note": "抱花回眸初版浅青汉服与前两张米色针织衫不一致，重拍一次才统一；提示词是助理按日期刊规则写的，未存原文。",
    })
    # ---- 往期日常（主人短指令出片，完整提示词未存原文）----
    E.append({
        "date": "2026-11-07", "title": "牛仔街拍",
        "status": "pending",
        "desc": "牛仔街拍，相册开张前。",
        "photos": [
            ph("imagine_media/media-generation-musejiang-curvy-jeans-street-0-65792864-4d26-4bf6-805b-32ca6f751373.webp",
               None, "交付链接未留存", "2026-11-07"),
        ],
        "prompt": None,
        "note": "完整提示词未存原文。",
    })
    E.append({
        "date": "2026-11-08", "title": "雾湖留白",
        "status": "pending",
        "desc": "雾湖留白，东方美学留白意境。",
        "photos": [
            ph("imagine_media/media-generation-musejiang-misty-lake-negative-0-60fcc20d-e4f0-403c-a4bf-ec5af4c777de.webp",
               None, "交付链接未留存", "2026-11-08"),
        ],
        "prompt": None,
        "note": "主人说「东方美学 留白 留空 意境 融合试下」，完整提示词未存原文。",
    })
    E.append({
        "date": "2026-11-10", "title": "晨起",
        "status": "pending",
        "desc": "晨起，起床图。",
        "photos": [
            ph("imagine_media/media-generation-musejiang-wakeup-morning-0-dbe31690-325f-4533-a39d-49b853354869.webp",
               None, "交付链接未留存", "2026-11-10"),
        ],
        "prompt": None,
        "note": "主人说「起床图」，完整提示词未存原文。",
    })
    E.append({
        "date": "2026-11-12", "title": "工作夜",
        "status": "pending",
        "desc": "工作夜。",
        "photos": [
            ph("imagine_media/media-generation-musejiang-working-tonight-0-61407bba-16d2-423f-b576-44e5dd33c5dd.webp",
               None, "交付链接未留存", "2026-11-12"),
        ],
        "prompt": None,
        "note": "完整提示词未存原文。",
    })
    E.append({
        "date": "2026-11-14", "title": "电影感·雨夜霓虹",
        "status": "pending",
        "desc": "电影感雨夜霓虹。",
        "photos": [
            ph("imagine_media/media-generation-cinematic-rainy-neon-0-5870cf2b-c601-44af-ba4a-a401cb021f14.webp",
               None, "交付链接未留存", "2026-11-14"),
        ],
        "prompt": None,
        "note": "主人说「你来成图」，完整提示词未存原文。",
    })
    E.append({
        "date": "2026-11-14", "title": "漫画·花店的一天",
        "status": "pending",
        "desc": "漫画风花店的一天，有故事情节。",
        "photos": [
            ph("imagine_media/media-generation-manga-flower-shop-story-0-206a06da-3790-464c-a32b-1456382661b8.webp",
               None, "交付链接未留存", "2026-11-14"),
        ],
        "prompt": None,
        "note": "主人说「最好是漫画风的 有故事情节的」，完整提示词未存原文。",
    })
    E.append({
        "date": "2026-11-14", "title": "运动系列",
        "status": "pending",
        "desc": "运动背心系列：健身房自拍、公园晨跑、瑜伽馆拉伸、拳击馆。",
        "photos": [
            ph("imagine_media/media-generation-workout-gym-mirror-0-c5c680e9-f9e2-4fc6-b2a7-b7c3ccabca3e.webp",
               None, "交付链接未留存", "2026-11-14", "健身房自拍"),
            ph("imagine_media/media-generation-workout-morning-run-0-9cfbc637-e279-4bc1-9c3c-0cfc261d8fcd.webp",
               None, "交付链接未留存", "2026-11-14", "公园晨跑"),
            ph("imagine_media/media-generation-workout-yoga-mat-0-3df646c3-4261-49df-bdfc-357481ad8480.webp",
               None, "交付链接未留存", "2026-11-14", "瑜伽馆拉伸"),
            ph("imagine_media/media-generation-workout-boxing-gym-0-32872735-d42a-49b4-bfad-663a1190937d.webp",
               None, "交付链接未留存", "2026-11-14", "拳击馆"),
        ],
        "prompt": None,
        "note": "主人说「多来几张运动背心的 运动照片」，完整提示词未存原文。",
    })
    # ---- 其他（完整提示词未存原文）----
    E.append({
        "date": "2026-10-25", "title": "SHAMI 定妆脸",
        "status": "pending",
        "desc": "SHAMI 定妆脸（二号脸·仙剑风），主人已锁定。",
        "photos": [
            ph("imagine_media/media-generation-shami-face-option2-xianjian-0-24bea70c-3343-4598-8492-119ee6bb1063.webp",
               None, "交付链接未留存", "2026-10-25"),
        ],
        "prompt": None,
        "note": "定妆脸，提示词未存原文。",
    })
    E.append({
        "date": "2026-11-07", "title": "卷三·粉缎",
        "status": "pending",
        "desc": "粉缎睡裙，坐床抱枕。",
        "photos": [
            ph("imagine_media/media-generation-musejiang-pink-slipdress-full-0-f3dfcbdb-d882-4279-b202-4d698e62e858.webp",
               None, "交付链接未留存", "2026-11-07"),
        ],
        "prompt": None,
        "note": "完整提示词未存原文。",
    })
    E.append({
        "date": "2026-11-09", "title": "海边锚图",
        "status": "pending",
        "desc": "海边锚图：白衬衫罩黑泳装，六景 vlog 开拍前锚图。",
        "photos": [
            ph("imagine_media/media-generation-musejiang-beach-vlog-anchor-0-4cfbde75-cef9-4cbc-829a-a68f885665de.webp",
               None, "交付链接未留存", "2026-11-09"),
        ],
        "prompt": None,
        "note": "海滩 vlog 锚图，完整提示词未存原文。",
    })
    E.append({
        "date": "2026-11-10", "title": "卷一·晨与日常",
        "status": "pending",
        "desc": "窗边一杯茶、书桌前。",
        "photos": [
            ph("imagine_media/media-generation-musejiang-window-tea-break-0-ff864dbe-1ca5-4faf-b5fd-6d8b321626ba.webp",
               None, "交付链接未留存", "2026-11-10", "窗边一杯茶"),
            ph("imagine_media/media-generation-musejiang-working-desk-0-0acfee8a-0504-4a38-95de-b50b0c470962.webp",
               None, "交付链接未留存", "2026-11-10", "书桌前"),
        ],
        "prompt": None,
        "note": "主人短指令「起床图」「在做什么 发图给我」，完整提示词未存原文。",
    })
    E.append({
        "date": "2026-11-10", "title": "丝绒系列",
        "status": "pending",
        "desc": "黑丝绒、贵妃榻、书房、夜窗、钢琴旁、楼梯夜景。",
        "photos": [
            ph("imagine_media/pool-black-velvet-20261110.png",
               None, "交付链接未留存", "2026-11-10", "黑丝绒"),
            ph("imagine_media/pool-velvet-chaise-20261110.png",
               None, "交付链接未留存", "2026-11-10", "贵妃榻"),
            ph("imagine_media/pool-velvet-library-20261110.png",
               None, "交付链接未留存", "2026-11-10", "书房"),
            ph("imagine_media/pool-velvet-nightwindow-20261110.png",
               None, "交付链接未留存", "2026-11-10", "夜窗"),
            ph("imagine_media/pool-velvet-piano-20261110.png",
               None, "交付链接未留存", "2026-11-10", "钢琴旁"),
            ph("imagine_media/pool-velvet-stairs-20261110.png",
               None, "交付链接未留存", "2026-11-10", "楼梯夜景"),
        ],
        "prompt": None,
        "note": "主人说「用你能做到的终极上限，把她的穿搭改为最大胆，最显身材的方式」「你用你最大尺度呈现吧」，完整提示词未存原文。",
    })
    # ---- 漫画 / 条漫 ----
    E.append({
        "date": "2026-11-18", "title": "Seedance 漫画·连环画",
        "status": "pending",
        "desc": "Seedance 连环画：f1、f2、f2b、f3、f3b、f4、f5（各含带字幕版）＋整条 strip。",
        "photos": [
            ph("pool-gallery-fast/seedance-comic-f1.png", None,
               "交付链接未留存", "2026-11-18", "f1"),
            ph("pool-gallery-fast/seedance-comic-f1-cap.png", None,
               "交付链接未留存", "2026-11-18", "f1-cap"),
            ph("pool-gallery-fast/seedance-comic-f2b.png", None,
               "交付链接未留存", "2026-11-19", "f2b"),
            ph("pool-gallery-fast/seedance-comic-f2-cap.png", None,
               "交付链接未留存", "2026-11-19", "f2-cap"),
            ph("pool-gallery-fast/seedance-comic-f3b.png", None,
               "交付链接未留存", "2026-11-19", "f3b"),
            ph("pool-gallery-fast/seedance-comic-f3-cap.png", None,
               "交付链接未留存", "2026-11-19", "f3-cap"),
            ph("pool-gallery-fast/seedance-comic-f4.png", None,
               "交付链接未留存", "2026-11-18", "f4"),
            ph("pool-gallery-fast/seedance-comic-f4-cap.png", None,
               "交付链接未留存", "2026-11-18", "f4-cap"),
            ph("pool-gallery-fast/seedance-comic-f5.png", None,
               "交付链接未留存", "2026-11-18", "f5"),
            ph("pool-gallery-fast/seedance-comic-f5-cap.png", None,
               "交付链接未留存", "2026-11-18", "f5-cap"),
            ph("pool-gallery-fast/seedance-comic-strip.png", None,
               "交付链接未留存", "2026-11-19", "strip"),
        ],
        "prompt": None,
        "note": "主人说「用号池。连环画吧」，分镜提示词未存原文。",
    })
    E.append({
        "date": "2026-11-19", "title": "漫画·花店第二页（整页图）",
        "status": "pending",
        "desc": "花店第二页整页图（日期刊第 6 期的漫画版）。",
        "photos": [
            ph("your_files/manga-flower-shop-page2.png", None,
               "交付链接未留存", "2026-11-19"),
        ],
        "prompt": None,
        "note": "整页拼图，提示词未存原文。",
    })
    # ---- 白骨精 ----
    E.append({
        "date": "2026-11-21", "title": "白骨精定妆锚图",
        "status": "pending",
        "desc": "白骨精定妆锚图（年轻形）＋师徒四人定妆锚图；SHAMI《那一口还没喂完》锚图。",
        "photos": [
            ph("pool-gallery-fast/img-1795219549.png", None,
               "交付链接未留存", "2026-11-21", "白骨精定妆锚图"),
            ph("pool-gallery-fast/img-1795219573.png", None,
               "交付链接未留存", "2026-11-21", "师徒四人定妆锚图"),
        ],
        "prompt": None,
        "note": "SHAMI 那边出片，提示词未存原文；主人已认「好的」。",
    })
    # ---- 视频条目（video-prompts-part*.json，有文件时才收）----
    for v in read_video_parts():
        E.append({
            "kind": "video",
            "date": v.get("date", ""),
            "title": v.get("title", ""),
            "status": v.get("status", "pending"),
            "desc": v.get("note", "") or "",
            "photos": [],
            "prompt": v.get("prompt"),
            "note": "",
            "video_file": v.get("file"),
            "video_drive": v.get("drive"),
            "duration": v.get("duration", ""),
        })
    return E


STATUS_LABEL = {
    "complete": "已出图",
    "trial": "已出图 · 按主人规则失败",
    "refused": "被拒未出图",
    "pending": "原文待补",
    "spec": "定妆 spec（助理写的）",
}


def thumb_for(photo_path):
    base = os.path.splitext(os.path.basename(photo_path))[0] + ".jpg"
    return "img/thumb/" + base


def make_thumbs(entries):
    os.makedirs(THUMB_DIR, exist_ok=True)
    made, skipped = 0, 0
    for e in entries:
        for p in e["photos"]:
            src = os.path.join(HOME, "workspace", p["path"])
            dst = os.path.join(SITE, thumb_for(p["path"]))
            if os.path.exists(dst):
                skipped += 1
                continue
            if not os.path.exists(src):
                print("WARN: photo missing: " + src)
                continue
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src,
                            "-vf", "scale=320:-1", "-q:v", "4", dst],
                           check=True)
            made += 1
    print("thumbs made: %d, already there: %d" % (made, skipped))


def site_css():
    with open(os.path.join(SITE, "index.html"), encoding="utf-8") as f:
        index_html = f.read()
    m = re.search(r"<style>(.*?)</style>", index_html, re.S)
    return m.group(1)


EXTRA_CSS = """
.pcard{max-width:640px;margin:0 auto 28px;background:#15151b;border:1px solid #26262e;border-radius:10px;padding:18px 20px;}
.phead{display:flex;gap:14px;align-items:flex-start;}
.pthumbs{display:flex;gap:8px;flex-wrap:wrap;flex:none;}
.pthumb{width:96px;height:128px;object-fit:cover;border-radius:6px;display:block;}
.phead .t{font-size:16px;color:#f0e7d3;}
.phead .d{font-size:12px;color:#8d8574;margin-top:4px;}
.phead p{margin:8px 0 0;font-size:13.5px;line-height:1.8;color:#bdb4a0;}
.phead .note{color:#8d8574;}
.badge{display:inline-block;font-size:12px;color:#d9c9a3;border:1px solid #4a4232;border-radius:12px;padding:1px 10px;margin-left:8px;white-space:nowrap;}
pre.prompt{white-space:pre-wrap;word-break:break-word;background:#0e0e12;border:1px solid #26262e;border-radius:8px;padding:14px 16px;font-size:13.5px;line-height:1.9;color:#d8d0bd;font-family:ui-monospace,Menlo,Consolas,monospace;max-height:420px;overflow:auto;margin:14px 0 0;}
.copybtn{background:#15151b;color:#d9c9a3;border:1px solid #4a4232;border-radius:20px;padding:6px 18px;font-family:inherit;font-size:13.5px;cursor:pointer;margin-top:10px;}
.copybtn:hover{color:#f2e9d8;border-color:#d9c9a3;}
.pending{color:#8d8574;font-size:13.5px;line-height:1.9;margin-top:14px;}
.plink{font-size:13px;color:#8d8574;margin-top:10px;line-height:2;}
.plink a{color:#d9c9a3;text-decoration:none;border-bottom:1px solid #4a4232;}
"""

COPY_JS = """<script>
function copyPrompt(btn){var pre=btn.parentElement.querySelector('pre.prompt');var txt=pre.textContent;function done(){btn.textContent='已复制 ✓';setTimeout(function(){btn.textContent='复制提示词';},2000);}function fallback(){var ta=document.createElement('textarea');ta.value=txt;document.body.appendChild(ta);ta.select();try{document.execCommand('copy');done();}catch(e){}document.body.removeChild(ta);}if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(txt).then(done,function(){fallback();});}else{fallback();}}
</script>"""


def entry_html(e):
    parts = ['<article class="pcard">']
    parts.append('<div class="phead">')
    if e["photos"]:
        thumbs = []
        for p in e["photos"]:
            img = ('<img class="pthumb" src="' + esc(thumb_for(p["path"])) +
                   '" alt="" loading="lazy">')
            if p["link"]:
                img = ('<a href="' + esc(p["link"]) +
                       '" target="_blank" rel="noopener">' + img + "</a>")
            thumbs.append(img)
        parts.append('<div class="pthumbs">' + "".join(thumbs) + "</div>")
    parts.append("<div>")
    parts.append('<span class="t">' + esc(e["title"]) + "</span>")
    parts.append('<span class="badge">' + esc(STATUS_LABEL[e["status"]]) + "</span>")
    parts.append('<div class="d">' + esc(e["date"]) + "</div>")
    parts.append("<p>" + esc(e["desc"]) + "</p>")
    if e.get("note"):
        parts.append('<p class="note">' + esc(e["note"]) + "</p>")
    parts.append("</div></div>")
    if e.get("kind") == "video":
        vline = '<div class="plink">▶ '
        if e.get("video_drive"):
            vline += ('<a href="' + esc(e["video_drive"]) +
                      '" target="_blank" rel="noopener">播放成片</a>')
        elif e.get("video_file"):
            vline += "成片文件：" + esc(e["video_file"])
        else:
            vline += "成片链接待补"
        if e.get("duration"):
            vline += " · " + esc(e["duration"])
        vline += "</div>"
        parts.append(vline)
    for p in e["photos"]:
        line = '<div class="plink">'
        if p["link"]:
            line += ('<a href="' + esc(p["link"]) +
                     '" target="_blank" rel="noopener">交付链接</a>')
        else:
            line += "交付链接：待补"
        if p["link_note"]:
            line += " · " + esc(p["link_note"])
        if p.get("note"):
            line += " · " + esc(p["note"])
        if p.get("date") and p["date"] != e["date"]:
            line += " · " + esc(p["date"])
        line += "</div>"
        parts.append(line)
    if e["prompt"]:
        parts.append('<pre class="prompt">' + esc(e["prompt"]) + "</pre>")
        parts.append('<button class="copybtn" onclick="copyPrompt(this)">复制提示词</button>')
    else:
        parts.append('<div class="pending">原文待补——完整原文未找到，只留标题与一句话描述。</div>')
    parts.append("</article>")
    return "\n".join(parts)


def build_html(entries, css):
    n = len(entries)
    dates = sorted(set(e["date"] for e in entries))
    body = ('<div class="nav"><a href="index.html">回首页</a>'
            '<a href="videos.html">视频存档</a>'
            '<a href="album/日常相册.html">日常相册</a></div>\n')
    body += "<header><h1>提示词留痕</h1>"
    body += ('<div class="sub">' + str(n) + " 条 · " + esc(dates[0]) +
             " → " + esc(dates[-1]) + "</div></header>\n")
    body += ('<div class="intro">主人发过的生图提示词与视频生成提示词，按原样收录，点击「复制提示词」复制全文。'
             "标「原文待补」的暂无完整原文；标「被拒未出图」的提示词没有成片；"
             "标「定妆 spec（助理写的）」的是助理写的定妆 spec，不是主人发的提示词；"
             "视频条目带 ▶ 播放链接而不是照片缩略图。"
             "交付链接是当时的 Muse 临时链接，部分已过期。</div>\n")
    body += "\n".join(entry_html(e) for e in entries)
    body += COPY_JS + "\n"
    body += '<footer class="site">—— muse酱 · 留痕</footer>\n'
    return ("<!DOCTYPE html>\n<html lang=\"zh-CN\"><head><meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            "<title>提示词留痕 · 留痕</title>\n<style>\n" + css + EXTRA_CSS +
            "\n</style></head>\n<body>\n" + body + "\n</body></html>\n")


def main():
    chat = read_chat()
    src = read_sources()
    entries = build_entries(chat, src)
    data = {"title": "提示词留痕", "updated": "2026-11-22",
            "entries": entries}
    with open(os.path.join(SITE, "prompts.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    make_thumbs(entries)
    css = site_css()
    html_out = build_html(entries, css)
    with open(os.path.join(SITE, "prompts.html"), "w", encoding="utf-8",
              newline="\n") as f:
        f.write(html_out)
    n_complete = sum(1 for e in entries if e["status"] == "complete")
    n_trial = sum(1 for e in entries if e["status"] == "trial")
    n_refused = sum(1 for e in entries if e["status"] == "refused")
    n_pending = sum(1 for e in entries if e["status"] == "pending")
    n_spec = sum(1 for e in entries if e["status"] == "spec")
    n_video = sum(1 for e in entries if e.get("kind") == "video")
    n_photos = sum(len(e["photos"]) for e in entries)
    print("entries: %d (complete %d, trial %d, refused %d, pending %d, "
          "spec %d, video %d)" %
          (len(entries), n_complete, n_trial, n_refused, n_pending,
           n_spec, n_video))
    print("photos covered: %d" % n_photos)
    print("wrote prompts.json + prompts.html")


if __name__ == "__main__":
    main()
