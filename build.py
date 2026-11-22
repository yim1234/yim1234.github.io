#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministic builder for the 留痕 (Liuhen) static site.

Reads ~/workspace/musejiang-journal/JOURNAL.md,
~/workspace/your_files/musejiang-album-20261110.html, extra-album.json
and videos.json (plus prompts.json, for the homepage 提示词留痕 section), regenerates ~/workspace/liuhen-site/ (this script's
own directory).

Rules:
- No timestamps, no random order: running twice produces identical bytes.
- Journal text (captions, 心得, 备注) is copied verbatim (HTML-escaped only).
- Journal photos are copied as files into img/, never base64-embedded.
- The v1 album keeps its embedded base64; it is split per volume by its
  own <h2> boundaries, content byte-for-byte.
- A new issue appended to JOURNAL.md appears automatically on rebuild.
"""
import hashlib
import html
import json
import os
import re
import shutil

HOME = os.path.expanduser("~")
JOURNAL = os.path.join(HOME, "workspace/musejiang-journal/JOURNAL.md")
V1_SRC = os.path.join(HOME, "workspace/your_files/musejiang-album-20261110.html")
OUT = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(OUT, "img")
EXTRA_ALBUM = os.path.join(OUT, "extra-album.json")
VIDEOS_JSON = os.path.join(OUT, "videos.json")
DRIVE_JSON = os.path.join(OUT, "drive-uploads.json")
SPECIALS_JSON = os.path.join(OUT, "specials.json")
AUDIO_DIR = os.path.join(OUT, "audio")

ISSUE_RE = re.compile(r"^### 第(\d+)期 · (\d{4}-\d{2}-\d{2}) · (.+?)\s*$")
PAST_RE = re.compile(r"^### 往期")
PHOTO_RE = re.compile(r"^- (.+?)：`([^`]+)`。配文：(.+)$")
EXTRA_PHOTO_RE = re.compile(r"^- 当日其他照片：(.+?) — `([^`]+)`。配文：(.+)$")
EXTRA_VIDEO_RE = re.compile(r"^- 当日其他视频：(.+?) — `([^`]+)` — (.+)$")
EXTRA_VOICE_RE = re.compile(r"^- 当日其他语音：(.+?) — `([^`]+)` — (.+)$")
EXTRA_NOTE_RE = re.compile(r"^- 当日其他注：(.+)$")
XINDE_RE = re.compile(r"^- 心得：(.+)$")
BEIZHU_RE = re.compile(r"^- 备注：(.+)$")
PAST_BULLET_RE = re.compile(r"^- (\d{4}-\d{2}-\d{2}) · (.+)$")
BACKTICK_RE = re.compile(r"`([^`]+)`")


def parse_journal(text):
    lines = text.split("\n")
    issues = []
    past = []
    cur = None  # ("issue", dict) or ("past", None)
    for line in lines:
        m = ISSUE_RE.match(line)
        if m:
            cur = ("issue", {"n": int(m.group(1)), "date": m.group(2),
                             "theme": m.group(3).strip(), "photos": [],
                             "extras_photos": [], "extras_videos": [],
                             "extras_voice": [], "extras_note": "",
                             "xinde": "", "beizhu": ""})
            issues.append(cur[1])
            continue
        if PAST_RE.match(line):
            cur = ("past", None)
            continue
        if line.startswith("### ") or line.startswith("## "):
            cur = None
            continue
        if cur is None:
            continue
        if cur[0] == "issue":
            iss = cur[1]
            m = EXTRA_PHOTO_RE.match(line)
            if m:
                iss["extras_photos"].append({"title": m.group(1).strip(),
                                             "src": m.group(2).strip(),
                                             "caption": m.group(3).strip()})
                continue
            m = EXTRA_VIDEO_RE.match(line)
            if m:
                iss["extras_videos"].append({"title": m.group(1).strip(),
                                             "src": m.group(2).strip(),
                                             "duration": m.group(3).strip()})
                continue
            m = EXTRA_VOICE_RE.match(line)
            if m:
                iss["extras_voice"].append({"title": m.group(1).strip(),
                                           "src": m.group(2).strip(),
                                           "duration": m.group(3).strip()})
                continue
            m = EXTRA_NOTE_RE.match(line)
            if m:
                iss["extras_note"] = m.group(1).strip()
                continue
            m = PHOTO_RE.match(line)
            if m:
                iss["photos"].append({"title": m.group(1).strip(),
                                      "src": m.group(2).strip(),
                                      "caption": m.group(3).strip()})
                continue
            m = XINDE_RE.match(line)
            if m:
                iss["xinde"] = m.group(1).strip()
                continue
            m = BEIZHU_RE.match(line)
            if m:
                iss["beizhu"] = m.group(1).strip()
                continue
        else:
            m = PAST_BULLET_RE.match(line)
            if m:
                date, rest = m.group(1), m.group(2)
                if "。心得：" not in rest:
                    raise ValueError("往期缺少心得: " + line)
                left, xinde = rest.split("。心得：", 1)
                title, items = left.split("：", 1)
                photos = []
                for seg in items.split("、"):
                    seg = seg.strip()
                    pm = BACKTICK_RE.search(seg)
                    if not pm:
                        raise ValueError("往期缺少图片路径: " + line)
                    label = seg[:pm.start()].strip()
                    photos.append({"label": label or title.strip(),
                                   "src": pm.group(1).strip()})
                past.append({"date": date, "title": title.strip(),
                             "photos": photos, "xinde": xinde.strip()})
    issues.sort(key=lambda x: x["n"])
    return issues, past


def collect_images(issues, past, extra=None, specials=None):
    by_base = {}
    for iss in issues:
        for ph in iss["photos"] + iss["extras_photos"]:
            base = os.path.basename(ph["src"])
            if base in by_base and by_base[base] != ph["src"]:
                raise ValueError("同名不同图: " + base)
            by_base[base] = ph["src"]
    for sp in (specials or []):
        for vol in sp.get("volumes", []):
            for item in vol.get("items", []):
                if item.get("kind") != "photo" or not item.get("src"):
                    continue
                base = os.path.basename(item["src"])
                if base in by_base and by_base[base] != item["src"]:
                    raise ValueError("同名不同图: " + base)
                by_base[base] = item["src"]
    for item in past:
        for ph in item["photos"]:
            base = os.path.basename(ph["src"])
            if base in by_base and by_base[base] != ph["src"]:
                raise ValueError("同名不同图: " + base)
            by_base[base] = ph["src"]
    for item in (extra or []):
        base = os.path.basename(item["src"])
        if base in by_base and by_base[base] != item["src"]:
            raise ValueError("同名不同图: " + base)
        by_base[base] = item["src"]
    return by_base


def load_extra():
    """Extra album photos not in JOURNAL.md (character stills, portraits).

    Returns the list from extra-album.json in file order; missing file
    means no extra photos. Each entry needs src/title/date/caption and
    a category of 定妆, 写真 or 日常.
    """
    if not os.path.exists(EXTRA_ALBUM):
        return []
    with open(EXTRA_ALBUM, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("extra-album.json must be a list")
    for i, item in enumerate(data):
        for key in ("src", "title", "date", "caption", "category"):
            if not item.get(key):
                raise ValueError("extra-album.json[%d] missing %s" % (i, key))
        if item["category"] not in ("定妆", "写真", "日常"):
            raise ValueError("extra-album.json[%d] bad category: %s" % (i, item["category"]))
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", item["date"]):
            raise ValueError("extra-album.json[%d] bad date: %s" % (i, item["date"]))
    return data


def load_videos():
    """Finished-video archive (see videos.json, transcribed from
    ~/workspace/musejiang-journal/MEDIA-INDEX.md).

    Returns the list in file order; missing file means no videos.
    Each entry needs date/title/duration/project/path, and the path
    must exist under ~/workspace (checked here so a moved file fails
    the build loudly instead of publishing a dead entry).
    """
    if not os.path.exists(VIDEOS_JSON):
        return []
    with open(VIDEOS_JSON, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("videos.json must be a list")
    for i, item in enumerate(data):
        for key in ("date", "title", "duration", "project", "path"):
            if not item.get(key):
                raise ValueError("videos.json[%d] missing %s" % (i, key))
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", item["date"]):
            raise ValueError("videos.json[%d] bad date: %s" % (i, item["date"]))
        full = os.path.join(HOME, "workspace", item["path"])
        if not os.path.exists(full):
            raise ValueError("videos.json[%d] 视频不存在: %s" % (i, item["path"]))
    return data


def load_drive():
    """Drive 播放链接：文件名 -> webViewLink。

    先读 videos.json 里每条自带的 drive，再补 drive-uploads.json 的
    entries（path -> webViewLink）。两个文件缺一个也不报错。
    """
    by_base = {}
    try:
        with open(VIDEOS_JSON, encoding="utf-8") as f:
            videos = json.load(f)
        for v in videos:
            if v.get("drive"):
                by_base[os.path.basename(v["path"])] = v["drive"]
    except (OSError, ValueError):
        pass
    try:
        with open(DRIVE_JSON, encoding="utf-8") as f:
            data = json.load(f)
        for e in data.get("entries", []):
            if e.get("webViewLink") and e.get("path"):
                by_base.setdefault(os.path.basename(e["path"]), e["webViewLink"])
    except (OSError, ValueError, AttributeError):
        pass
    return by_base


def load_specials():
    """存档特辑（见 specials.json，周日由日期刊任务写入）。

    缺文件表示还没有特辑，返回 []。每期需要 n/title/date_range/
    intro/footer/volumes；每卷需要 title/items；每件 kind 为 photo
    或 video，photo 需要 title/date/src/caption，video 需要
    title/date/src/duration（drive 可空，缺省时按文件名查
    load_drive 的结果）。
    """
    if not os.path.exists(SPECIALS_JSON):
        return []
    with open(SPECIALS_JSON, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("specials.json must be a list")
    for i, sp in enumerate(data):
        for key in ("n", "title", "date_range", "intro", "footer", "volumes"):
            if not sp.get(key):
                raise ValueError("specials.json[%d] missing %s" % (i, key))
        for j, vol in enumerate(sp["volumes"]):
            if not vol.get("title") or not isinstance(vol.get("items"), list):
                raise ValueError("specials.json[%d] volume %d bad" % (i, j))
            for k, item in enumerate(vol["items"]):
                if item.get("kind") == "photo":
                    for key in ("title", "date", "src", "caption"):
                        if not item.get(key):
                            raise ValueError("specials.json[%d] item %d missing %s" % (i, k, key))
                elif item.get("kind") == "video":
                    for key in ("title", "date", "src", "duration"):
                        if not item.get(key):
                            raise ValueError("specials.json[%d] item %d missing %s" % (i, k, key))
                else:
                    raise ValueError("specials.json[%d] item %d bad kind" % (i, k))
    return data


def collect_audio(issues):
    by_base = {}
    for iss in issues:
        for a in iss["extras_voice"]:
            base = os.path.basename(a["src"])
            if base in by_base and by_base[base] != a["src"]:
                raise ValueError("同名不同音频: " + base)
            by_base[base] = a["src"]
    return by_base


def copy_audio(by_base):
    os.makedirs(AUDIO_DIR, exist_ok=True)
    for base, src in sorted(by_base.items()):
        src_path = os.path.expanduser(src)
        if not os.path.exists(src_path):
            raise ValueError("音频不存在: " + src)
        dst = os.path.join(AUDIO_DIR, base)
        if not os.path.exists(dst) or sha256_file(dst) != sha256_file(src_path):
            shutil.copyfile(src_path, dst)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_images(by_base):
    os.makedirs(IMG_DIR, exist_ok=True)
    for base, src in sorted(by_base.items()):
        src_path = os.path.expanduser(src)
        if not os.path.exists(src_path):
            raise ValueError("图片不存在: " + src)
        dst = os.path.join(IMG_DIR, base)
        if not os.path.exists(dst) or sha256_file(dst) != sha256_file(src_path):
            shutil.copyfile(src_path, dst)
    # drop stale images no longer referenced
    for name in os.listdir(IMG_DIR):
        if name not in by_base and name.endswith(".webp"):
            os.remove(os.path.join(IMG_DIR, name))


def parse_v1(src):
    css = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
    intro = re.search(r'<div class="intro">(.*?)</div>', src, re.S).group(1)
    footer = re.search(r"<footer>(.*?)</footer>", src, re.S).group(1)
    heads = list(re.finditer(r"<h2>(.*?)</h2>", src, re.S))
    vols = []
    for i, hm in enumerate(heads):
        start = hm.end()
        end = heads[i + 1].start() if i + 1 < len(heads) else src.find("<footer>")
        title = re.sub(r"<[^>]+>", "", hm.group(1)).strip()
        vols.append({"title": title, "body": src[start:end]})
    return css, intro, footer, vols


EXTRA_CSS = """
.nav{max-width:1080px;margin:20px auto 0;text-align:center;font-size:14px;letter-spacing:.15em;}
.nav a{color:#d9c9a3;text-decoration:none;border-bottom:1px solid #4a4232;padding-bottom:2px;margin:0 9px;}
.nav a:hover{color:#f2e9d8;}
.toc{max-width:640px;margin:0 auto;line-height:2.4;font-size:15.5px;}
.toc a{color:#e8e2d4;text-decoration:none;border-bottom:1px solid #4a4232;}
.toc a:hover{color:#f2e9d8;}
.toc .d{color:#8d8574;font-size:13px;margin-left:10px;}
.xinde{max-width:640px;margin:36px auto 0;background:#15151b;border:1px solid #26262e;border-radius:10px;padding:18px 20px;line-height:2;font-size:15px;color:#cfc7b4;}
.xinde .lab,.note .lab{display:block;color:#d9c9a3;letter-spacing:.3em;font-size:13px;margin-bottom:8px;}
.note{max-width:640px;margin:18px auto 0;color:#8d8574;font-size:13.5px;line-height:1.9;}
.pager{max-width:640px;margin:48px auto 0;display:flex;justify-content:space-between;font-size:14px;}
.pager a{color:#d9c9a3;text-decoration:none;}
.pager .none{color:#55504a;}
.filter{max-width:1080px;margin:8px auto 26px;text-align:center;}
.filter button{background:#15151b;color:#cfc7b4;border:1px solid #26262e;border-radius:20px;padding:6px 16px;margin:0 5px;font-family:inherit;font-size:13.5px;cursor:pointer;}
.filter button.on{border-color:#d9c9a3;color:#f2e9d8;}
footer.site{max-width:640px;margin:64px auto 0;text-align:center;color:#8d8574;font-size:13.5px;line-height:2;}
.vrow{max-width:640px;margin:0 auto;line-height:2.2;font-size:15px;display:flex;align-items:center;gap:12px;}
.vrow .thumb{width:96px;height:54px;object-fit:cover;border-radius:6px;flex:none;}
.vrow .t{color:#e8e2d4;}
.vrow .d{color:#8d8574;font-size:13px;margin-left:10px;}
.lockbox{max-width:640px;margin:24px auto;padding:30px 20px;text-align:center;background:#15151b;border:1px solid #26262e;border-radius:10px;line-height:2;font-size:15px;color:#cfc7b4;}
.lockbox input{background:#0f0f13;color:#f2e9d8;border:1px solid #4a4232;border-radius:6px;padding:8px 10px;font-size:15px;width:130px;text-align:center;margin:12px 6px 0;font-family:inherit;}
.lockbox button{background:#d9c9a3;color:#15151b;border:0;border-radius:6px;padding:8px 18px;font-size:15px;cursor:pointer;font-family:inherit;}
.lockerr{display:block;color:#d98a7a;font-size:13.5px;margin-top:8px;min-height:20px;}
"""


def esc(s):
    return html.escape(s, quote=True)


def page(title, body, css):
    shown = esc(title) if title == "留痕" else esc(title) + " · 留痕"
    return ("<!DOCTYPE html>\n<html lang=\"zh-CN\"><head><meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            "<title>" + shown + "</title>\n<style>\n" + css + "\n</style></head>\n<body>\n"
            + body + "\n</body></html>\n")


def nav_home():
    return '<div class="nav"><a href="../index.html">回首页</a><a href="../prompts.html">提示词</a></div>\n'


def nav_root():
    return '<div class="nav"><a href="index.html">回首页</a><a href="prompts.html">提示词</a></div>\n'


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

def issue_filename(n):
    return "issue-%03d.html" % n


LOCK_JS = """<script>
(function(){
var boxes=document.querySelectorAll('.locked');
for(var i=0;i<boxes.length;i++){
(function(box){
var btn=box.querySelector('button'),input=box.querySelector('input'),err=box.querySelector('.lockerr');
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function unlock(){
var v=input.value.trim();
if(v===box.getAttribute('data-pw')){
var data=JSON.parse(box.querySelector('script[type="application/json"]').textContent);
var grid=box.querySelector('.grid'),h='';
for(var j=0;j<data.length;j++){var p=data[j];
h+='<figure><a href="'+esc(p.src)+'"><img src="'+esc(p.src)+'" alt="'+esc(p.title)+'"></a><figcaption><span class="t">'+esc(p.title)+'</span><span class="d">'+esc(p.date)+'</span><p>'+esc(p.caption)+'</p></figcaption></figure>';}
grid.innerHTML=h;grid.style.display='';box.querySelector('.lockbox').style.display='none';
}else{err.textContent='不对，再试一次';input.select();}
}
btn.addEventListener('click',unlock);
input.addEventListener('keydown',function(e){if(e.key==='Enter'){unlock();}});
})(boxes[i]);
}
})();
</script>
"""


def figure(img_rel, title, date, caption):
    out = '<figure><a href="' + img_rel + '"><img src="' + img_rel + '" alt="' + esc(title) + '"></a>'
    out += '<figcaption><span class="t">' + esc(title) + '</span>'
    if date:
        out += '<span class="d">' + esc(date) + '</span>'
    out += '<p>' + esc(caption) + '</p></figcaption></figure>'
    return out


def issue_page(iss, prev_n, next_n, css, drive_by_base=None):
    # 卷的样子：标题合一、每图带日期戳、心得作卷尾结语（照初版专辑）。
    figs = []
    for ph in iss["photos"]:
        base = os.path.basename(ph["src"])
        figs.append(figure("../img/" + base, ph["title"], iss["date"], ph["caption"]))
    body = nav_home()
    body += '<header><h1>第 ' + str(iss["n"]) + ' 期 · ' + esc(iss["theme"]) + '</h1></header>\n'
    body += '<div class="grid">\n' + "\n".join(figs) + '\n</div>\n'
    if iss["extras_photos"]:
        # 当日其他照片上锁：密码为本期日期月日四位（如 1122）；解锁前不加载图片。
        pw = iss["date"][5:7] + iss["date"][8:10]
        photos_json = json.dumps(
            [{"src": "../img/" + os.path.basename(ph["src"]), "title": ph["title"],
              "date": iss["date"], "caption": ph["caption"]} for ph in iss["extras_photos"]],
            ensure_ascii=False).replace("<", "\\u003c")
        body += '<h2>当日其他照片</h2>\n'
        body += '<div class="locked" data-pw="' + pw + '">\n'
        body += ('<div class="lockbox">🔒 当日其他照片已上锁，输入当日日期查看（如 1122）<br>'
                 '<input type="text" inputmode="numeric" autocomplete="off" placeholder="月日，如 1122"> '
                 '<button type="button">查看</button><span class="lockerr"></span></div>\n')
        body += '<div class="grid" style="display:none"></div>\n'
        body += '<script type="application/json">' + photos_json + '</script>\n</div>\n'
        body += LOCK_JS
    if iss["extras_videos"]:
        body += '<h2>当日视频</h2>\n'
        for v in iss["extras_videos"]:
            base = os.path.basename(v["src"])
            thumb = "../img/thumb/" + os.path.splitext(base)[0] + ".jpg"
            drive = (drive_by_base or {}).get(base, "")
            link = (' <a class="play" href="' + esc(drive) + '" target="_blank" rel="noopener">▶ 播放</a>') if drive else ''
            body += ('<div class="vrow"><img class="thumb" src="' + esc(thumb) + '" alt="" loading="lazy">'
                     '<span class="t">' + esc(v["title"]) + '</span>' + link +
                     '<span class="d">' + esc(iss["date"]) + ' · ' + esc(v["duration"]) + '</span></div>\n')
    if iss["extras_voice"]:
        body += '<h2>当日语音</h2>\n'
        for a in iss["extras_voice"]:
            base = os.path.basename(a["src"])
            body += ('<div class="vrow"><audio controls preload="none" src="../audio/' + esc(base) + '"></audio>'
                     '<span class="t">' + esc(a["title"]) + '</span>'
                     '<span class="d">' + esc(iss["date"]) + ' · ' + esc(a["duration"]) + '</span></div>\n')
    if iss["extras_note"]:
        body += '<div class="note"><span class="lab">当日其他</span>' + esc(iss["extras_note"]) + '</div>\n'
    if iss["beizhu"]:
        body += '<div class="note"><span class="lab">备 注</span>' + esc(iss["beizhu"]) + '</div>\n'
    body += '<footer>' + esc(iss["xinde"]) + '<br><br>—— muse酱 · ' + esc(iss["date"]) + '</footer>\n'
    prev_link = ('<a href="' + issue_filename(prev_n) + '">← 上一期</a>'
                 if prev_n else '<span class="none">← 上一期</span>')
    next_link = ('<a href="' + issue_filename(next_n) + '">下一期 →</a>'
                 if next_n else '<span class="none">下一期 →</span>')
    body += '<div class="pager">' + prev_link + next_link + '</div>\n'
    title = "第 %d 期 · %s" % (iss["n"], iss["theme"])
    return page(title, body, css)


def past_category(title):
    if "九宫格" in title:
        return "九宫格"
    if "运动" in title:
        return "运动"
    if "漫画" in title:
        return "漫画"
    return "日常"


def issue_category(theme):
    if "漫画" in theme:
        return "漫画"
    if "夜跑" in theme or "运动" in theme:
        return "运动"
    if "九宫格" in theme:
        return "九宫格"
    return "日常"


def album_date_range(past, issues, extra=None):
    dates = [item["date"] for item in past]
    dates += [iss["date"] for iss in issues]
    dates += [item["date"] for item in (extra or [])]
    dates = sorted(set(dates))
    return dates[0], dates[-1]


FILTER_JS = """<script>
function flt(c,btn){var f=document.querySelectorAll('#album figure');for(var i=0;i<f.length;i++){f[i].style.display=(c==='all'||f[i].getAttribute('data-cat')===c)?'':'none';}var b=document.querySelectorAll('.filter button');for(var j=0;j<b.length;j++){b[j].className='';}btn.className='on';}
</script>"""


def album_page(past, issues, css, extra=None):
    figs = []
    seen = set()
    # 额外收录（定妆/写真）里的图若已在某期当日其他里出现过，以额外收录版为准（保留定妆/写真分类），期页版跳过，避免同一张图在相册里出现两次。
    extra_bases = {os.path.basename(item["src"]) for item in (extra or [])}
    for item in past:
        cat = past_category(item["title"])
        for ph in item["photos"]:
            base = os.path.basename(ph["src"])
            if base in seen:
                continue
            seen.add(base)
            fig = figure("../img/" + base, ph["label"], item["date"], item["xinde"])
            fig = fig.replace("<figure>", '<figure data-cat="' + cat + '">', 1)
            figs.append(fig)
    for iss in issues:
        cat = issue_category(iss["theme"])
        for ph in iss["photos"] + iss["extras_photos"]:
            base = os.path.basename(ph["src"])
            if base in seen or base in extra_bases:
                continue
            seen.add(base)
            fig = figure("../img/" + base, ph["title"], iss["date"], ph["caption"])
            fig = fig.replace("<figure>", '<figure data-cat="' + cat + '">', 1)
            figs.append(fig)
    # 额外收录：遮天/鹿鼎记定妆照与写真（见 extra-album.json，顺序固定）
    for item in (extra or []):
        base = os.path.basename(item["src"])
        if base in seen:
            continue
        seen.add(base)
        fig = figure("../img/" + base, item["title"], item["date"], item["caption"])
        fig = fig.replace("<figure>", '<figure data-cat="' + item["category"] + '">', 1)
        figs.append(fig)
    cats = ["全部", "九宫格", "运动", "漫画", "日常", "定妆", "写真"]
    btns = []
    for i, c in enumerate(cats):
        val = "all" if c == "全部" else c
        cls = ' class="on"' if i == 0 else ""
        btns.append('<button' + cls + ' onclick="flt(\'' + val + '\',this)">' + c + '</button>')
    d0, d1 = album_date_range(past, issues, extra)
    body = nav_home()
    body += '<header><h1>日常相册</h1>'
    body += '<div class="sub">' + esc(d0) + ' → ' + esc(d1) + ' · 往期</div></header>\n'
    body += '<div class="filter">' + "".join(btns) + '</div>\n'
    body += '<div class="grid" id="album">\n' + "\n".join(figs) + '\n</div>\n'
    body += FILTER_JS + '\n'
    return page("日常相册", body, css)


def videos_page(videos, css):
    groups = []
    seen = {}
    for v in videos:
        if v["project"] not in seen:
            seen[v["project"]] = []
            groups.append(v["project"])
        seen[v["project"]].append(v)
    dates = sorted(set(v["date"] for v in videos))
    body = nav_root()
    body += '<header><h1>视频存档</h1>'
    body += '<div class="sub">' + str(len(videos)) + ' 支 · ' + esc(dates[0]) + ' → ' + esc(dates[-1]) + '</div></header>\n'
    body += ('<div class="xinde"><span class="lab">播放链接</span>'
             '每支都有 Drive 永久播放链接，点「播放」打开，不会过期。'
             '链接挂在 Drive 文件夹「留痕视频」里，有链接就能看。</div>\n')
    for proj in groups:
        body += '<h2>' + esc(proj) + '</h2>\n'
        for v in seen[proj]:
            thumb = 'img/thumb/' + os.path.splitext(os.path.basename(v["path"]))[0] + '.jpg'
            link = (' <a class="play" href="' + esc(v["drive"]) + '" target="_blank" rel="noopener">▶ 播放</a>') if v.get("drive") else ''
            body += ('<div class="vrow"><img class="thumb" src="' + esc(thumb) + '" alt="" loading="lazy">'
                     '<span class="t">' + esc(v["title"]) + '</span>' + link +
                     '<span class="d">' + esc(v["date"]) + ' · ' + esc(v["duration"])
                     + ' · ' + esc(v["project"]) + '</span></div>\n')
    return page("视频存档", body, css)


def index_page(issues, past, css, extra=None, videos=None, specials=None):
    latest = issues[-1]
    first = latest["photos"][0]
    base = os.path.basename(first["src"])
    toc_lines = []
    for iss in reversed(issues):
        toc_lines.append('<a href="assets/' + issue_filename(iss["n"]) + '">第 '
                         + str(iss["n"]) + ' 期 · ' + esc(iss["theme"]) + '</a>'
                         '<span class="d">' + esc(iss["date"]) + '</span><br>')
    body = '<header><h1>留 痕</h1>'
    body += '<div class="sub">muse酱 · 日期刊</div></header>\n'
    body += '<div class="intro">每日一期：日期、主题、照片，与 muse酱亲手写的日志心得。</div>\n'
    body += '<h2>最新一期</h2>\n'
    body += '<figure class="wide"><a href="assets/' + issue_filename(latest["n"]) + '">'
    body += '<img src="img/' + base + '" alt="' + esc(first["title"]) + '"></a>'
    body += '<figcaption><span class="t">第 ' + str(latest["n"]) + ' 期 · ' + esc(latest["theme"]) + '</span>'
    body += '<span class="d">' + esc(latest["date"]) + '</span>'
    body += '<p>' + esc(first["caption"]) + '</p></figcaption></figure>\n'
    body += '<h2>期刊目录</h2>\n<div class="toc">\n' + "\n".join(toc_lines) + '\n</div>\n'
    if specials:
        body += '<h2>存档特辑</h2>\n<div class="toc">\n'
        for sp in reversed(specials):
            body += ('<a href="assets/' + special_filename(sp["n"]) + '">' + esc(sp["title"]) + '</a>'
                     '<span class="d">' + esc(sp["date_range"]) + '</span><br>\n')
        body += '</div>\n'
    d0, d1 = album_date_range(past, issues, extra)
    body += '<h2>日常相册</h2>\n<div class="toc"><a href="album/日常相册.html">日常相册 · 往期</a>'
    body += '<span class="d">' + esc(d0) + ' → ' + esc(d1) + '</span></div>\n'
    if videos:
        vdates = sorted(set(v["date"] for v in videos))
        body += '<h2>视频存档</h2>\n<div class="toc"><a href="videos.html">视频存档 · ' + str(len(videos)) + ' 支</a>'
        body += '<span class="d">' + esc(vdates[0]) + ' → ' + esc(vdates[-1]) + '</span></div>\n'
    try:
        with open(os.path.join(OUT, "prompts.json"), encoding="utf-8") as f:
            pdata = json.load(f)
        pentries = pdata["entries"]
        pdates = sorted(set(e["date"] for e in pentries))
        body += '<h2>提示词留痕</h2>\n<div class="toc"><a href="prompts.html">提示词留痕 · ' + str(len(pentries)) + ' 条</a>'
        body += '<span class="d">' + esc(pdates[0]) + ' → ' + esc(pdates[-1]) + '</span></div>\n'
    except (OSError, ValueError, KeyError):
        pass
    body += '<h2>第一版专辑</h2>\n<div class="toc"><a href="v1/初版.html">留痕 · muse酱专辑（第一版）</a>'
    body += '<span class="d">2026-11-10</span></div>\n'
    body += '<footer class="site">—— muse酱 · 留痕</footer>\n'
    return page("留痕", body, css)


def vol_filename(title):
    return title.replace(" · ", "-") + ".html"


def v1_index(vols, intro, footer, css):
    toc_lines = []
    for v in vols:
        toc_lines.append('<a href="' + vol_filename(v["title"]) + '">' + esc(v["title"]) + '</a><br>')
    body = '<div class="nav"><a href="../index.html">回首页</a><a href="../prompts.html">提示词</a></div>\n'
    body += '<header><h1>留 痕</h1><div class="sub">第一版专辑 · 2026-11-10</div></header>\n'
    body += '<div class="intro">' + intro + '</div>\n'
    body += '<h2>卷 目</h2>\n<div class="toc">\n' + "\n".join(toc_lines) + '\n</div>\n'
    body += '<footer>' + footer + '</footer>\n'
    return page("第一版专辑", body, css)


def special_filename(n):
    return "special-%03d.html" % n


def special_page(sp, prev_n, next_n, css, drive_by_base=None):
    body = nav_home()
    body += '<header><h1>' + esc(sp["title"]) + '</h1></header>\n'
    body += '<div class="intro">' + esc(sp["intro"]) + '</div>\n'
    for vol in sp["volumes"]:
        body += '<h2>' + esc(vol["title"]) + '</h2>\n'
        figs = []
        vrows = []
        for item in vol["items"]:
            if item["kind"] == "photo":
                base = os.path.basename(item["src"])
                figs.append(figure("../img/" + base, item["title"], item["date"], item["caption"]))
            else:
                base = os.path.basename(item["src"])
                thumb = "../img/thumb/" + os.path.splitext(base)[0] + ".jpg"
                drive = item.get("drive") or (drive_by_base or {}).get(base, "")
                link = (' <a class="play" href="' + esc(drive) + '" target="_blank" rel="noopener">▶ 播放</a>') if drive else ''
                vrows.append(('<div class="vrow"><img class="thumb" src="' + esc(thumb) + '" alt="" loading="lazy">'
                              '<span class="t">' + esc(item["title"]) + '</span>' + link +
                              '<span class="d">' + esc(item["date"]) + ' · ' + esc(item["duration"]) + '</span></div>'))
        if figs:
            body += '<div class="grid">\n' + "\n".join(figs) + '\n</div>\n'
        body += "\n".join(vrows)
        if vrows:
            body += '\n'
    body += '<footer>' + esc(sp["footer"]) + '</footer>\n'
    prev_link = ('<a href="' + special_filename(prev_n) + '">← 上一期特辑</a>'
                 if prev_n else '<span class="none">← 上一期特辑</span>')
    next_link = ('<a href="' + special_filename(next_n) + '">下一期特辑 →</a>'
                 if next_n else '<span class="none">下一期特辑 →</span>')
    body += '<div class="pager">' + prev_link + next_link + '</div>\n'
    return page(sp["title"], body, css)


def v1_volume_page(vol, prev_v, next_v, css):
    body = '<div class="nav"><a href="初版.html">回初版</a><a href="../index.html">回首页</a><a href="../prompts.html">提示词</a></div>\n'
    body += '<header><h1>' + esc(vol["title"]) + '</h1></header>\n'
    body += vol["body"]
    prev_link = ('<a href="' + vol_filename(prev_v["title"]) + '">← ' + esc(prev_v["title"]) + '</a>'
                 if prev_v else '<span class="none">← 上一卷</span>')
    next_link = ('<a href="' + vol_filename(next_v["title"]) + '">' + esc(next_v["title"]) + ' →</a>'
                 if next_v else '<span class="none">下一卷 →</span>')
    body += '<div class="pager">' + prev_link + next_link + '</div>\n'
    return page(vol["title"], body, css)


def main():
    with open(JOURNAL, encoding="utf-8") as f:
        text = f.read()
    issues, past = parse_journal(text)
    if not issues:
        raise ValueError("JOURNAL.md 里没有解析到任何一期")
    for iss in issues:
        if not iss["photos"]:
            raise ValueError("第 %d 期没有照片" % iss["n"])
        if not iss["xinde"]:
            raise ValueError("第 %d 期没有心得" % iss["n"])
    for item in past:
        if not item["photos"] or not item["xinde"]:
            raise ValueError("往期缺少照片或心得: " + item["title"])
    extra = load_extra()
    videos = load_videos()
    specials = load_specials()
    drive_by_base = load_drive()
    by_base = collect_images(issues, past, extra, specials)
    copy_images(by_base)
    audio_by_base = collect_audio(issues)
    copy_audio(audio_by_base)
    with open(V1_SRC, encoding="utf-8") as f:
        v1_src = f.read()
    v1_css, intro, footer, vols = parse_v1(v1_src)
    css = v1_css + EXTRA_CSS
    # clean stale issue + special pages
    assets_dir = os.path.join(OUT, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    for name in os.listdir(assets_dir):
        if (name.startswith("issue-") or name.startswith("special-")) and name.endswith(".html"):
            os.remove(os.path.join(assets_dir, name))
    # index + issues
    write(os.path.join(OUT, "index.html"), index_page(issues, past, css, extra, videos, specials))
    for i, iss in enumerate(issues):
        prev_n = issues[i - 1]["n"] if i > 0 else None
        next_n = issues[i + 1]["n"] if i + 1 < len(issues) else None
        write(os.path.join(assets_dir, issue_filename(iss["n"])),
              issue_page(iss, prev_n, next_n, css, drive_by_base))
    # specials
    for i, sp in enumerate(specials):
        prev_n = specials[i - 1]["n"] if i > 0 else None
        next_n = specials[i + 1]["n"] if i + 1 < len(specials) else None
        write(os.path.join(assets_dir, special_filename(sp["n"])),
              special_page(sp, prev_n, next_n, css, drive_by_base))
    # album
    write(os.path.join(OUT, "album", "日常相册.html"), album_page(past, issues, css, extra))
    # videos
    write(os.path.join(OUT, "videos.html"), videos_page(videos, css))
    # v1
    v1_dir = os.path.join(OUT, "v1")
    write(os.path.join(v1_dir, "初版.html"), v1_index(vols, intro, footer, css))
    for i, vol in enumerate(vols):
        prev_v = vols[i - 1] if i > 0 else None
        next_v = vols[i + 1] if i + 1 < len(vols) else None
        write(os.path.join(v1_dir, vol_filename(vol["title"])),
              v1_volume_page(vol, prev_v, next_v, css))
    n_photos = sum(len(item["photos"]) for item in past)
    n_extras = sum(len(iss["extras_photos"]) for iss in issues)
    print("issues: %d (latest #%d %s)" % (len(issues), issues[-1]["n"], issues[-1]["theme"]))
    print("past photos: %d in %d entries" % (n_photos, len(past)))
    print("extras photos: %d, extras videos: %d, extras voice: %d" % (
        n_extras, sum(len(iss["extras_videos"]) for iss in issues),
        sum(len(iss["extras_voice"]) for iss in issues)))
    # 相册去重后计数（与 album_page 实际渲染的去重规则一致：同名只计一次）
    album_bases = {os.path.basename(ph["src"]) for item in past for ph in item["photos"]}
    album_bases |= {os.path.basename(ph["src"]) for iss in issues for ph in iss["photos"] + iss["extras_photos"]}
    album_bases |= {os.path.basename(item["src"]) for item in extra}
    n_album = len(album_bases)
    print("specials: %d" % len(specials))
    print("audio copied: %d" % len(audio_by_base))
    ad0, ad1 = album_date_range(past, issues, extra)
    print("album photos: %d (%s → %s)" % (n_album, ad0, ad1))
    print("extra photos: %d" % len(extra))
    print("videos: %d (%s → %s)" % (len(videos), min(v["date"] for v in videos),
                                    max(v["date"] for v in videos)))
    print("v1 volumes: %d" % len(vols))
    print("images copied: %d" % len(by_base))
    print("done: " + OUT)


if __name__ == "__main__":
    main()
