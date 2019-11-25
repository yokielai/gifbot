import psycopg2
import os

conn = None


def setup_database():
    try:
        conn = create_connection()
        cur = conn.cursor()

        print("creating table if it doesnt exist")
        cur.execute("CREATE TABLE IF NOT EXISTS images (id SERIAL PRIMARY KEY, key VARCHAR(255), image BYTEA, guildId VARCHAR(255))")
        conn.commit()

    except (Exception, psycopg2.Error) as error:
        if conn:
            print("Failed to setup database tables", error)

    finally:
        if conn:
            cur.close()
            conn.close()


def create_connection():
    url = os.environ['DATABASE_URL']
    if os.getenv("LOCAL"):
        return psycopg2.connect(url)
    return psycopg2.connect(url, sslmode='require')


def image_exists(key, guildId):
    exists = True
    try:
        conn = create_connection()
        cur = conn.cursor()

        postgres_insert_query = "SELECT key FROM images WHERE key = %s AND guildId = %s"
        params = (key, str(guildId))

        cur.execute(postgres_insert_query, params)
        rows = cur.fetchall()

        exists = len(rows) > 0

    except (Exception, psycopg2.Error) as error:
        if (conn):
            print("Failed to check if key exists: ", error)

    finally:
        if (conn):
            cur.close()
            conn.close()
        return exists


def insert_image(key, image, guildId):
    try:
        conn = create_connection()
        cur = conn.cursor()

        postgres_insert_query = "INSERT INTO images (key, image, guildId) VALUES (%s, %s, %s)"
        record_to_insert = (key, image, str(guildId))

        cur.execute(postgres_insert_query, record_to_insert)
        conn.commit()
        print("Added image to db")

    except (Exception, psycopg2.Error) as error:
        if (conn):
            print("Failed to insert record in images table", error)

    finally:
        if (conn):
            cur.close()
            conn.close()


def read_image(key, guildId):
    rows=[]
    try:
        conn = create_connection()
        cur = conn.cursor()

        postgres_insert_query = f"SELECT image FROM images WHERE key = %s AND guildId = %s"

        cur.execute(postgres_insert_query, (key, str(guildId)))
        rows = cur.fetchall() #get all records
        
    except (Exception, psycopg2.Error) as error:
        if conn:
            print("Failed to insert record in images table", error)

    finally:
        if conn:
            cur.close()
            conn.close()
            
    if len(rows) > 0:
        return rows[0][0]

    return None


def delete_image(key, guildId):
    deleted_rows = 0
    try:
        conn = create_connection()
        cur = conn.cursor()

        postgres_insert_query = "DELETE FROM images WHERE key = %s AND guildId = %s"

        params = (key, str(guildId))
        cur.execute(postgres_insert_query, params)

        deleted_rows = cur.rowcount

        conn.commit()
        print("Deleted image from db")

    except (Exception, psycopg2.Error) as error:
        if conn:
            print("Failed to delete record from images table", error)

    finally:
        if conn:
            cur.close()
            conn.close()

    return deleted_rows


def update_image(key, image, guildId):
    try:
        conn = create_connection()
        cur = conn.cursor()

        postgres_insert_query = "UPDATE images SET image = %s WHERE key = %s AND guildId = %s"
        record_to_update = (image, key, str(guildId))

        cur.execute(postgres_insert_query, record_to_update)
        conn.commit()
        print("Image updated")

    except (Exception, psycopg2.Error) as error:
        if conn:
            print("Failed to update record in images table", error)

    finally:
        if conn:
            cur.close()
            conn.close()


def list_keys(guildId):
    try:
        conn = create_connection()
        cur = conn.cursor()

        postgres_insert_query = "SELECT key FROM images WHERE guildId = %s"
        params = (str(guildId),)
        cur.execute(postgres_insert_query, params)

        # the query is bringing back all the arrays, not smart enough to only bring the first element, i.e. keys only
        rows = cur.fetchall()

        # so we create a new array, and only insert keys into it, to get round the problem
        keys = []
        for row in rows:
            keys.append(row[0])

        return keys

    except (Exception, psycopg2.Error) as error:
        if conn:
            print("Failed to obtain a list of keys", error)

    finally:
        if conn:
            cur.close()
            conn.close()