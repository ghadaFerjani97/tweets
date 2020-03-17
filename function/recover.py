###### fichier qui regroupe les fonctions pour récupérer les données

import pandas as pd
import numpy as np
import mysql.connector
from mysql.connector import Error
import pickle


def get_dataframe_from_table(table_name, number=None, columns=None):
    df = None
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='tweeter',
                                             user='alexandre',
                                             password='Alexandre1%')
        if number is not None:
            if columns is not None:
                sql_select_query = "select t.%s from %s t limit %d" % (',t.'.join(columns), table_name, number)
            else:
                sql_select_query = "select * from %s limit %d" % (table_name, number)

        else:
            if columns is not None:
                sql_select_query = "select t.%s from %s t " % (',t.'.join(columns), table_name)
            else:
                sql_select_query = "select * from %s " % table_name

        cursor = connection.cursor()
        cursor.execute(sql_select_query)
        records = cursor.fetchall()
        columns_names = [field[0] for field in cursor.description]
        print("Total number of rows in " + table_name + " is: ", cursor.rowcount)
        df = pd.DataFrame(np.array(records), columns=columns_names)
        # print(columns_names)

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if (connection.is_connected()):
            connection.close()
            cursor.close()
            print("MySQL connection is closed")
            return df


def read_pkl(filename):
    file = open('./data/%s.pkl' % filename, 'rb')
    data = pickle.load(file)
    file.close()
    return data


def dump_pkl(filename, data):
    file = open('./data/%s.pkl' % filename, 'wb')
    pickle.dump(data, file)
    file.close()
    return data
