"""Utility functions for MicroCLI."""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_json(filepath: str) -> Any:
    """Load data from JSON file."""
    path = Path(filepath)
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_json(filepath: str, data: Any) -> None:
    """Save data to JSON file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_tasks() -> List[Dict]:
    """Load tasks from tasks.json."""
    tasks = load_json('tasks.json')
    return tasks if tasks else []


def load_progress() -> Dict:
    """Load progress from progress.json."""
    progress = load_json('progress.json')
    return progress if progress else {
        "total_solved": 0,
        "streak_days": 0,
        "last_solved_date": None,
        "completed_tasks": {},
        "category_stats": {}
    }


def save_progress(progress: Dict) -> None:
    """Save progress to progress.json."""
    save_json('progress.json', progress)


def get_today_date() -> str:
    """Get today's date as string YYYY-MM-DD."""
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d')


def normalize_answer(answer: str) -> str:
    """Normalize answer for comparison."""
    return answer.strip().lower()


def check_answer(user_answer: str, correct_answer: str, options: Optional[List[str]] = None) -> bool:
    """Check if user's answer is correct."""
    user = normalize_answer(user_answer)
    correct = normalize_answer(correct_answer)
    
    # Direct match
    if user == correct:
        return True
    
    # Check options if provided
    if options:
        normalized_options = {normalize_answer(opt): i for i, opt in enumerate(options)}
        if user in normalized_options:
            correct_index = normalized_options.get(correct)
            if correct_index is not None:
                return True
    
    return False


def get_random_task(completed_ids: List[str], tasks: List[Dict]) -> Optional[Dict]:
    """Get a random task that hasn't been completed yet."""
    available = [t for t in tasks if t['id'] not in completed_ids]
    if not available:
        return None
    import random
    return random.choice(available)
