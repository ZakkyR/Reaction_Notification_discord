import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

def insert_user_mst(server_id:str, user_id:str):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO MST_USER (SERVER_ID, USER_ID) VALUES (%s, %s);",
        (server_id, user_id)
    )

    conn.commit()

    cur.close()
    conn.close()

def count_user_mst(server_id:str, user_id:str):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM MST_USER WHERE SERVER_ID = %s AND USER_ID = %s;",
        (server_id, user_id)
    )

    count = cur.fetchone()[0]

    cur.close()
    conn.close()

    return count

def delete_user_mst(server_id:str, user_id:str):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM MST_USER WHERE SERVER_ID = %s AND USER_ID = %s;",
        (server_id, user_id)
    )

    conn.commit()

    cur.close()
    conn.close()