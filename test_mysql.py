#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from datetime import datetime as DT
from random import randint

test_phone_number = '+79115556688'

server_host = '192.168.1.57'
server_port = 3306
db_name = 'moop'
db_user = 'moop'
db_pass = 'moop'

conn = mysql.connector.connect(host = server_host, port = server_port, 
    database = db_name, user = db_user, password = db_pass)
cur = conn.cursor(dictionary = True)
print('paramstyle=', mysql.connector.paramstyle)
if not mysql.connector.paramstyle == 'pyformat':
    print('sql paramstyle = "{}" not supported.'.format(mysql.connector.paramstyle))

# insert
# cur.execute("""INSERT
                # INTO clients (`id`, `ls_number`, `phone_number`, `registration_date`)
                # VALUES (NULL, %(ls)s, %(phone)s, %(date)s)""",
            # {
                # 'ls' : randint(1000, 9999), 
                # 'phone' : '+79115556688', 
                # 'date' : DT.now().isoformat(sep = ' ', timespec = 'seconds')
            # }
            # )

# delete
#cur.execute('DELETE FROM clients WHERE phone_number=%s', (test_phone_number,))
#cur.execute("DELETE FROM clients WHERE registration_date='0000-00-00 00:00:00'")

#conn.commit()

# select
#cur.execute('SELECT * FROM clients WHERE phone_number=%s', (test_phone_number,))
#cur.execute('SELECT * FROM clients ORDER BY registration_date ASC WHRE')

# update
request_test = """UPDATE `meters` 
    SET `updated` = %(date)s, 
    `count` = %(count)s 
    WHERE `meters`.`id` = %(meter_id)s"""
cur.execute(request_test, {'date' : DT.now(), 'count' : 223, 'meter_id' : 3})

conn.commit()

request_text = """SELECT `clients`.`id` AS `client_id`,
    `clients`.`account`,
    `clients`.`phone_number`,
    `clients`.`registration_date`,
    `meters`.`id` AS `meter_id`,
    `meters`.`updated`,
    `meters`.`updated_from_db`,
    `meters`.`count`,
    `meters`.`count_from_db`,
    `pers_set`.`greeting_f`
    FROM `clients` 
    INNER JOIN `meters` ON `meters`.`owner_id` = `clients`.`id` AND `clients`.`phone_number`=%(phone)s
    LEFT JOIN `pers_set` ON `pers_set`.`phone_number`=%(phone)s"""

cur.execute(request_text, {'phone' : '+79115792506'})
for item in cur.fetchall():
    print('data:', item)