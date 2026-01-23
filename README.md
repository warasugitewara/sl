slを背景透過にしたPython版です。
私の技量不足により煙のアニメーションは断念しました
## 特徴
- weztermのANSI VTサポートで完全な背景透過を実現
- Windowsで `py sl.py` または `sl` コマンドで実行可能
- 本家slと同じアニメーション（機関車、荷台、車輪、煙）

## 環境
- Win11にて、Wezterm + Nushell + starship環境で検証
- Python 3.10.6以上

## セットアップ

### 1. weztermの設定 (wezterm.lua)

```lua
config.window_background_opacity = 0.65

config.colors = {
    background = "#1a1a1a",
    tab_bar = {
        inactive_tab_edge = "none",
    },
}
```

### 2. Nushellの設定 (config.nu)

```nu
alias sl = py C:\Users\waras\sl\sl.py
```

## 実行

```bash
sl
```

## 元のC版について

詳細は [オリジナルREADME](./README.ja.md) を参照してください。

---

Original sl: Copyright 1993,1998,2014 Toyoda Masashi (mtoyoda@acm.org)

Python版 - 背景透過実装: warasugitewara


