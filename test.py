def check_exists(id_row:int, where_column:str='id_tg', table:str='users', return_column:tuple = ('id', 'id_tg')):
        """
        user exists -> id_tg
        dont exists -> 0
        """
        sql = f"SELECT {', '.join(return_column)}  FROM {table} WHERE {where_column} = {id_row};"
        # return execute(sql).fetchone()
        return sql

print(check_exists(1, where_column='id', table='admins'))
