# Topos Power

Topos Power 是一个基于 PyQt6 的跨平台电源定时工具，支持：

- 定时关机
- 定时睡眠
- 仅关闭显示器
- 先关闭显示器再进入睡眠
- macOS 系统空闲关屏/睡眠参数读取与修改
- 倒计时期间阻止系统自动睡眠

## 项目结构

```text
Topos Power/
├── src/topos_power/
│   ├── app.py                 # 应用入口
│   ├── config.py              # 应用名称与版本
│   ├── core/power_manager.py  # 跨平台系统电源能力
│   └── ui/                    # Qt 界面与样式
├── tests/                     # 自动化测试
├── pyproject.toml
└── requirements.txt
```

## 本地运行

```bash
cd "Topos Power"
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m topos_power
```

macOS 也可以双击项目根目录中的 `run_topos.command` 启动；Windows 使用 `run_topos.bat`。两个脚本都会优先使用项目中的 `.venv`，并自动处理 `src` 布局。

也可以安装命令行入口：

```bash
topos-power
```

运行测试：

```bash
pytest
```

## macOS 权限说明

睡眠、关屏和修改 `pmset` 参数由 macOS 系统命令完成。首次使用时，系统可能要求输入管理员密码，锁屏操作还可能需要在“系统设置 → 隐私与安全性 → 自动化/辅助功能”中允许应用控制“系统事件”。

## 设计原则

电源操作与 Qt 界面分离，系统命令返回值会传回界面，避免命令失败时显示“已成功”。macOS 关屏使用 `pmset displaysleepnow`，不修改显示器伽马值。
