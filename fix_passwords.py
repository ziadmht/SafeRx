import sqlite3 
import hashlib 
from pathlib import Path 
db_path = Path('data/safeRx.db') 
conn = sqlite3.connect(db_path) 
cursor = conn.cursor() 
admin_hash = hashlib.sha256('admin123'.encode()).hexdigest() 
pharma_hash = hashlib.sha256('pharmacien123'.encode()).hexdigest() 
cursor.execute('UPDATE Utilisateur SET mot_de_passe = ? WHERE email = ?', (admin_hash, 'admin@saferx.com')) 
cursor.execute('UPDATE Utilisateur SET mot_de_passe = ? WHERE email = ?', (pharma_hash, 'pharmacien@saferx.com')) 
conn.commit() 
conn.close() 
print('? Mots de passe mis … jour !') 
print('admin@saferx.com / admin123') 
print('pharmacien@saferx.com / pharmacien123') 
