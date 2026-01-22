<p>slを背景透過にしただけです。<br>
Win11にて、Wezterm+Nushell+starship環境でのみ検証しました。<br>
Wezterm.luaに以下の内容を追加してください<br>
---wezterm.lua<br>
config.window_background_opacity = 0.65<br>
<br>
config.colors = { <br>
background = "rgba(0,0,0,0.65)",<br>
}<br>
</p>

<video src="https://github.com/user-attachments/assets/aefb9199-7615-4f36-8a77-8e0c543370d4">|
