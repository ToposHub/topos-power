# Topos Power

**中文** | [English](README.md)

Topos Power 是一个基于 PyQt6 的跨平台电源定时工具，支持：

- 定时关机
- 定时睡眠
- 仅关闭显示器
- 先关闭显示器再进入睡眠
- macOS 系统空闲关屏/睡眠参数读取与修改
- 倒计时期间阻止系统自动睡眠
- 环形倒计时进度、阶段时间线与轻量呼吸动画
- 中英文界面即时切换

## 界面预览

<p align="center">
  <img src="assets/screenshots/scheduled-shutdown.png" alt="定时关机界面" width="48%">
  <img src="assets/screenshots/scheduled-sleep.png" alt="定时睡眠界面" width="48%">
</p>

## 项目结构

```text
Topos Power/
├── src/topos_power/
│   ├── app.py                 # 应用入口
│   ├── config.py              # 应用名称与版本
│   ├── core/localization.py   # 中文/英文界面文案
│   ├── core/power_manager.py  # 跨平台系统电源能力
│   └── ui/                    # Qt 界面与样式
├── tests/                     # 自动化测试
├── pyproject.toml
└── requirements.txt
```

## 运行方式

### 方法一：一键启动

macOS：双击项目根目录中的 `run_topos.command` 即可启动。如果系统阻止执行，也可以在终端运行：

```bash
./run_topos.command
```

Windows：双击项目根目录中的 `run_topos.bat` 即可启动。

两个启动脚本都会优先使用项目中的 `.venv`，并自动处理 `src` 布局。

### 方法二：传统 Python 启动

```bash
cd "Topos Power"
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m topos_power
```

也可以安装命令行入口：

```bash
topos-power
```

## 界面语言

应用顶部右侧提供中文和 English 两种语言选择。选择会立即刷新界面，并保存在本机，下次启动时自动使用上次的语言。

## 许可证与版权

Copyright (C) 2026 ToposHub

Topos Power is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

本项目采用 GNU General Public License v3.0 or later（GPL-3.0-or-later）授权，完整协议见 [LICENSE](LICENSE)。项目按“现状”提供，不对适用性、稳定性或因使用本软件造成的任何损失作保证。

发布本项目的修改版或打包版时，请保留版权声明、许可证文本和第三方许可说明，并按照 GPL-3.0-or-later 提供对应源代码。

当前项目依赖 PyQt6。PyQt6 社区版本采用 GPLv3 授权；分发包含 PyQt6 的应用时，还必须遵守 PyQt6、Qt 及其他实际打包组件各自的许可证要求，详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

贡献代码前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

运行测试：

```bash
pytest
```

## macOS 权限说明

睡眠、关屏和修改 `pmset` 参数由 macOS 系统命令完成。首次使用时，系统可能要求输入管理员密码，锁屏操作还可能需要在“系统设置 → 隐私与安全性 → 自动化/辅助功能”中允许应用控制“系统事件”。

## 设计原则

电源操作与 Qt 界面分离，系统命令返回值会传回界面，避免命令失败时显示“已成功”。macOS 关屏使用 `pmset displaysleepnow`，不修改显示器伽马值。
