import sqlite3
import time
from statistics import mean


# print the table
def print_posts(conn, table_name):
    cur = conn.cursor()
    cur.execute("SELECT * FROM {}".format(table_name))
    print("Table:", table_name, cur.fetchall())

def get_ok_values(conn, param_name):
    ok_values = conn.execute(
        "SELECT id_request FROM classification_requests WHERE response_status='OK'"
    ).fetchall()
    conn.commit()
    ok_values = [int(x) for t in ok_values for x in t]

    sql = "SELECT param_value from classification_request_params WHERE param_name='{}' \
                    AND id_request IN ({seq})".format(param_name, seq=','.join(['?'] * len(ok_values)))

    cursor = conn.execute(sql, ok_values)
    ok_values = cursor.fetchall()
    conn.commit()
    ok_values = [x for t in ok_values for x in t]

    return ok_values

def compute_most_frequent(conn, param_name):
    # get value with maximal occurence from f3
    if conn.execute("SELECT COUNT() FROM classification_requests").fetchone()[0] > 0:
        ok_values = get_ok_values(conn, param_name)
        most_frequent = max(set(ok_values), key=ok_values.count)
    else:
        most_frequent = ''
    return most_frequent


def compute_mean_value(conn, param_name):
    if conn.execute("SELECT COUNT() FROM classification_requests").fetchone()[0] > 0:
        ok_values = get_ok_values(conn, param_name)
        mean_val = mean([float(x) for x in ok_values])
    else:
        mean_val = 0
    return mean_val

def add_to_tables(conn, f1, f2, f3, pred_class, status):
    timestamp = time.time()
    cursor = conn.cursor()
    id = cursor.execute("SELECT COUNT() FROM classification_requests").fetchone()[0] + 1
    id_param = cursor.execute("SELECT COUNT() FROM classification_request_params").fetchone()[0] + 1

    cursor.execute("INSERT INTO classification_requests (id_request, request_timestamp,predicted_class,response_status,error_message) \
           VALUES ('%i', '%f', '%i', '%s', '0' )" % (id, timestamp, pred_class, status))

    conn.execute("INSERT INTO classification_request_params (id_request_param, id_request, param_name, param_value) \
            VALUES ({},{}, 'f1', {value})".format(id_param, id, value=f1))
    id_param += 1
    cursor.execute("INSERT INTO classification_request_params (id_request_param, id_request, param_name, param_value) \
                VALUES ({},{}, 'f2', {value})".format(id_param, id, value=f2))
    id_param += 1
    cursor.execute("INSERT INTO classification_request_params VALUES ('%i', '%i', 'f3', '%s')" %(id_param, id, f3))

    conn.commit()

    return

def compare_prediction_with_two_last(conn, pred):

    status = 'OK'

    # using increasing IDs
    # cursor = conn.cursor()
    # id = cursor.execute("SELECT COUNT() FROM classification_requests").fetchone()[0]
    #
    # cursor = conn.execute(
    #     "SELECT predicted_class from ('%s') WHERE id_request>= ('%i')" %(table, id-1))
    # values = cursor.fetchall()
    # conn.commit()
    # values = [x for t in values for x in t]
    # print("Table:", values)
    #
    # if all(x == pred for x in values):
    #     print("Last 3 are the same")

    if conn.execute("SELECT COUNT() FROM classification_requests").fetchone()[0] > 1:
        # use time stamp
        largest_time_id, largest_time, pred1 = conn.execute( \
                    "SELECT id_request, request_timestamp, predicted_class \
                    FROM classification_requests \
                    WHERE request_timestamp = (SELECT MAX(request_timestamp) \
                    FROM classification_requests)").fetchone()

        second_largest_time_id, second_largest_time, pred2 = conn.execute( \
                    "SELECT id_request, request_timestamp, predicted_class \
                    FROM classification_requests \
                    WHERE request_timestamp = (SELECT MAX(request_timestamp) FROM classification_requests \
                    WHERE (id_request < %i))" %(largest_time_id)).fetchone()
        # print("Largest time id:", largest_time_id, second_largest_time_id)
        # print("Largest times:", largest_time, second_largest_time)

        if pred == pred1 and pred == pred2:
            status = "WARNING"

    return status

