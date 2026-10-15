import json
from unittest.mock import Mock

import pytest

from seo import service as seo
from tools import seo_registry


@pytest.fixture
def setup(tmp_path, monkeypatch):
    config = tmp_path / 'DAILY_SEO.md'
    config.write_text('# Daily SEO\n\nenabled: false\npairs_per_day: 1\ntimezone: America/Chicago\n')
    monkeypatch.setattr(seo, 'CONFIG', config)
    monkeypatch.setattr(seo, 'STATE', tmp_path / 'state.json')
    monkeypatch.setattr(seo, 'OUTPUT', tmp_path / 'drafts')
    monkeypatch.setattr(seo.emergency, 'active', lambda: False)
    keywords = tmp_path / 'keywords.md'
    keywords.write_text('| ID | State | Topic | English | Spanish | Priority | Status |\n| --- | --- | --- | --- | --- | --- | --- |\n| KW-001 | TX | Brakes | air brakes | frenos | P1 | active |\n| KW-002 | TX | Inspection | inspection | inspección | P2 | active |\n')
    rules = tmp_path / 'rules.md'
    rules.write_text('Verify sources.')
    monkeypatch.setitem(seo_registry.FILES, 'cdl_keywords', keywords)
    monkeypatch.setitem(seo_registry.FILES, 'google_seo_rules', rules)
    monkeypatch.setattr(seo.service, 'start', Mock())
    worker = Mock(return_value={'en': '# English', 'es': '# Español'})
    monkeypatch.setattr(seo, 'supervise', worker)
    return worker


def test_restart_and_quota_do_not_repeat(setup):
    seo.command('start 1')
    seo.DailySEO().tick()
    seo.DailySEO().tick()
    assert setup.call_count == 1
    assert len(list(seo.OUTPUT.rglob('*.md'))) == 2
    seo.command('set 2')
    seo.DailySEO().tick()
    assert setup.call_count == 2
    assert seo.load()['used'] == ['KW-001', 'KW-002']


def test_paused_and_emergency_do_no_work(setup, monkeypatch):
    seo.DailySEO().tick()
    assert not setup.called
    seo.command('start')
    monkeypatch.setattr(seo.emergency, 'active', lambda: True)
    seo.DailySEO().tick()
    assert not setup.called
    with pytest.raises(ValueError, match='Emergency'):
        seo.command('start')


def test_failure_is_saved_without_retry(setup):
    setup.side_effect = RuntimeError('offline')
    seo.command('start')
    seo.DailySEO().tick()
    seo.DailySEO().tick()
    assert setup.call_count == 1
    assert 'offline' in seo.command('status')


def test_stop_during_generation_does_not_save(setup):
    def stop(*args, **kwargs):
        seo.command('stop')
        return {'en': '# English', 'es': '# Spanish'}
    setup.side_effect = stop
    seo.command('start')
    seo.DailySEO().tick()
    assert not seo.OUTPUT.exists()


def test_settings_invalid_count_is_not_written(setup):
    before = seo.CONFIG.read_text()
    with pytest.raises(ValueError):
        seo.command('start 0')
    assert seo.CONFIG.read_text() == before


def test_keyword_crud_preserves_fields_and_table(setup):
    def call(data):
        return seo_registry.run_seo_registry(json.dumps(data), 'cdl_keywords')
    call({'action': 'update', 'id': 'KW-001', 'priority': 'P3'})
    row = next(r for r in seo.keywords() if r['id'] == 'KW-001')
    assert row['english'] == 'air brakes'
    assert row['priority'] == 'P3'
    call({'action': 'create', 'state': 'TX', 'topic': 'New', 'english': 'New', 'spanish': 'Nuevo'})
    assert seo.keywords()[-1]['id'] == 'KW-001'
    assert 'KW-003' in call({'action': 'list'})
    lines = seo_registry.FILES['cdl_keywords'].read_text().splitlines()
    assert lines[1].startswith('| ---')
    call({'action': 'delete', 'id': 'KW-003'})
    assert 'KW-003' not in call({'action': 'list'})


def test_interrupted_slot_is_reported_after_restart(setup):
    from datetime import datetime
    from zoneinfo import ZoneInfo
    today = datetime.now(ZoneInfo('America/Chicago')).date().isoformat()
    seo.save({'days': {today: {'1': {'keyword': 'KW-001', 'status': 'running'}}},
              'used': ['KW-001'], 'status': 'Drafting'})
    seo.command('start')
    seo.DailySEO().tick()
    assert not setup.called
    assert seo.load()['days'][today]['1']['status'] == 'interrupted'
    assert 'interrupted' in seo.command('status')


def test_console_controls_work_in_plan_mode(setup):
    from commands import run
    from store import store
    old = store.get('mode')
    try:
        store['mode'] = 'plan'
        assert 'SEO enabled' in run('/seo start 2')['text']
        result = run('/cdl_keywords {"action":"update","id":"KW-001","priority":"P2"}')
        assert result['kind'] == 'text'
    finally:
        store['mode'] = old


def test_content_title_persists_and_is_used_in_brief(setup):
    seo.command('title Texas CDL air brakes')
    assert seo.settings()['content_title'] == 'Texas CDL air brakes'
    seo.command('start')
    seo.DailySEO().tick()
    assert setup.call_args.args[1]['content_title'] == 'Texas CDL air brakes'
    assert seo.load()['article_title'] == 'English'
    assert 'Texas CDL air brakes' in seo.command('status')


def test_tmux_title_targets_only_current_pane(monkeypatch):
    monkeypatch.setenv('TMUX_PANE', '%42')
    run = Mock()
    monkeypatch.setattr(seo.subprocess, 'run', run)
    seo.show_title('A1 | Texas CDL | Air brakes')
    assert run.call_args.args[0] == ['tmux', 'rename-window', '-t', '%42', 'A1 | Texas CDL | Air brakes']


def test_title_and_keywords_start_parameters_control_topic(setup):
    seo.command(json.dumps({'action': 'start', 'content_title': 'Texas air brakes',
                            'keywords': ['air brake inspection', 'air brake practice'],
                            'pairs_per_day': 2}))
    seo.DailySEO().tick()
    payload = setup.call_args.args[1]
    assert payload['content_title'] == 'Texas air brakes'
    assert payload['keyword']['english'] == 'air brake inspection'
    assert payload['keyword']['topic'] == 'Texas air brakes'
    seo.DailySEO().tick()
    assert setup.call_args.args[1]['keyword']['english'] == 'air brake practice'
    seo.DailySEO().tick()
    assert setup.call_count == 2


def test_clear_keywords_restores_registry(setup):
    seo.command('keywords custom keyword')
    assert seo.settings()['keywords'] == 'custom keyword'
    seo.command('keywords')
    assert seo.settings()['keywords'] == ''
    seo.command('start')
    seo.DailySEO().tick()
    assert setup.call_args.args[1]['keyword']['id'] == 'KW-001'


def test_default_author_and_timestamp_on_both_drafts(setup):
    from datetime import datetime
    seo.command('start')
    seo.DailySEO().tick()
    files = list(seo.OUTPUT.rglob('*.md'))
    assert len(files) == 2
    timestamps = []
    for path in files:
        metadata = path.read_text().split('---')[1]
        fields = dict(line.split(': ', 1) for line in metadata.strip().splitlines())
        assert json.loads(fields['author']) == 'Sergio'
        timestamps.append(json.loads(fields['created_at']))
        assert datetime.fromisoformat(timestamps[-1]).utcoffset() is not None
    assert timestamps[0] == timestamps[1]


def test_author_parameter_and_help(setup):
    seo.command('author Ana Pérez')
    assert seo.settings()['author'] == 'Ana Pérez'
    seo.command('{"action":"set","author":"Sergio"}')
    assert seo.settings()['author'] == 'Sergio'
    with pytest.raises(ValueError):
        seo.command('author')
    for parameter in ('author', 'title', 'keywords', 'pairs/day'):
        assert parameter in seo.command('help')


def test_startup_lists_seo_parameters(setup, monkeypatch, capsys):
    import cli
    monkeypatch.setattr(cli, '_read', lambda: '/quit')
    cli._loop()
    output = capsys.readouterr().out
    assert '/seo author <name>' in output
    assert 'default: Sergio' in output
    assert 'Tool: daily_seo' in output


def test_model_failure_keeps_provider_model_and_reason():
    from seo.draft import failure_detail
    detail = failure_detail([
        {'provider': 'openrouter', 'model': 'nvidia/example',
         'error': {'type': 'TimeoutError', 'message': 'LLM route exceeded 120s'}},
        {'provider': 'ollama', 'model': 'qwen3:4b',
         'error': {'type': 'TimeoutError', 'message': 'LLM route exceeded 60s'}}])
    assert 'openrouter/nvidia/example' in detail
    assert 'ollama/qwen3:4b' in detail
    assert '120s' in detail and '60s' in detail


def test_status_keeps_failure_after_later_success(setup):
    seo.command('start 2')
    setup.side_effect = [RuntimeError('openrouter/model: timeout'), {'en': '# English', 'es': '# Spanish'}]
    runner = seo.DailySEO()
    runner.tick()
    runner.tick()
    assert 'openrouter/model: timeout' in seo.command('status')
    assert 'Drafts ready' in seo.command('status')
