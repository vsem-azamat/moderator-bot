from db.sqlite import cursor, conn


def add_start(id_user: str):
    sql = """
    SELECT *
    FROM start_users
    WHERE user_id = (?)
    """
    cursor.execute(sql, [id_user])
    catalog = cursor.fetchall()
    if len(catalog) == 0:
        id_user = str(id_user)
        sql = """
        INSERT INTO start_users
        (user_id)
        VALUES (?)
        """
        cursor.execute(sql, [id_user])
        conn.commit()
    else:
        pass
