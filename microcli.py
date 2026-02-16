#!/usr/bin/env python3
"""
MicroCLI - Micro-learning system via CLI
Supports Russian and English languages.
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme

# Localization support
LOCALE_DIR = Path(__file__).parent / "locales"
_translations = {}


def load_locale(lang: str = "ru") -> dict:
    """Load translation file."""
    locale_file = LOCALE_DIR / f"{lang}.json"
    if locale_file.exists():
        with open(locale_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def _(key: str, lang: str = "ru") -> str:
    """Get translated string."""
    global _translations
    if lang not in _translations:
        _translations[lang] = load_locale(lang)
    return _translations[lang].get(key, key)


def set_language(lang: str):
    """Set current language."""
    global _translations
    _translations[lang] = load_locale(lang)


# Custom theme
theme = Theme({
    "success": "green",
    "error": "red",
    "info": "blue",
    "warning": "yellow",
})

console = Console(theme=theme)


def get_tasks() -> list:
    """Load tasks from JSON file."""
    tasks_file = Path(__file__).parent / "tasks.json"
    if tasks_file.exists():
        with open(tasks_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def get_progress() -> dict:
    """Load progress from JSON file."""
    progress_file = Path(__file__).parent / "progress.json"
    if progress_file.exists():
        with open(progress_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "total_solved": 0,
        "streak_days": 0,
        "last_solved_date": None,
        "completed_tasks": {},
        "category_stats": {}
    }


def save_progress(progress: dict):
    """Save progress to JSON file."""
    progress_file = Path(__file__).parent / "progress.json"
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def get_today() -> str:
    """Get today's date as string."""
    return datetime.now().strftime('%Y-%m-%d')


def normalize_answer(answer: str) -> str:
    """Normalize answer for comparison."""
    return answer.strip().lower()


def check_answer(user_answer: str, correct_answer: str, options: list = None) -> bool:
    """Check if answer is correct."""
    user = normalize_answer(user_answer)
    correct = normalize_answer(correct_answer)
    
    if user == correct:
        return True
    
    if options:
        for opt in options:
            if normalize_answer(opt) == correct:
                return True
    
    return False


def get_random_task(completed_ids: list, tasks: list) -> dict:
    """Get random uncompleted task."""
    available = [t for t in tasks if t['id'] not in completed_ids]
    if not available:
        return None
    import random
    return random.choice(available)


def update_progress(progress: dict, task: dict, lang: str) -> dict:
    """Update progress after correct answer."""
    today = get_today()
    last_date = progress.get('last_solved_date')
    
    # Update streak
    if last_date != today:
        if last_date:
            last_dt = datetime.strptime(last_date, '%Y-%m-%d')
            today_dt = datetime.strptime(today, '%Y-%m-%d')
            diff = (today_dt - last_dt).days
            if diff == 1:
                progress['streak_days'] += 1
            else:
                progress['streak_days'] = 1
        else:
            progress['streak_days'] = 1
    
    progress['last_solved_date'] = today
    progress['total_solved'] += 1
    progress['completed_tasks'][task['id']] = today
    
    # Update category stats
    cat = task['category']
    if cat not in progress.get('category_stats', {}):
        progress['category_stats'][cat] = 0
    progress['category_stats'][cat] += 1
    
    return progress


def cmd_today(args):
    """Show today's task."""
    lang = args.lang or "ru"
    set_language(lang)
    
    tasks = get_tasks()
    progress = get_progress()
    
    if not tasks:
        rprint(_("task_database_empty", lang))
        return
    
    completed_ids = list(progress.get('completed_tasks', {}).keys())
    task = get_random_task(completed_ids, tasks)
    
    if not task:
        rprint(_("all_completed", lang))
        rprint(f"{_('total_solved', lang)}: {progress['total_solved']}")
        return
    
    # Show task
    category_colors = {
        "Логика": "cyan",
        "Математика": "magenta",
        "Программирование": "green",
        "Языки": "yellow",
        "Общие знания": "blue",
    }
    cat_color = category_colors.get(task['category'], "white")
    
    panel = Panel(
        f"[bold]{task['question']}[/bold]\n\n{_('category', lang)}: {task['category']}",
        title=f"[{cat_color}][BOOK] {task['category']}[/{cat_color}]",
        subtitle=_("subtitle_enter", lang),
        expand=False,
        padding=(1, 2),
    )
    rprint(panel)
    
    # Get answer
    answer = console.input(f"\n{_('enter_answer', lang)}: ")
    
    if answer.lower() in ('q', 'й', _('quit', lang)):
        rprint(_("bye", lang))
        return
    
    correct = check_answer(answer, task['answer'], task.get('options'))
    
    if correct:
        rprint(f"\n{_('correct', lang)}")
        
        progress = update_progress(progress, task, lang)
        save_progress(progress)
        
        if 'explanation' in task:
            rprint(f"\n[BULB] {task['explanation']}")
        
        rprint(f"\n{_('streak_days', lang)}: {progress['streak_days']}")
        rprint(f"{_('total_solved_stat', lang)}: {progress['total_solved']}")
    else:
        rprint(f"\n{_('wrong', lang)}")
        rprint(f"{_('correct_answer', lang)}: {task['answer']}")
        
        if 'explanation' in task:
            rprint(f"\n[BULB] {task['explanation']}")


def cmd_stats(args):
    """Show statistics."""
    lang = args.lang or "ru"
    set_language(lang)
    
    progress = get_progress()
    
    table = Table(title=_("statistics", lang), show_header=True)
    table.add_column(_("metric", lang), style="cyan")
    table.add_column(_("value", lang), style="magenta")
    
    table.add_row(_("total_solved_stat", lang), str(progress.get('total_solved', 0)))
    table.add_row(_("streak_days", lang), str(progress.get('streak_days', 0)))
    
    rprint(table)
    
    # Category stats
    cat_stats = progress.get('category_stats', {})
    if cat_stats:
        cat_table = Table(title=_("by_category", lang), show_header=True)
        cat_table.add_column(_("category_label", lang))
        cat_table.add_column(_("solved_label", lang))
        
        for cat, count in sorted(cat_stats.items(), key=lambda x: -x[1]):
            cat_table.add_row(cat, str(count))
        
        rprint(cat_table)
    
    # Recent
    completed = progress.get('completed_tasks', {})
    if completed:
        rprint(f"\n{_('recently_completed', lang)}")
        recent = list(completed.items())[-5:]
        for task_id, date in recent:
            rprint(f"  * {task_id} - {date}")


def cmd_category(args):
    """Show task from specific category."""
    lang = args.lang or "ru"
    set_language(lang)
    
    category = args.category
    tasks = get_tasks()
    progress = get_progress()
    
    cat_tasks = [t for t in tasks if t.get('category') == category]
    
    if not cat_tasks:
        rprint(_("category_not_found", lang).format(category=category))
        return
    
    completed_ids = [
        tid for tid, date in progress.get('completed_tasks', {}).items()
        if any(t['id'] == tid for t in cat_tasks)
    ]
    
    task = get_random_task(completed_ids, cat_tasks)
    
    if not task:
        rprint(_("category_completed", lang).format(category=category))
        return
    
    panel = Panel(
        f"[bold]{task['question']}[/bold]\n\n{_('category', lang)}: {task['category']}",
        title=f"[BOOK] {category}",
        expand=False,
    )
    rprint(panel)
    
    answer = console.input(f"\n{_('enter_answer', lang)}: ")
    
    correct = check_answer(answer, task['answer'], task.get('options'))
    
    if correct:
        rprint(f"\n{_('correct', lang)}")
        progress = update_progress(progress, task, lang)
        save_progress(progress)
        if 'explanation' in task:
            rprint(f"\n[BULB] {task['explanation']}")
        rprint(f"\n{_('streak_days', lang)}: {progress['streak_days']}")
    else:
        rprint(f"\n{_('wrong', lang)}")
        rprint(f"{_('correct_answer', lang)}: {task['answer']}")


def cmd_reset(args):
    """Reset progress."""
    lang = args.lang or "ru"
    set_language(lang)
    
    rprint(_("reset_warning", lang))
    rprint(_("reset_cannot_undo", lang))
    
    confirm = console.input(f"\n{_('enter_yes', lang)}: ")
    
    if confirm.lower() == _("reset_confirm", lang):
        default_progress = {
            "total_solved": 0,
            "streak_days": 0,
            "last_solved_date": None,
            "completed_tasks": {},
            "category_stats": {
                "Логика": 0,
                "Математика": 0,
                "Программирование": 0,
                "Языки": 0,
                "Общие знания": 0
            }
        }
        save_progress(default_progress)
        rprint(f"\n{_('progress_reset', lang)}")
    else:
        rprint(_("cancelled", lang))


def cmd_categories(args):
    """Show all categories."""
    lang = args.lang or "ru"
    set_language(lang)
    
    tasks = get_tasks()
    
    if not tasks:
        rprint(_("task_database_empty", lang))
        return
    
    categories = {}
    for task in tasks:
        cat = task.get('category', _("no_category", lang))
        categories[cat] = categories.get(cat, 0) + 1
    
    table = Table(title=_("categories_title", lang), show_header=True)
    table.add_column(_("category_label", lang), style="cyan")
    table.add_column(_("solved_label", lang), style="magenta")
    
    for cat, count in sorted(categories.items()):
        table.add_row(cat, str(count))
    
    rprint(table)


def main():
    parser = argparse.ArgumentParser(
        description="MicroCLI - Micro-learning system via CLI",
    )
    
    parser.add_argument(
        "--lang", "-l",
        choices=["ru", "en"],
        default="ru",
        help="Language (ru/en, default: ru)"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Today
    parser_today = subparsers.add_parser('today', help=_("get_today_task", "ru"))
    parser_today.add_argument("--lang", "-l", choices=["ru", "en"], help="Language")
    
    # Stats
    parser_stats = subparsers.add_parser('stats', help=_("show_statistics", "ru"))
    parser_stats.add_argument("--lang", "-l", choices=["ru", "en"], help="Language")
    
    # Category
    parser_cat = subparsers.add_parser('category', help=_("choose_category", "ru"))
    parser_cat.add_argument('category', help=_("category_name", "ru"))
    parser_cat.add_argument("--lang", "-l", choices=["ru", "en"], help="Language")
    
    # Categories
    parser_list = subparsers.add_parser('categories', help=_("show_all_categories", "ru"))
    parser_list.add_argument("--lang", "-l", choices=["ru", "en"], help="Language")
    
    # Reset
    parser_reset = subparsers.add_parser('reset', help=_("reset_progress", "ru"))
    parser_reset.add_argument("--lang", "-l", choices=["ru", "en"], help="Language")
    
    args = parser.parse_args()
    
    # Default language
    lang = getattr(args, 'lang', None) or "ru"
    
    if args.command is None:
        set_language(lang)
        cmd_today(args)
    elif args.command == 'today':
        cmd_today(args)
    elif args.command == 'stats':
        cmd_stats(args)
    elif args.command == 'category':
        cmd_category(args)
    elif args.command == 'categories':
        cmd_categories(args)
    elif args.command == 'reset':
        cmd_reset(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
