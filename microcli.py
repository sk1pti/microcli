#!/usr/bin/env python3
"""
MicroCLI - Micro-learning system via CLI
"""
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme

from utils import load_tasks, load_progress, save_progress, get_today_date
from utils import check_answer, get_random_task, normalize_answer

# Custom theme
theme = Theme({
    "success": "green",
    "error": "red",
    "info": "blue",
    "warning": "yellow",
})

console = Console(theme=theme)


def cmd_today(args):
    """Show today's task."""
    tasks = load_tasks()
    progress = load_progress()
    
    if not tasks:
        rprint("[red][X] Task database is empty![/red]")
        return
    
    completed_ids = list(progress.get('completed_tasks', {}).keys())
    task = get_random_task(completed_ids, tasks)
    
    if not task:
        rprint("[green][*] Congratulations! All tasks completed![/green]")
        rprint(f"[info]Total solved: {progress['total_solved']}[/info]")
        return
    
    # Show task
    category_color = {
        "Логика": "cyan",
        "Математика": "magenta",
        "Программирование": "green",
        "Языки": "yellow",
        "Общие знания": "blue",
    }.get(task['category'], "white")
    
    panel = Panel(
        f"[bold]{task['question']}[/bold]\n\n[dim]Category: {task['category']}[/dim]",
        title=f"[{category_color}][BOOK] {task['category']}[/{category_color}]",
        subtitle="Press Enter to answer or 'q' to quit",
        expand=False,
        padding=(1, 2),
    )
    rprint(panel)
    
    # Get answer
    answer = console.input("\nYour answer: ")
    
    if answer.lower() in ('q', 'й'):
        rprint("[yellow][WAVE] Bye![/yellow]")
        return
    
    # Check answer
    correct = check_answer(answer, task['answer'], task.get('options'))
    
    if correct:
        rprint("\n[success][OK] Correct![/success]")
        
        # Update progress
        progress = update_progress(progress, task)
        save_progress(progress)
        
        # Show explanation
        if 'explanation' in task:
            rprint(f"\n[info][BULB] {task['explanation']}[/info]")
        
        # Show streak
        show_streak(progress)
    else:
        rprint(f"\n[error][X] Wrong![/error]")
        rprint(f"[success]Correct answer: {task['answer']}[/success]")
        
        if 'explanation' in task:
            rprint(f"\n[info][BULB] {task['explanation']}[/info]")


def update_progress(progress: dict, task: dict) -> dict:
    """Update progress after correct answer."""
    today = get_today_date()
    last_date = progress.get('last_solved_date')
    
    # Update streak
    if last_date == today:
        pass
    elif last_date:
        last_dt = datetime.strptime(last_date, '%Y-%m-%d')
        today_dt = datetime.strptime(today, '%Y-%m-%d')
        if (today_dt - last_dt).days == 1:
            progress['streak_days'] += 1
        elif (today_dt - last_dt).days > 1:
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


def show_streak(progress: dict):
    """Show streak progress."""
    streak = progress.get('streak_days', 0)
    total = progress.get('total_solved', 0)
    
    rprint(f"\n[info][FIRE] Streak days: {streak}[/info]")
    rprint(f"[info][CHART] Total solved: {total}[/info]")


def cmd_stats(args):
    """Show statistics."""
    progress = load_progress()
    
    table = Table(title="[CHART] Statistics", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Total solved", str(progress.get('total_solved', 0)))
    table.add_row("Streak days", str(progress.get('streak_days', 0)))
    
    rprint(table)
    
    # Category stats
    cat_stats = progress.get('category_stats', {})
    if cat_stats:
        cat_table = Table(title="[FOLDER] By category", show_header=True)
        cat_table.add_column("Category")
        cat_table.add_column("Solved")
        
        for cat, count in sorted(cat_stats.items(), key=lambda x: -x[1]):
            cat_table.add_row(cat, str(count))
        
        rprint(cat_table)
    
    # Recent completed
    completed = progress.get('completed_tasks', {})
    if completed:
        rprint("\n[info][CLOCK] Recently completed:[/info]")
        recent = list(completed.items())[-5:]
        for task_id, date in recent:
            rprint(f"  * {task_id} - {date}")


def cmd_category(args):
    """Show task from specific category."""
    category = args.category
    
    tasks = load_tasks()
    progress = load_progress()
    
    # Filter by category
    cat_tasks = [t for t in tasks if t.get('category') == category]
    
    if not cat_tasks:
        rprint(f"[error][X] Category '{category}' not found![/error]")
        return
    
    completed_ids = [
        tid for tid, date in progress.get('completed_tasks', {}).items()
        if any(t['id'] == tid for t in cat_tasks)
    ]
    
    task = get_random_task(completed_ids, cat_tasks)
    
    if not task:
        rprint(f"[yellow]All tasks in category '{category}' completed![/yellow]")
        return
    
    panel = Panel(
        f"[bold]{task['question']}[/bold]\n\n[dim]Category: {task['category']}[/dim]",
        title=f"[BOOK] {category}",
        expand=False,
    )
    rprint(panel)
    
    answer = console.input("\nYour answer: ")
    
    correct = check_answer(answer, task['answer'], task.get('options'))
    
    if correct:
        rprint("\n[success][OK] Correct![/success]")
        progress = update_progress(progress, task)
        save_progress(progress)
        if 'explanation' in task:
            rprint(f"\n[info][BULB] {task['explanation']}[/info]")
        show_streak(progress)
    else:
        rprint(f"\n[error][X] Wrong![/error]")
        rprint(f"[success]Correct answer: {task['answer']}[/success]")


def cmd_reset(args):
    """Reset progress."""
    rprint("[warning][!] Are you sure you want to reset progress?[/warning]")
    rprint("This action [bold]cannot be undone[/bold]!")
    
    confirm = console.input("\nEnter 'yes' to confirm: ")
    
    if confirm.lower() == 'yes':
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
        rprint("\n[success][OK] Progress reset![/success]")
    else:
        rprint("[yellow]Cancelled.[/yellow]")


def cmd_list_categories(args):
    """Show all available categories."""
    tasks = load_tasks()
    
    if not tasks:
        rprint("[red][X] Task database is empty![/red]")
        return
    
    categories = {}
    for task in tasks:
        cat = task.get('category', 'No category')
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
    
    table = Table(title="[FOLDER] Categories", show_header=True)
    table.add_column("Category", style="cyan")
    table.add_column("Tasks", style="magenta")
    
    for cat, count in sorted(categories.items()):
        table.add_row(cat, str(count))
    
    rprint(table)


def main():
    parser = argparse.ArgumentParser(
        description="MicroCLI - Micro-learning system via CLI",
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Default - today's task
    parser_today = subparsers.add_parser('today', help='Get today\'s task')
    
    # Stats
    parser_stats = subparsers.add_parser('stats', help='Show statistics')
    
    # Category
    parser_cat = subparsers.add_parser('category', help='Choose category')
    parser_cat.add_argument('category', help='Category name')
    
    # List categories
    parser_list = subparsers.add_parser('categories', help='Show all categories')
    
    # Reset
    parser_reset = subparsers.add_parser('reset', help='Reset progress')
    
    args = parser.parse_args()
    
    if args.command is None:
        cmd_today(args)
    elif args.command == 'today':
        cmd_today(args)
    elif args.command == 'stats':
        cmd_stats(args)
    elif args.command == 'category':
        cmd_category(args)
    elif args.command == 'categories':
        cmd_list_categories(args)
    elif args.command == 'reset':
        cmd_reset(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
