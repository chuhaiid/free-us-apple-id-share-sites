#!/usr/bin/env python3
"""每日把桃子ID指南(taozi55.com)公开页上的免费共享 Apple ID 写进 README 的 DAILY 区块。
只用标准库;账号与密码照来源页的打码显示,不公开明文。GitHub Actions 约每 3 小时跑一次,账号表没变就不改 README(不为刷时间提交)。"""
import re, html, datetime, urllib.request, urllib.parse, sys, os

SRC = "https://www.taozi55.com/gongxiang/"
README = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "README.md")
SINCE = datetime.date(2026, 10, 4)          # 仓库建立日(北京时间 10-04 02:46),用来算「已运行天数」
TZ = datetime.timezone(datetime.timedelta(hours=8))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (free-us-apple-id-share-sites daily update)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


def parse(page):
    """返回 [(地区, 打码账号, 来源检测时间)],来源页本身已把账号与密码打码。"""
    out = []
    for li in re.findall(r'<li class="acc">(.*?)</li>', page, re.S):
        tag = re.search(r'class="acc-tag">([^<]*)<', li)
        acc = re.search(r'class="acc-k">账号</span><span class="acc-v">([^<]*)<', li)
        foot = re.search(r'class="acc-foot">([^<]*)<', li)
        if not acc:
            continue
        out.append((html.unescape(tag.group(1)).strip() if tag else "未标注地区",
                    html.unescape(acc.group(1)).strip(),
                    html.unescape(foot.group(1)).replace("来源检测时间", "").strip() if foot else ""))
    return out


def badge(label, value, color):
    q = lambda s: urllib.parse.quote(s.replace("-", "--").replace("_", "__"), safe="")
    return f"![{label}](https://img.shields.io/badge/{q(label)}-{q(value)}-{color})"


def build(accounts, now):
    days = (now.date() - SINCE).days
    stamp = now.strftime("%Y-%m-%d %H:%M")
    if accounts:
        count = badge("当前共享账号", f"{len(accounts)} 个", "f59e0b")
        head = f"> 🍎 **{stamp} 更新 · 当前 {len(accounts)} 个公开共享账号**(来源页每小时刷新,本表约每 3 小时自动同步)。"
    else:                                       # 来源页没号时如实写「暂缺」,不保留旧账号充数
        count = badge("当前共享账号", "暂缺", "lightgrey")
        head = f"> 🍎 **来源页 {now:%H:%M} 暂时没有可用账号**,一般几小时内恢复;急用先试下方共享站列表。"
    lines = [
        f'{badge("更新", stamp, "fbbf24")} {count} {badge("已运行", f"{days} 天", "0ea5e9")}',
        "",
        head,
        "> 账号和密码的完整内容在来源页点一下就能复制:**[桃子ID指南 · 免费共享账号](https://www.taozi55.com/gongxiang/)**;本仓库只保留打码版做备用入口,不公开明文,减少被爬虫批量登录导致的锁号。",
        "",
        "想要能自己改密码、一人一号的独享账号:[桃子出海 · 苹果ID自助下单](https://www.taozi277.com/idshop)(美区、港区、日区等地区,付款后自动发货)。",
        "",
        "| 地区 | 账号(打码) | 密码 | 来源检测时间 |",
        "| --- | --- | --- | --- |",
    ]
    if accounts:
        for region, acc, t in accounts:
            lines.append(f"| {region} | `{acc}` | `••••••••` | {t} |")
    else:
        lines.append("| — | 来源页暂时没有可用账号 | — | — |")
    return "\n".join(lines)


def table(block):
    """只取账号表部分比较:时间戳每次都变,表没变就不算更新。"""
    i = block.find("| 地区 |")
    return block[i:] if i >= 0 else block


def main():
    now = datetime.datetime.now(TZ)
    try:
        accounts = parse(fetch(SRC))
    except Exception as e:                      # 来源页抓不到就不动 README,不改日期装新
        print("fetch failed, README unchanged:", e, file=sys.stderr)
        return
    src = open(README, encoding="utf-8").read()
    m = re.search(r"<!-- DAILY:START -->\n(.*?)\n<!-- DAILY:END -->", src, re.S)
    if not m:
        sys.exit("README 缺 DAILY 标记")
    new = build(accounts, now)
    if table(new) == table(m.group(1)):
        print("table unchanged, README not touched")
        return
    out = src[:m.start(1)] + new + src[m.end(1):]
    if out != src:
        open(README, "w", encoding="utf-8").write(out)
        print("README updated:", len(accounts), "accounts")
    else:
        print("no change")


if __name__ == "__main__":
    main()
