import fcntl
import json
import hashlib
import threading
import os
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from task_runtime import emergency
from task_runtime.supervisor import supervise
from seo.draft import run

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'context/DAILY_SEO.md'
STATE = ROOT / '.a1-seo.json'
OUTPUT = ROOT / 'docs/seo/drafts'
FIELDS = ('id', 'state', 'topic', 'english', 'spanish', 'priority', 'status')
HELP = '''CDLTestReady daily SEO — bilingual Markdown drafts
Destination: CDLTestReady. Auto-posting and review email are not connected yet.
/seo title <subject>             What the content is about
/seo keywords <phrase, phrase>   Target keywords; blank uses the Markdown registry
/seo author <name>               Author (default: Sergio)
/seo start [pairs/day]           Enable daily drafting (default: 5 pairs/day)
/seo activate cdltestready      Enable CDLTestReady with default settings
/seo set <pairs/day>             Change the daily quota
/seo status                     Show settings, current article, and progress
/seo stop                       Pause drafting
/seo help                       Show this help
/cdl_keywords {"action":"list"}  View the Markdown keyword registry
Tool: daily_seo; parameters: action, content_title, keywords, author, pairs_per_day.
Each pair = one English + one Spanish draft, with author and creation timestamp.
Settings: context/DAILY_SEO.md | Drafts: docs/seo/drafts/
Each keyword is used once. Drafts stay local for review.'''


def show_title(text):
    """Target this console's pane only; never rename another tmux session."""
    pane = os.environ.get('TMUX_PANE')
    if not pane:
        return
    title = ' '.join(text.split())[:100]
    try:
        subprocess.run(['tmux', 'rename-window', '-t', pane, title],
                       check=False, capture_output=True, timeout=2)
    except (OSError, subprocess.TimeoutExpired):
        pass


def settings():
    values = {}
    for line in CONFIG.read_text().splitlines():
        if ':' in line and not line.startswith('#'):
            key, value = line.split(':', 1)
            values[key] = value.strip()
    count = int(values['pairs_per_day'])
    if not 1 <= count <= 50 or values['enabled'] not in {'true', 'false'}:
        raise ValueError('Use enabled: true/false and pairs_per_day: 1–50.')
    ZoneInfo(values['timezone'])
    values.setdefault('content_title', 'CDL daily SEO')
    values.setdefault('keywords', '')
    values.setdefault('author', 'Sergio')
    if not values['author'].strip() or len(values['author']) > 100:
        raise ValueError('Author must be 1–100 characters.')
    return values


def keywords():
    from tools.seo_registry import FILES
    rows = []
    for line in FILES['cdl_keywords'].read_text().splitlines():
        cells = [v.strip() for v in line.strip().strip('|').split('|')]
        if len(cells) == 7 and cells[0].startswith('KW-'):
            rows.append(dict(zip(FIELDS, cells)))
    return sorted((r for r in rows if r['status'] == 'active'), key=lambda r: (r['priority'], r['id']))


def load():
    return json.loads(STATE.read_text()) if STATE.exists() else {'days': {}, 'used': [], 'status': 'idle'}


def save(state):
    temp = STATE.with_suffix('.tmp')
    temp.write_text(json.dumps(state, indent=2) + '\n')
    temp.replace(STATE)


def command(body):
    """Accept short console commands or the same actions as JSON tool input."""
    if body.strip() in {'help', '--help', '-h'}:
        return HELP
    data = {}
    if body.strip().startswith('{'):
        data = json.loads(body)
        action = data.get('action', 'status')
        if action == 'help':
            return HELP
        argument = str(data.get('pairs_per_day', ''))
        if action == 'title':
            argument = str(data.get('content_title', ''))
        if action == 'keywords':
            argument = data.get('keywords', '')
        if action == 'author':
            argument = data.get('author', '')
    else:
        action, _, argument = (body.strip() or 'status').partition(' ')
    if action not in {'start', 'stop', 'status', 'set', 'title', 'keywords', 'author', 'activate'}:
        raise ValueError('Use /seo start [pairs/day], stop, status, set <pairs/day>, title <topic>, keywords <phrases>, author <name>, or activate cdltestready.')
    if action == 'start' and emergency.active():
        raise ValueError('Emergency stop is active; inspect and clear it before starting SEO.')
    with CONFIG.with_suffix('.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        values = settings()
        if action == 'author' or (action in {'start', 'set'} and 'author' in data):
            author = argument if action == 'author' else data['author']
            if not isinstance(author, str) or not author.strip() or len(author) > 100 or '\n' in author or '\r' in author:
                raise ValueError('Author must be a single line of 1–100 characters.')
            values['author'] = author.strip()
        if action == 'title' or (action in {'start', 'set'} and 'content_title' in data):
            title = argument if action == 'title' else data['content_title']
            title = ' '.join(str(title).split())
            if not title or len(title) > 100:
                raise ValueError('Content title must be 1–100 characters.')
            values['content_title'] = title
        if action == 'keywords' or (action in {'start', 'set'} and 'keywords' in data):
            phrases = argument if action == 'keywords' else data['keywords']
            if isinstance(phrases, list):
                phrases = ', '.join(str(v) for v in phrases)
            if not isinstance(phrases, str) or len(phrases) > 2000:
                raise ValueError('Keywords must be a list or comma-separated text, up to 2000 characters.')
            values['keywords'] = ' '.join(phrases.split())
        if action in {'start', 'set'} and argument:
            if not argument.isdigit() or not 1 <= int(argument) <= 50:
                raise ValueError('pairs_per_day must be 1–50.')
            values['pairs_per_day'] = str(int(argument))
        elif action == 'set' and not any(k in data for k in ('content_title', 'keywords', 'author')):
            raise ValueError('Use /seo set <pairs/day>.')
        if action in {'start', 'stop'}:
            values['enabled'] = 'true' if action == 'start' else 'false'
        if action == 'activate':
            # Activate CDLTestReady defaults; assumes CONFIG already has the keys
            # (from DAILY_SEO.md or a prior /seo start command).
            values['enabled'] = 'true'
            service.wake.set()
            show_title(f"A1 | {values['content_title']} | enabled")
            return (f"SEO enabled | {values['content_title']} | {values['pairs_per_day']} EN+ES pairs/day | {values['timezone']}\n"
                    f"Keywords: {values['keywords'] or '(active Markdown keyword registry)'}\n"
                    f"Author: {values['author']}\n"
                    f"Runner: active")
        if action != 'status':
            text = CONFIG.read_text()
            for key, value in values.items():
                if not any(line.startswith(key + ':') for line in text.splitlines()):
                    text += f'{key}: {value}'.rstrip() + '\n'
                text = '\n'.join(f'{key}: {value}'.rstrip() if line.startswith(key + ':') else line for line in text.splitlines()) + '\n'
            temp = CONFIG.with_suffix('.tmp')
            temp.write_text(text)
            temp.replace(CONFIG)
    if action == 'stop':
        service.cancel.set()
    if action != 'status':
        service.wake.set()
    state = load()
    failures = '\n'.join(f"{day} slot {slot}: {entry['status']} — {entry.get('error', 'Previous run interrupted')}"
                         for day, slots in state['days'].items() for slot, entry in slots.items()
                         if entry['status'] in {'failed', 'interrupted'})
    if action != 'status':
        show_title(f"A1 | {values['content_title']} | {'enabled' if values['enabled'] == 'true' else 'paused'}")
    return (f"SEO {'enabled' if values['enabled'] == 'true' else 'paused'} | {values['content_title']} | "
            f"{values['pairs_per_day']} EN+ES pairs/day | {values['timezone']}\n"
            f"Keywords: {values['keywords'] or '(active Markdown keyword registry)'}\n"
            f"Author: {values['author']}\n"
            f"Runner: {'active' if service.thread and service.thread.is_alive() else 'not running in this process; start A1 console'}\n"
            f"{('Runner error: ' + service.error + chr(10)) if service.error else ''}"
            f"Article: {state.get('article_title', '(none yet)')}\n"
            f"{state.get('status', 'idle')}\n"
            f"{('Failed/interrupted jobs:\n' + failures + chr(10)) if failures else ''}"
            f"Settings: {CONFIG}\nDrafts: {OUTPUT}")


class DailySEO:
    def __init__(self):
        self.closed = threading.Event()
        self.cancel = threading.Event()
        self.wake = threading.Event()
        self.error = ''
        self.thread = None

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.closed.clear()
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    def close(self):
        self.closed.set()
        self.cancel.set()
        self.wake.set()
        if self.thread:
            self.thread.join(5)

    def loop(self):
        while not self.closed.is_set():
            self.wake.clear()
            try:
                self.tick()
                self.error = ''
            except Exception as exc:
                from tools.log import log_exception
                log_exception('daily_seo', exc)
                self.error = str(exc)
                from features.terminal_output.status import emit
                emit("SEO", f"Runner error: {exc}", "red")
            self.wake.wait(15)

    def tick(self):
        with STATE.with_suffix('.lock').open('w') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return
            config = settings()
            if config['enabled'] != 'true' or emergency.active() or self.closed.is_set():
                return
            self.cancel.clear()
            state = load()
            for day in state['days'].values():
                for previous in day.values():
                    if previous['status'] == 'running':
                        previous['status'] = 'interrupted'
                        state['status'] = 'Previous draft interrupted; inspect ' + str(STATE)
                        save(state)
            today = datetime.now(ZoneInfo(config['timezone'])).date().isoformat()
            slots = state['days'].setdefault(today, {})
            if len(slots) >= int(config['pairs_per_day']):
                ready = sum(s['status'] == 'drafted' for s in slots.values())
                show_title(f"A1 | {config['content_title']} | {ready}/{len(slots)} ready | {state.get('article_title', '')}")
                return
            candidates = keywords()
            if config['keywords']:
                candidates = []
                for phrase in dict.fromkeys(p.strip() for p in config['keywords'].split(',') if p.strip()):
                    ident = hashlib.sha256((config['content_title'] + '\n' + phrase).encode()).hexdigest()[:12]
                    candidates.append({'id': 'TOPIC-' + ident, 'topic': config['content_title'],
                                       'english': phrase, 'spanish': '', 'state': '',
                                       'priority': 'P1', 'status': 'active'})
            available = [r for r in candidates if r['id'] not in state['used']]
            if not available:
                state['status'] = 'No unused active keywords. Add keywords or activate new topics.'
                show_title(f"A1 | {config['content_title']} | needs keywords")
                save(state)
                return
            row = available[0]
            slot = str(len(slots) + 1)
            folder = OUTPUT / today / f"{int(slot):02d}-{row['id']}"
            # Reserve before calling the model: interruption/failure is visible and never
            # automatically retried, avoiding duplicate work and endless model calls.
            slots[slot] = {'keyword': row['id'], 'status': 'running', 'path': str(folder)}
            state['used'].append(row['id'])
            state['status'] = f"Drafting {today} slot {slot}: {row['id']}"
            from features.terminal_output.status import emit
            emit("SEO", f"Starting {slot}/{config['pairs_per_day']}: {row['english']} | Author: {config['author']}", "green")
            state['content_title'] = config['content_title']
            state['article_title'] = row['english'].split(';')[0]
            show_title(f"A1 | {config['content_title']} | {slot}/{config['pairs_per_day']} | {state['article_title']}")
            save(state)
            try:
                from tools.seo_registry import FILES
                pair = supervise('seo', {'content_title': config['content_title'], 'keyword': row, 'rules': FILES['google_seo_rules'].read_text()},
                                 None, timeout=600, target=run, cancel=self.cancel)
                if self.cancel.is_set() or settings()['enabled'] != 'true' or emergency.active():
                    raise RuntimeError('SEO stopped before saving the pair.')
                folder.mkdir(parents=True, exist_ok=True)
                created = datetime.now(ZoneInfo(config['timezone'])).isoformat(timespec='seconds')
                for lang in ('en', 'es'):
                    metadata = {'title': pair[lang].splitlines()[0].lstrip('# ').strip(),
                                'author': config['author'], 'created_at': created, 'lang': lang}
                    frontmatter = '---\n' + ''.join(f'{k}: {json.dumps(v, ensure_ascii=False)}\n' for k, v in metadata.items()) + '---\n\n'
                    (folder / f'{lang}.md').write_text(frontmatter + pair[lang] + '\n', encoding='utf-8')
                slots[slot].update(author=config['author'], created_at=created)
                slots[slot]['status'] = 'drafted'
                slots[slot]['title'] = pair['en'].splitlines()[0].lstrip('# ').strip()
                state['article_title'] = slots[slot]['title']
                state['status'] = f'Drafts ready for review: {folder}'
                show_title(f"A1 | {config['content_title']} | ready: {state['article_title']}")
            except Exception as exc:
                slots[slot]['status'] = 'failed'
                slots[slot]['error'] = str(exc)
                state['status'] = f'Slot {slot} failed: {exc}. See {STATE}.'
                show_title(f"A1 | {config['content_title']} | failed: {row['topic']}")
            save(state)
            emit("SEO", state['status'], "red" if "failed" in state['status'].lower() else "green")


service = DailySEO()
