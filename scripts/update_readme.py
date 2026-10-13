#!/usr/bin/env python3
"""每日把桃子ID指南(taozi55.com)公开页上的免费共享 Apple ID 写进 README 的 DAILY 区块。
只用标准库;账号与密码照来源页的打码显示,不公开明文。GitHub Actions 每天 0:00(北京)跑一次。"""
import re, html, datetime, urllib.request, urllib.parse, sys, os

SRC = "https://www.taozi55.com/gongxiang/"
README = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "README.md")
SINCE = datetime.date(2026, 10, 3)          # 仓库建立日,用来算「已运行天数」
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


def build(accounts, today):
    days = (today - SINCE).days
    lines = [
        f'{badge("更新", today.isoformat(), "fbbf24")} {badge("今日共享账号", f"{len(accounts)} 个", "f59e0b")} {badge("已自动更新", f"{days} 天", "0ea5e9")}',
        "",
        f"> 🍎 **{today.isoformat()} 已更新 · 今日 {len(accounts)} 个公开共享账号**(来源页每小时刷新,本表每天 0:00 同步一次)。",
        "> 账号和密码的完整内容在来源页点一下就能复制:**[桃子ID指南 · 免费共享账号](https://www.taozi55.com/gongxiang/)**;本仓库只保留打码版做备用入口,不公开明文,减少被爬虫批量登录导致的锁号。",
        "",
        "| 地区 | 账号(打码) | 密码 | 来源检测时间 |",
        "| --- | --- | --- | --- |",
    ]
    if accounts:
        for region, acc, t in accounts:
            lines.append(f"| {region} | `{acc}` | `••••••••` | {t} |")
    else:
        lines.append("| — | 今日来源页暂无可用账号 | — | — |")
    lines += [
        "",
        "想要能自己改密码、一人一号的独享账号:[桃子出海 · 苹果ID自助下单](https://www.taozi277.com/idshop)(美区、港区、日区等地区,付款后自动发货)。",
    ]
    return "\n".join(lines)


def main():
    today = datetime.datetime.now(TZ).date()
    try:
        accounts = parse(fetch(SRC))
    except Exception as e:                      # 来源页抓不到就只更新日期,不清空上次的表
        print("fetch failed:", e, file=sys.stderr)
        accounts = None
    src = open(README, encoding="utf-8").read()
    m = re.search(r"<!-- DAILY:START -->\n(.*?)\n<!-- DAILY:END -->", src, re.S)
    if not m:
        sys.exit("README 缺 DAILY 标记")
    if accounts is None:
        new = re.sub(r"\d{4}-\d{2}-\d{2}", today.isoformat(), m.group(1), count=2)
    else:
        new = build(accounts, today)
    out = src[:m.start(1)] + new + src[m.end(1):]
    if out != src:
        open(README, "w", encoding="utf-8").write(out)
        print("README updated:", len(accounts or []), "accounts")
    else:
        print("no change")


if __name__ == "__main__":
    main()
