import sqlite3
con = sqlite3.connect('dtb.db', check_same_thread=False)
cur = con.cursor()

# We read the .sql file and execute it

# We clear the file
with open("dtb.db", "w") as f:
	f.write("")

with open("build.sql", "r", encoding="utf-8") as script:
	cur.executescript(script.read())
	con.commit()

cur.execute("INSERT INTO users (userid, cat_counter) VALUES (?, ?)", (1, 0))
cur.execute("INSERT INTO users (userid, cat_counter) VALUES (?, ?)", (2, 3))
cur.execute("INSERT INTO users (userid, cat_counter) VALUES (?, ?)", (7, 2))

con.commit()

cur.execute("SELECT * FROM users")
req = cur.fetchall()
print(req)