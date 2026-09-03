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
