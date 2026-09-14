"""SQLite-backed demonstration railway reservation system."""
import argparse
from datetime import date
from pathlib import Path
import sqlite3
import uuid

def connect(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript('''
    CREATE TABLE IF NOT EXISTS trains(id INTEGER PRIMARY KEY, name TEXT, origin TEXT, destination TEXT, capacity INTEGER CHECK(capacity>0), fare INTEGER CHECK(fare>0));
    CREATE TABLE IF NOT EXISTS bookings(pnr TEXT PRIMARY KEY, train_id INTEGER REFERENCES trains(id), journey TEXT, passenger TEXT, seats INTEGER CHECK(seats>0), status TEXT CHECK(status IN ('confirmed','cancelled')));
    ''')
    with db:
        db.executemany('INSERT OR IGNORE INTO trains VALUES(?,?,?,?,?,?)', [(101,'Deccan Demo','Hyderabad','Pune',60,450),(102,'Coastal Demo','Vijayawada','Chennai',40,350),(103,'Garden Demo','Hyderabad','Bengaluru',50,600)])
    return db

def journey_date(value):
    parsed = date.fromisoformat(value)
    if parsed < date.today():
        raise ValueError('Journey date must be today or later.')
    return parsed.isoformat()

def availability(db, train_id, day):
    train = db.execute('SELECT * FROM trains WHERE id=?', (train_id,)).fetchone()
    if train is None:
        raise ValueError('Unknown train.')
    booked = db.execute("SELECT COALESCE(SUM(seats),0) FROM bookings WHERE train_id=? AND journey=? AND status='confirmed'", (train_id,day)).fetchone()[0]
    return train, train['capacity']-booked

def book(db, train_id, day, passenger, seats):
    day = journey_date(day)
    if not passenger.strip() or type(seats) is not int or seats < 1:
        raise ValueError('Passenger and a positive integer seat count are required.')
    with db:
        db.execute('BEGIN IMMEDIATE')
        train, remaining = availability(db, train_id, day)
        if seats > remaining:
            raise ValueError(f'Only {remaining} seats available.')
        pnr = uuid.uuid4().hex[:12].upper()
        db.execute("INSERT INTO bookings VALUES(?,?,?,?,?,'confirmed')", (pnr,train_id,day,passenger.strip(),seats))
    return pnr, train['fare']*seats

def cancel(db, pnr):
    with db:
        result = db.execute("UPDATE bookings SET status='cancelled' WHERE pnr=? AND status='confirmed'", (pnr.upper(),))
        if result.rowcount != 1:
            raise ValueError('Confirmed booking not found.')

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db', default=str(Path(__file__).with_name('railway.sqlite3')))
    sub = p.add_subparsers(dest='command', required=True)
    search = sub.add_parser('search'); search.add_argument('date'); search.add_argument('--origin', default=''); search.add_argument('--destination', default='')
    reserve = sub.add_parser('book'); reserve.add_argument('train',type=int); reserve.add_argument('date'); reserve.add_argument('passenger'); reserve.add_argument('--seats',type=int,default=1)
    for cmd in ('cancel','ticket'):
        sub.add_parser(cmd).add_argument('pnr')
    args = p.parse_args()
    db = connect(args.db)
    try:
        if args.command == 'search':
            day = journey_date(args.date)
            for row in db.execute('SELECT * FROM trains WHERE origin LIKE ? AND destination LIKE ?',('%'+args.origin+'%','%'+args.destination+'%')):
                _, remaining = availability(db,row['id'],day)
                print(f"{row['id']} | {row['name']} | {row['origin']} -> {row['destination']} | INR {row['fare']} | {remaining} seats")
        elif args.command == 'book':
            pnr, total = book(db,args.train,args.date,args.passenger,args.seats)
            print(f'Confirmed. PNR: {pnr}; total INR {total}')
        elif args.command == 'cancel':
            cancel(db,args.pnr); print('Cancelled. Seats released.')
        else:
            row = db.execute('SELECT * FROM bookings WHERE pnr=?',(args.pnr.upper(),)).fetchone()
            if row is None: raise ValueError('Ticket not found.')
            print(dict(row))
    except (ValueError,sqlite3.Error) as error:
        p.exit(1,f'Error: {error}\n')
    finally:
        db.close()

if __name__ == '__main__': main()
