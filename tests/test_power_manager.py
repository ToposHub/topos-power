from types import SimpleNamespace

from topos_power.core import power_manager
from topos_power.core.power_manager import PowerManager


def test_parse_active_pmset_settings(monkeypatch):
    monkeypatch.setattr(power_manager.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(
        power_manager.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0,
            stdout=(
                " sleep 180 (sleep prevented by powerd)\n"
                " displaysleep 30\n"
                " disksleep 10\n"
            ),
            stderr="",
        ),
    )

    assert PowerManager.get_system_idle_settings() == (30, 180)


def test_screen_off_prefers_pmset(monkeypatch):
    calls = []
    monkeypatch.setattr(power_manager.platform, "system", lambda: "Darwin")

    def fake_run(*args, **kwargs):
        calls.append(args[0])
        return SimpleNamespace(returncode=0, stdout=b"", stderr=b"")

    monkeypatch.setattr(power_manager.subprocess, "run", fake_run)

    assert PowerManager.screen_off() is True
    assert calls == [["pmset", "displaysleepnow"]]


def test_idle_settings_reject_negative_values(monkeypatch):
    monkeypatch.setattr(power_manager.platform, "system", lambda: "Darwin")
    assert PowerManager.set_system_idle_settings(-1, 180) is False
    assert PowerManager.set_system_idle_settings(30, -1) is False


def test_parse_windows_idle_settings(monkeypatch):
    monkeypatch.setattr(power_manager.platform, "system", lambda: "Windows")

    def fake_run(command, **kwargs):
        if command[-1] == "VIDEOIDLE":
            seconds = "0x0000001e"
        else:
            seconds = "0x00000078"
        return SimpleNamespace(
            returncode=0,
            stdout=f"Current AC Power Setting Index: {seconds}\n",
            stderr="",
        )

    monkeypatch.setattr(power_manager.subprocess, "run", fake_run)
    assert PowerManager.get_system_idle_settings() == (1, 2)


def test_parse_chinese_windows_idle_setting_label(monkeypatch):
    monkeypatch.setattr(power_manager.platform, "system", lambda: "Windows")
    monkeypatch.setattr(
        power_manager.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0,
            stdout="当前交流电源设置索引: 0x0000003c\n",
            stderr="",
        ),
    )

    assert PowerManager._get_windows_timeout("SUB_VIDEO", "VIDEOIDLE") == 1


def test_set_windows_idle_settings_updates_ac_and_dc(monkeypatch):
    monkeypatch.setattr(power_manager.platform, "system", lambda: "Windows")
    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(power_manager.subprocess, "run", fake_run)
    assert PowerManager.set_system_idle_settings(30, 120) is True
    assert calls == [
        ["powercfg", "/change", "monitor-timeout-ac", "30"],
        ["powercfg", "/change", "monitor-timeout-dc", "30"],
        ["powercfg", "/change", "standby-timeout-ac", "120"],
        ["powercfg", "/change", "standby-timeout-dc", "120"],
    ]
