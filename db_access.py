import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

def upsert_server_mst(server_id:str, lang:str='J', pin_mode:str='0', all_mention:bool=False):
    with psycopg2.connect(DATABASE_URL, sslmode='require') as conn:
        with conn.cursor() as cur:
            
            bool2str = lambda b: 'X' if b else 'A'

            if(count_server_mst(server_id) > 0):
                cur.execute(
                    "UPDATE MST_SERVER SET LANG = %s, PIN_MODE = %s, ALL_MENTION = %s WHERE SERVER_ID = %s;",
                    (lang, pin_mode, bool2str(all_mention), server_id)
                )
            else:
                cur.execute(
                    "INSERT INTO MST_SERVER (SERVER_ID, LANG, PIN_MODE, ALL_MENTION) VALUES (%s, %s, %s, %s);",
                    (server_id, lang, pin_mode, bool2str(all_mention))
                )

            conn.commit()

def count_server_mst(server_id:str):
    with psycopg2.connect(DATABASE_URL, sslmode='require') as conn:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT COUNT(*) FROM MST_SERVER WHERE SERVER_ID = %s;",
                (server_id)
            )

            count = cur.fetchone()[0]

            return count

def insert_user_mst(server_id:str, user_id:str):
    with psycopg2.connect(DATABASE_URL, sslmode='require') as conn:
        with conn.cursor() as cur:

            cur.execute(
                "INSERT INTO MST_USER (SERVER_ID, USER_ID) VALUES (%s, %s);",
                (server_id, user_id)
            )

            conn.commit()

def count_user_mst(server_id:str, user_id:str):
    with psycopg2.connect(DATABASE_URL, sslmode='require') as conn:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT COUNT(*) FROM MST_USER WHERE SERVER_ID = %s AND USER_ID = %s;",
                (server_id, user_id)
            )

            count = cur.fetchone()[0]

            return count

def delete_user_mst(server_id:str, user_id:str):
    with psycopg2.connect(DATABASE_URL, sslmode='require') as conn:
        with conn.cursor() as cur:

            cur.execute(
                "DELETE FROM MST_USER WHERE SERVER_ID = %s AND USER_ID = %s;",
                (server_id, user_id)
            )

            conn.commit()
