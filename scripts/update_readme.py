#!/usr/bin/env python3
"""每日把桃子ID指南(taozi55.com)公开页上的免费共享 Apple ID 写进 README 的 DAILY 区块。
只用标准库;账号与密码照来源页的打码显示,不公开明文。GitHub Actions 约每 3 小时跑一次,账号表没变就不改 README(不为刷时间提交)。"""
import re, html, datetime, urllib.request, urllib.parse, sys, os

SRC = "https://www.taozi55.com/gongxiang/"
README = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "README.md")
SINCE = datetime.date(2026, 10, 4)          # 仓库建立日(北京时间 10-04 02:46),用来算「已运行天数」
TZ = datetime.timezone(datetime.timedelta(hours=8))
# 来源页的地区名 → (这里的叫法, 来源站的地区页)。来源站只在该地区当时有号时才有地区页,和这里「有号才出小标题」同一个条件。
REGIONS = {
    "美国": ("美区", "meiqu"), "香港": ("港区", "gangqu"), "台湾": ("台区", "taiqu"),
    "日本": ("日区", "riqu"), "韩国": ("韩区", "hanqu"), "中国大陆": ("国区", None),
}
ORDER = ["美国", "香港", "台湾", "日本", "韩国"]      # 其余地区按账号数排在后面,未标注地区放最后
BLANK = "未标注地区"


def groups(accounts):
    """按地区分组,保持来源页里的先后;不猜地区,来源没标的归「未标注地区」。"""
    g = {}
    for region, acc, t in accounts:
        g.setdefault(region or BLANK, []).append((acc, t))
    rest = sorted((r for r in g if r not in ORDER and r != BLANK), key=lambda r: -len(g[r]))
    return [(r, g[r]) for r in ORDER + rest + [BLANK] if r in g]


def title(region):
    return REGIONS[region][0] if region in REGIONS else region


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
        mix = " · ".join(f"{title(r)} {len(v)}" for r, v in groups(accounts))
        head = f"> 🍎 **{stamp} 更新 · 当前 {len(accounts)} 个公开共享账号**({mix};来源页每小时刷新,本表约每 3 小时自动同步)。"
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
    ]
    if not accounts:
        lines += ["", "| 地区 | 账号(打码) | 密码 | 来源检测时间 |", "| --- | --- | --- | --- |", "| — | 来源页暂时没有可用账号 | — | — |"]
    for region, rows in groups(accounts):
        name = title(region)
        slug = REGIONS.get(region, (None, None))[1]
        if region == BLANK:
            lines += ["", f"### 未标注地区的共享 Apple ID({len(rows)} 个)", "", "来源没有写明地区,登录后看 App Store 显示的是哪个地区的商店。"]
        else:
            link = f"https://www.taozi55.com/gongxiang/{slug}.html" if slug else SRC
            lines += ["", f"### {name} Apple ID 共享账号({region},{len(rows)} 个)", "", f"完整账号和密码:[{name}免费共享 Apple ID]({link})"]
        lines += ["", "| 地区 | 账号(打码) | 密码 | 来源检测时间 |", "| --- | --- | --- | --- |"]
        for acc, t in rows:
            lines.append(f"| {region} | `{acc}` | `••••••••` | {t} |")
    return "\n".join(lines)


def table(block):
    """只取账号表部分比较:时间戳每次都变,表没变就不算更新。分组后从第一个地区小标题算起。"""
    i = block.find("\n### ")
    if i < 0:
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
