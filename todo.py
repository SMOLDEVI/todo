import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import calendar
import typer
from colorama import Fore, Style, init

init(autoreset=True)

app = typer.Typer()

# Путь к файлу, где будут храниться задачи
TODO_FILE = Path.home() / "todo.json"

# Статусы задач
STATUS_NOT_STARTED = "not_started"
STATUS_IN_PROGRESS = "in_progress"
STATUS_DONE = "done"

def load_tasks() -> List[Dict[str, str]]:
    """Загружает задачи из файла."""
    if not TODO_FILE.exists():
        return []
    with open(TODO_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_tasks(tasks: List[Dict[str, str]]) -> None:
    """Сохраняет задачи в файл."""
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4)

def get_color_for_status(status: str) -> str:
    """Возвращает цвет для статуса задачи."""
    if status == STATUS_DONE:
        return Fore.GREEN
    elif status == STATUS_IN_PROGRESS:
        return Fore.YELLOW
    else:
        return Fore.WHITE

def print_calendar(year: int, month: int, highlight_day: Optional[int] = None):
    """Печатает календарь на указанный месяц и год."""
    cal = calendar.month(year, month)
    if highlight_day:
        # Подсвечиваем день в календаре
        cal = cal.replace(f" {highlight_day} ", f"[{highlight_day}]")
    print(cal)

@app.command()
def add(task: str, due_date: Optional[str] = None):
    """Добавляет новую задачу с опциональной датой выполнения."""
    tasks = load_tasks()
    task_data = {"task": task, "status": STATUS_NOT_STARTED, "due_date": due_date}
    tasks.append(task_data)
    save_tasks(tasks)
    typer.echo(f"Задача добавлена: {task} (Дата выполнения: {due_date or 'Бессрочно'})")

@app.command()
def show(task_number: Optional[int] =typer.Argument( None)):
    """Показывает все задачи или конкретную задачу с календарем."""
    tasks = load_tasks()
    if not tasks:
        typer.echo("Задач нет.")
        return

    if task_number is not None:
        # Показать конкретную задачу
        if 1 <= task_number <= len(tasks):
            task = tasks[task_number - 1]
            typer.echo(f"Задача {task_number}: {task['task']}")
            typer.echo(f"Статус: {task['status']}")
            due_date = task.get("due_date")
            if due_date:
                typer.echo(f"Дата выполнения: {due_date}")
                # Показать календарь с датой выполнения
                due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
                print_calendar(due_date_obj.year, due_date_obj.month, due_date_obj.day)
            else:
                typer.echo("Дата выполнения: Бессрочно")
        else:
            typer.echo("Неверный номер задачи.")
    else:
        # Показать все задачи
        for i, task in enumerate(tasks, 1):
            due_date = task.get("due_date", "Бессрочно")
            typer.echo(f"{i}. {task['task']} (Статус: {task['status']}, Дата выполнения: {due_date})")

@app.command()
def remove(task_number: int):
    """Удаляет задачу по номеру."""
    tasks = load_tasks()
    if 1 <= task_number <= len(tasks):
        removed_task = tasks.pop(task_number - 1)
        save_tasks(tasks)
        typer.echo(f"Задача удалена: {removed_task['task']}")
    else:
        typer.echo("Неверный номер задачи.")

@app.command()
def clear():
    """Очищает все задачи."""
    save_tasks([])
    typer.echo("Все задачи удалены.")

@app.command()
def start(task_number: int):
    """Помечает задачу как 'в процессе'."""
    tasks = load_tasks()
    if 1 <= task_number <= len(tasks):
        tasks[task_number - 1]["status"] = STATUS_IN_PROGRESS
        save_tasks(tasks)
        typer.echo(f"Задача '{tasks[task_number - 1]['task']}' в процессе.")
    else:
        typer.echo("Неверный номер задачи.")

@app.command()
def done(task_number: int):
    """Помечает задачу как 'выполнено'."""
    tasks = load_tasks()
    if 1 <= task_number <= len(tasks):
        tasks[task_number - 1]["status"] = STATUS_DONE
        save_tasks(tasks)
        typer.echo(f"Задача '{tasks[task_number - 1]['task']}' выполнена.")
    else:
        typer.echo("Неверный номер задачи.")

if __name__ == "__main__":
    app()
