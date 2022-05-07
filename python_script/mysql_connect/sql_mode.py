import mysql.connector
class ConnectMySql :
    def __init__(self,database_name='',host='',user='',passwd='') :
        self.host = host
        self.database_name = database_name
        self.user = user
        self.passwd = passwd
        self.mydb = self.connect_mysql()
        self.mycursor = self.mydb.cursor()
    def connect_mysql(self) :
        try :
            mydb = mysql.connector.connect(
                host = self.host,
                user = self.user,
                passwd = self.passwd,
                buffered = 0,
                auth_plugin = "mysql_native_password"
            )
            
            return mydb
        except Exception as connect_mysql_err :
            print("connect_mysql_err:",connect_mysql_err)
            exit()
    def _connect_database_and_get_cursor(self) :
        try :
            self.mydb.connect(database = self.database_name)
            self.mycursor = self.mydb.cursor()
        except Exception as connect_database_err:
            print("connect_database_err:",connect_database_err)
class MysqlAdd(ConnectMySql)  :
    def __init__(self,database_name='',host='', user='', passwd='',):
        super().__init__(database_name,host, user, passwd)
    def add_database(self,database_name) :
        try :
            mydb = self.connect_mysql()
            mycursor = mydb.cursor()
            mycursor.execute('CREATE DATABASE %s' % (database_name))
            return mycursor
        except Exception as add_database_err :
            print("add_database_err:",add_database_err)
    def add_table(self,table_name) :
        try :
            self._connect_database_and_get_cursor()
            self.mycursor.execute("CREATE TABLE %s (id INT AUTO_INCREMENT PRIMARY KEY)" % (table_name))
            return self.mycursor
        except Exception as add_table_err :
            print("add_table_err:",add_table_err)
    def add_column(self,table_name,column_name) :
        try :
            self._connect_database_and_get_cursor()
            self.mycursor.execute('ALTER TABLE %s ADD COLUMN (%s mediumtext)' % (table_name,column_name))
            return self.mycursor
        except Exception as add_column_err:
            print("add_column_err:",add_column_err)
    def add_data(self,add_sql,add_value) :
        try :
            self._connect_database_and_get_cursor()
            self.mycursor.executemany(add_sql,add_value)
            self.mydb.commit()
            return self.mycursor.rowcount
        except  Exception as  add_data_err :
            print("add_data_err:",add_data_err)
    def mysql_add(self) :
        self._connect_database_and_get_cursor()
        return self.mydb,self.mycursor
class MysqlDelete(ConnectMySql) :
    def __init__(self, database_name='', host='', user='', passwd=''):
        super().__init__(database_name, host, user, passwd)
    def delete_database(self,database_name) :
        try :
            self.mycursor.execute('DROP DATABASE %s' % (database_name))
            return self.mycursor
        except Exception as del_database_err :
            print("del_database_err:",del_database_err)
    def delete_table(self,table_name) :
        try :
            self._connect_database_and_get_cursor()
            sql_comm = 'DROP TABLE %s' % (table_name)
            self.mycursor.execute(sql_comm)
            return self.mycursor
        except Exception as delete_table_err :
            print("delete_table_err:",delete_table_err)
    def delete_table_data(self,sql_comm) :
        try :
            self._connect_database_and_get_cursor()
            sql_comm = sql_comm
            self.mycursor.execute(sql_comm)
            self.mydb.commit()
            return self.mycursor
        except Exception as delete_table_data_err :
            print("delete_table_data_err:",delete_table_data_err)
    def delete_table_all_data(self,table_name) :
        try :
            self._connect_database_and_get_cursor()
            sql_comm = 'TRUNCATE TABLE %s' % (table_name)
            self.mycursor.execute(sql_comm)
            return self.mycursor
        except Exception as delete_table_all_data_err :
            print("delete_table_all_data_err:",delete_table_all_data_err)  
    def mysql_delete(self) :
        self._connect_database_and_get_cursor()
        return self.mydb,self.mycursor
class MysqlSearch(ConnectMySql) :
    def __init__(self, database_name='', host='', user='', passwd=''):
        super().__init__(database_name, host, user, passwd)
    def search_database_list(self) :
        try :
            database_name_list  = []
            self.mycursor.execute('SHOW DATABASES')
            for i in self.mycursor :
                database_name_list.append(i[0].decode('utf-8'))
            return database_name_list
        except Exception as search_database_list_err :
            print("search_database_list_err:",search_database_list_err)
    def search_table_list(self) :
        try :
            table_name_list = []
            self._connect_database_and_get_cursor()
            self.mycursor.execute('SHOW TABLES')
            for i in self.mycursor :
                table_name_list.append(i[0].decode('utf-8'))
            return table_name_list
        except Exception as search_table_list_err :
            print("search_table_list_err:",search_table_list_err)
    def search_table_data(self,sql_comm) :
        try :
            self._connect_database_and_get_cursor()
            self.mycursor.execute(sql_comm) 
            sql_result = self.mycursor.fetchall()
            return sql_result
        except Exception as search_table_data_err :
            print("search_table_data_err:",search_table_data_err)
class MysqlChange(ConnectMySql) :
    def __init__(self, database_name='', host='', user='', passwd=''):
        super().__init__(database_name, host, user, passwd) 
    def change_table_data(self,sql_comm) :
        try :
            self._connect_database_and_get_cursor()
            self.mycursor.execute(sql_comm)
            self.mydb.commit()
            return self.mycursor
        except Exception as change_table_data_err :
            print("change_table_data_err:",change_table_data_err)
class MysqlMode(MysqlAdd,MysqlDelete,MysqlSearch,MysqlChange,ConnectMySql) :
    def __init__(self, database_name='', host='', user='', passwd=''):
        super().__init__(database_name, host, user, passwd)
    def create_database_and_table_and_cloumn(self,database_name,table_name,column_list) :
        print(self.search_database_list())
        if database_name not in self.search_database_list() :    
            self.add_database(database_name)
        self.database_name = database_name
        self.add_table(table_name)
        for i in column_list :
            self.add_column(table_name,i)

if __name__ == '__main__' :
    pass
    # MysqlMode().create_database_and_table_and_cloumn('mode_test','mode_test',["a","b","c"])
    # sql_comm = "UPDATE test SET test2='666666' WHERE id=5"
    # MysqlChange("AbnormalData").change_table_data(sql_comm)
    # sql_comm = 'SELECT * FROM test'

    # MysqlSearch('AbnormalData').search_table_data(sql_comm)
    # pass
    # add_sql = 'INSERT INTO test VALUES (null,%s,%s)'
    # add_value = [(1,2),(2,3),(3,4)]
    # OBJ = MysqlAdd('AbnormalData')
    # OBJ.add_table('test')
    # OBJ.add_column('test','test2')
    # OBJ.add_data(add_sql,add_value)
    # MysqlAdd('abnormal').add_database('abnormal')
    # sql_comm = "DELETE FROM test WHERE id=1"
    # OBJ = MysqlDelete("AbnormalData")
    # OBJ.delete_table('test')
    # OBJ.delete_table_all_data('test')
    # OBJ.delete_table_data(sql_comm)
    # MysqlDelete(database_name='AbnormalData').delete_table("test")