"""Persistent command-line to-do list with deadlines and priorities."""
import argparse
from datetime import date
from pathlib import Path
import sqlite3

def connect(path):
    db=sqlite3.connect(path); db.row_factory=sqlite3.Row
    db.execute("CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,due TEXT,priority INTEGER CHECK(priority BETWEEN 1 AND 3),done INTEGER NOT NULL DEFAULT 0 CHECK(done IN(0,1)))")
    return db

def add(db,title,due=None,priority=2):
    if not title.strip(): raise ValueError('Task title is required.')
    if due: due=date.fromisoformat(due).isoformat()
    if priority not in (1,2,3): raise ValueError('Priority must be 1, 2 or 3.')
    with db: return db.execute('INSERT INTO tasks(title,due,priority) VALUES(?,?,?)',(title.strip(),due,priority)).lastrowid

def change(db,task_id,action):
    statements={'done':'UPDATE tasks SET done=1 WHERE id=?','reopen':'UPDATE tasks SET done=0 WHERE id=?','delete':'DELETE FROM tasks WHERE id=?'}
    if action not in statements: raise ValueError('Unknown action.')
    with db:
        if db.execute(statements[action],(task_id,)).rowcount!=1: raise ValueError('Task not found.')

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--db',default=str(Path(__file__).with_name('tasks.sqlite3')))
    sub=p.add_subparsers(dest='command',required=True)
    cmd=sub.add_parser('add'); cmd.add_argument('title'); cmd.add_argument('--due'); cmd.add_argument('--priority',type=int,default=2,choices=(1,2,3))
    cmd=sub.add_parser('list'); cmd.add_argument('--all',action='store_true'); cmd.add_argument('--search',default='')
    for action in ('done','reopen','delete'): sub.add_parser(action).add_argument('id',type=int)
    args=p.parse_args(); db=connect(args.db)
    try:
        if args.command=='add': print('Task added:',add(db,args.title,args.due,args.priority))
        elif args.command=='list':
            rows=db.execute('SELECT * FROM tasks WHERE (? OR done=0) AND title LIKE ? ORDER BY done,priority,due IS NULL,due,id',(args.all,'%'+args.search+'%')).fetchall()
            if not rows: print('No matching tasks.')
            for row in rows:
                overdue=bool(row['due'] and row['due']<date.today().isoformat() and not row['done'])
                print(f"{row['id']} [{'x' if row['done'] else ' '}] P{row['priority']} {row['title']} | {row['due'] or 'No deadline'} {'OVERDUE' if overdue else ''}")
        else: change(db,args.id,args.command); print('Task updated.')
    except (ValueError,sqlite3.Error) as error: p.exit(1,f'Error: {error}\n')
    finally: db.close()

if __name__=='__main__': main()
