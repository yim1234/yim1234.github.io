#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministic builder for the 留痕 (Liuhen) static site.

Reads ~/workspace/musejiang-journal/JOURNAL.md and
~/workspace/your_files/musejiang-album-20261110.html, regenerates
~/workspace/liuhen-site/ (this script's own directory).

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
import os
import re
import shutil

HOME = os.path.expanduser("~")
JOURNAL = os.path.join(HOME, "workspace/musejiang-journal/JOURNAL.md")
V1_SRC = os.path.join(HOME, "workspace/your_files/musejiang-album-20261110.html")
OUT = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(OUT, "img")

ISSUE_RE = re.compile(r"^### 第(\d+)期 · (\d{4}-\d{2}-\d{2}) · (.+?)\s*$")
PAST_RE = re.compile(r"^### 往期")
PHOTO_RE = re.compile(r"^- (.+?)：`([^`]+)`。配文：(.+)$")
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


def collect_images(issues, past):
    by_base = {}
    for iss in issues:
        for ph in iss["photos"]:
            base = os.path.basename(ph["src"])
            if base in by_base and by_base[base] != ph["src"]:
                raise ValueError("同名不同图: " + base)
            by_base[base] = ph["src"]
    for item in past:
        for ph in item["photos"]:
            base = os.path.basename(ph["src"])
            if base in by_base and by_base[base] != ph["src"]:
                raise ValueError("同名不同图: " + base)
            by_base[base] = ph["src"]
    return by_base


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
    return '<div class="nav"><a href="../index.html">回首页</a></div>\n'


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

def issue_filename(n):
    return "issue-%03d.html" % n


def figure(img_rel, title, date, caption):
    out = '<figure><a href="' + img_rel + '"><img src="' + img_rel + '" alt="' + esc(title) + '"></a>'
    out += '<figcaption><span class="t">' + esc(title) + '</span>'
    if date:
        out += '<span class="d">' + esc(date) + '</span>'
    out += '<p>' + esc(caption) + '</p></figcaption></figure>'
    return out


def issue_page(iss, prev_n, next_n, css):
    figs = []
    for ph in iss["photos"]:
        base = os.path.basename(ph["src"])
        figs.append(figure("../img/" + base, ph["title"], "", ph["caption"]))
    body = nav_home()
    body += '<header><h1>第 ' + str(iss["n"]) + ' 期</h1>'
    body += '<div class="sub">' + esc(iss["date"]) + ' · ' + esc(iss["theme"]) + '</div></header>\n'
    body += '<div class="grid">\n' + "\n".join(figs) + '\n</div>\n'
    body += '<div class="xinde"><span class="lab">心 得</span>' + esc(iss["xinde"]) + '</div>\n'
    if iss["beizhu"]:
        body += '<div class="note"><span class="lab">备 注</span>' + esc(iss["beizhu"]) + '</div>\n'
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


FILTER_JS = """<script>
function flt(c,btn){var f=document.querySelectorAll('#album figure');for(var i=0;i<f.length;i++){f[i].style.display=(c==='all'||f[i].getAttribute('data-cat')===c)?'':'none';}var b=document.querySelectorAll('.filter button');for(var j=0;j<b.length;j++){b[j].className='';}btn.className='on';}
</script>"""


def album_page(past, css):
    figs = []
    for item in past:
        cat = past_category(item["title"])
        for ph in item["photos"]:
            base = os.path.basename(ph["src"])
            fig = figure("../img/" + base, ph["label"], item["date"], item["xinde"])
            fig = fig.replace("<figure>", '<figure data-cat="' + cat + '">', 1)
            figs.append(fig)
    cats = ["全部", "九宫格", "运动", "漫画", "日常"]
    btns = []
    for i, c in enumerate(cats):
        val = "all" if c == "全部" else c
        cls = ' class="on"' if i == 0 else ""
        btns.append('<button' + cls + ' onclick="flt(\'' + val + '\',this)">' + c + '</button>')
    dates = sorted(set(item["date"] for item in past))
    body = nav_home()
    body += '<header><h1>日常相册</h1>'
    body += '<div class="sub">' + esc(dates[0]) + ' → ' + esc(dates[-1]) + ' · 往期</div></header>\n'
    body += '<div class="filter">' + "".join(btns) + '</div>\n'
    body += '<div class="grid" id="album">\n' + "\n".join(figs) + '\n</div>\n'
    body += FILTER_JS + '\n'
    return page("日常相册", body, css)


def index_page(issues, css):
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
    body += '<h2>日常相册</h2>\n<div class="toc"><a href="album/日常相册.html">日常相册 · 往期</a>'
    body += '<span class="d">2026-11-12 → 2026-11-15</span></div>\n'
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
    body = '<div class="nav"><a href="../index.html">回首页</a></div>\n'
    body += '<header><h1>留 痕</h1><div class="sub">第一版专辑 · 2026-11-10</div></header>\n'
    body += '<div class="intro">' + intro + '</div>\n'
    body += '<h2>卷 目</h2>\n<div class="toc">\n' + "\n".join(toc_lines) + '\n</div>\n'
    body += '<footer>' + footer + '</footer>\n'
    return page("第一版专辑", body, css)


def v1_volume_page(vol, prev_v, next_v, css):
    body = '<div class="nav"><a href="初版.html">回初版</a><a href="../index.html">回首页</a></div>\n'
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
    by_base = collect_images(issues, past)
    copy_images(by_base)
    with open(V1_SRC, encoding="utf-8") as f:
        v1_src = f.read()
    v1_css, intro, footer, vols = parse_v1(v1_src)
    css = v1_css + EXTRA_CSS
    # clean stale issue pages
    assets_dir = os.path.join(OUT, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    for name in os.listdir(assets_dir):
        if name.startswith("issue-") and name.endswith(".html"):
            os.remove(os.path.join(assets_dir, name))
    # index + issues
    write(os.path.join(OUT, "index.html"), index_page(issues, css))
    for i, iss in enumerate(issues):
        prev_n = issues[i - 1]["n"] if i > 0 else None
        next_n = issues[i + 1]["n"] if i + 1 < len(issues) else None
        write(os.path.join(assets_dir, issue_filename(iss["n"])),
              issue_page(iss, prev_n, next_n, css))
    # album
    write(os.path.join(OUT, "album", "日常相册.html"), album_page(past, css))
    # v1
    v1_dir = os.path.join(OUT, "v1")
    write(os.path.join(v1_dir, "初版.html"), v1_index(vols, intro, footer, css))
    for i, vol in enumerate(vols):
        prev_v = vols[i - 1] if i > 0 else None
        next_v = vols[i + 1] if i + 1 < len(vols) else None
        write(os.path.join(v1_dir, vol_filename(vol["title"])),
              v1_volume_page(vol, prev_v, next_v, css))
    n_photos = sum(len(item["photos"]) for item in past)
    print("issues: %d (latest #%d %s)" % (len(issues), issues[-1]["n"], issues[-1]["theme"]))
    print("past photos: %d in %d entries" % (n_photos, len(past)))
    print("v1 volumes: %d" % len(vols))
    print("images copied: %d" % len(by_base))
    print("done: " + OUT)


if __name__ == "__main__":
    main()
