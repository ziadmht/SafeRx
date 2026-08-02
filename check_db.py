import sqlite3 
from pathlib import Path 
db_path = Path('data/safeRx.db') 
conn = sqlite3.connect(db_path) 
cursor = conn.cursor() 
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Utilisateur'") 
exists = cursor.fetchone() 
if exists: 
    print('? Table Utilisateur existe') 
    cursor.execute('SELECT email, role FROM Utilisateur') 
    users = cursor.fetchall() 
    for u in users: 
        print(f'   - {u[0]} ({u[1]})') 
else: 
    print('? Table Utilisateur ABSENTE') 
conn.close() 
