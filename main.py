import sqlite3


def create_db():
    con = sqlite3.connect("final_project.db")
    cur = con.cursor()
    cur.execute("""CREATE TABLE "User" (
	"user_name"	TEXT,
	"password"	TEXT,
	"email"	TEXT,
	"internet_package_type"	INTEGER,
	" publish_sectors"	INTEGER
);""")
    con.commit()
    con.close()



if __name__ == '__main__':
    create_db()