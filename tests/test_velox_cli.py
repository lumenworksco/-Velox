"""Tests for the velox CLI and the terminal kill-switch request channel."""

import json
from datetime import datetime, timedelta

import pytest

import velox
from oms import kill_switch as ks


@pytest.fixture
def request_file(tmp_path, monkeypatch):
    path = tmp_path / "kill_request.json"
    monkeypatch.setattr(ks, "_REQUEST_FILE", str(path))
    return path


def test_kill_request_roundtrip(request_file):
    assert ks.consume_kill_request() is None
    ks.request_kill("fat finger")
    assert json.loads(request_file.read_text())["reason"] == "fat finger"
    assert ks.consume_kill_request() == "fat finger"
    assert not request_file.exists()          # consumed exactly once
    assert ks.consume_kill_request() is None


def test_corrupt_kill_request_still_kills(request_file):
    request_file.write_text("{not json")
    assert ks.consume_kill_request() == "manual (velox kill)"
    assert not request_file.exists()


def test_kill_command_requires_running_bot_or_force(request_file, monkeypatch, capsys):
    monkeypatch.setattr(velox, "_running_pid", lambda: None)
    monkeypatch.setattr(velox, "_heartbeat", lambda: None)
    assert velox.main(["kill", "--yes"]) == 1
    assert not request_file.exists()
    assert velox.main(["kill", "--yes", "--force"]) == 0
    assert request_file.exists()


def test_kill_command_aborts_without_confirmation(request_file, monkeypatch):
    monkeypatch.setattr(velox, "_running_pid", lambda: 123)
    monkeypatch.setattr("builtins.input", lambda _="": "no")
    assert velox.main(["kill"]) == 1
    assert not request_file.exists()


@pytest.mark.parametrize("age,expected", [(10, 0), (10_000, 1)])
def test_health_uses_heartbeat_age(tmp_path, monkeypatch, age, expected):
    hb = tmp_path / "heartbeat.json"
    hb.write_text(json.dumps({"timestamp": (datetime.now() - timedelta(seconds=age)).isoformat()}))
    monkeypatch.setattr(velox, "HEARTBEAT_FILE", hb)
    assert velox.main(["health"]) == expected


def test_health_fails_without_heartbeat(tmp_path, monkeypatch):
    monkeypatch.setattr(velox, "HEARTBEAT_FILE", tmp_path / "missing.json")
    assert velox.main(["health"]) == 1


def test_backtest_rejects_unknown_strategy(capsys):
    assert velox.main(["backtest", "--strategy", "bogus"]) == 2
    assert "Unknown strategy" in capsys.readouterr().out


def test_backtest_runs_on_sample_data(capsys):
    assert velox.main(["backtest", "--strategy", "ma_crossover", "--symbols", "AAPL"]) == 0
    out = capsys.readouterr().out
    assert "Baseline backtest" in out and "AAPL" in out


def test_ago_formatting():
    assert velox._ago(30) == "30s ago"
    assert velox._ago(600) == "10m ago"
    assert velox._ago(7200 * 2) == "4h ago"
    assert velox._ago(86400 * 5) == "5d ago"


def test_passthrough_commands_forward_leading_options(monkeypatch):
    seen = {}
    monkeypatch.setattr(velox, "cmd_run", lambda a: seen.setdefault("extra", a.extra) and 0)
    assert velox.main(["run", "--live", "--diagnose"]) == 0
    assert seen["extra"] == ["--live", "--diagnose"]


def test_non_passthrough_commands_reject_unknown_options(capsys):
    with pytest.raises(SystemExit):
        velox.main(["status", "--bogus"])
