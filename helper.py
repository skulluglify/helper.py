#! /usr/bin/env python

import os, ctypes#, time
from typing import Any
import mysql.connector
from mysql.connector import (connection)
from multiprocessing import Process, Value, Queue, Lock, Manager
from serverApi import ServerApi

from tools import parseIntAuto

user: str =  os.getenv("MYSQL_USER")
password: str = os.getenv("MYSQL_PASSWORD")
host: str = os.getenv("MYSQL_HOST")
database: str = os.getenv("MYSQL_DATABASE")

serverApiConfig: dict = {}

serverApiConfig.update({

    "host": os.getenv("API_HOST") or "127.0.0.1",
    "port": os.getenv("API_PORT") or "5000"
})

## ifconfig | grep -i inet  | grep -i 192 | awk '{print $2}'

"""
?SERVER API RUN WITH MULTIPROCESSING AND COMMUNICATE DATABASE LOCAL SERVER
"""
def serverApiMp(host: Value, port: Value, data: Any, queue: Queue, lock: Lock):

    api: ServerApi = ServerApi() ## bypass
    route: Any = api.routeJSON(methods=["GET", "POST"])

    def request(req: str, response: Any):

        timeout: int = 1e3 * 5e3

        while True:

            if timeout <= 0:

                break

            if queue.empty():

                queue.put(req)
                data.update({

                    "request": True,
                    "body": response

                })

                return True

            else:

                ## conflict taskl
                ## delete all taskl

                while not queue.empty():

                    queue.get()

            timeout -= 1

        return False

    def wrapper(path, response):
        
        post: bool = False
        
        match(path):
            
            case "maps":
                
                with lock:

                    post = request("SELECT", response)

            case "registry":
                
                with lock:

                    post = request("INSERT", response)

            case "update":
                
                with lock:

                    post = request("UPDATE", response)

            case "remove":
                
                with lock:

                    post = request("DELETE", response)
            
            case "test":

                return {

                    "code": 1,
                    "status": "done",
                    "message": "say hello!",
                    "dataModels": [
                        {
                            "fd_id": 1,
                            "fd_name": "jagung bakar",
                            "fd_stock": 12,
                            "fd_price": 12000,
                            "fd_chef": "ahmad asy syafiq",
                            "fd_sale": 12
                        }
                    ]
                }
                
        if post:

            timeout: int = 1e3 * 5e3

            while True:

                if timeout <= 0:

                    break

                if data["response"]:
                    data["response"] = False
                    break

                timeout -= 1

            timeout = 1e3 * 5e3

            while True:

                if timeout <= 0:

                    break

                if not queue.empty():

                    check: str = queue.get()

                    if check in ("DONE",):

                        return data["body"]
                    
                    else:

                        queue.put_nowait(check)

                        break

                timeout -= 1

            return {}


    route(wrapper)
    api.run(host = host.value, port = port.value)
    # with subprocess.Popen("ifconfig | grep -i inet  | grep -i 192 | head -n 1 | awk '{print $2}'", stderr = subprocess.PIPE, stdout = subprocess.PIPE, stdin = subprocess.PIPE, shell = True) as process:
# 
        # host: str = process.stdout.read().decode("utf-8")
# 
        # if (len(host)):
# 
            # print(host)
            # api.run(host = host)
# 
        # else:
# 
            # print("cannot read ip route!")
            # exit()

"""
?MYSQL CONNECTOR CONNECT TO LOCAL SERVER AND COMMUNICATE TO THE SERVER API
"""
if str(__name__).upper() in ("__MAIN__",):

    try:

        cnx = connection.MySQLConnection(user = user, password = password, host = host, database = database, raise_on_warnings = True, use_pure = False)

        try:

            cursor = cnx.cursor(raw = True)

            try:

                def rawQuery(cursor: Any):

                    raws: Any = [ data for data in cursor ]

                    data: list = [ \
                        tuple( \
                            map(lambda x: parseIntAuto(x) \
                                if not type(x) is bytearray else \
                                    parseIntAuto(x.decode("utf-8")),  \
                            data)) \
                        if type(data) in (tuple, list) else \
                            [ \
                            \
                            \
                            \
                            \
                            ] \
                        for data in raws \
                    
                    ]

                    return data

                def select_all_from_table():

                    cursor.execute("SELECT * FROM `fd_table`;")

                    return rawQuery(cursor)

                def demand_body_custom(body: Any):

                    if type(body) is dict:

                        attrs: list = [
                            "fd_name",
                            "fd_stock",
                            "fd_price",
                            "fd_chef",
                            "fd_sale"
                        ]

                        return dict([ (k, v) for (k, v) in body.items() if k in attrs ])

                    return {}

                def insert_in_table(body: Any):

                    if type(body) is dict:

                        data: dict = demand_body_custom(body)

                        ## INSERT INTO `fd_table` (`fd_id`, `fd_name`, `fd_stock`, `fd_price`, `fd_chef`, `fd_sale`) VALUES (NULL, 'sosis', '64', '6000', 'udin', '0');

                        def set_default(key: str, value: str | int):

                            if (not key in data):

                                data.__setitem__(key, value)

                        set_default("fd_name" , "unknown")
                        set_default("fd_stock", 0)
                        set_default("fd_price", 0)
                        set_default("fd_chef" , "unknown")
                        set_default("fd_sale" , 0)

                        keys: str = str.join(",", map(lambda x : "`{}`".format(x), data.keys()))
                        values: str = str.join(",", map(lambda x : "'{}'".format(x), data.values()))

                        context: str = "INSERT INTO `fd_table` (`fd_id`,{}) VALUES (NULL,{});".format(keys, values)

                        print(context)

                        cursor.execute(context)

                        return {

                            "code": 1,
                            "status": "done",
                            "message": "maybe was inserting",
                            "dataModels": [ data ]
                        }

                    return {

                        "code": 0,
                        "status": "dump",
                        "message": "failed",
                        "dataModels": []
                    }
                
                def demand_where_custom(where: dict):

                    where = demand_body_custom(where)

                    def whatisit(c: Any):

                        if type(c) is str:

                            return "'{}'".format(c)

                        if type(c) is int:

                            return str(c)
                        
                        return None;

                    return str.join(" and ", [ \
                        str.join("=", [ \
                            "`fd_table`.`{}`".format(x.__getitem__(0)), \
                            whatisit(x.__getitem__(1)) \
                        ]) \
                        for x in where.items() \
                        if whatisit(x.__getitem__(1)) \
                    ])

                def _zip(*args):

                    size: int = len(args[0])

                    return [ \
                        tuple(x[i] for x in args) \
                        for i in range(size) \
                    ]

                def raws_to_json(raws: list):

                    def make_json(data: list):

                        default_keys: list = [

                            "fd_id",
                            "fd_name",
                            "fd_stock",
                            "fd_price",
                            "fd_chef",
                            "fd_sale"
                        ]

                        return dict(_zip(default_keys, data))

                    return [ make_json(data) for data in raws ]

                def select_from_table(body: Any):

                    if type(body) is dict:

                        if "where" in body:

                            where: Any = body.__getitem__("where")

                            if type(where) is dict:

                                wheres: str = demand_where_custom(where)

                                wheres: str = "WHERE {}".format(wheres)

                                context = "SELECT * FROM `fd_table` {};".format(wheres)

                                print(context)

                                cursor.execute(context)

                                return {

                                    "code": 2,
                                    "status": "successfull",
                                    "message": "select in condition",
                                    "dataModels": raws_to_json(rawQuery(cursor))
                                }

                    return {

                        "code": 1,
                        "status": "done",
                        "message": "warning, load alls make buffer flow!",
                        "dataModels": raws_to_json(select_all_from_table())
                    }

                def update_in_table(body: Any):

                    if type(body) is dict:

                        if "where" in body:

                            where: Any = body.__getitem__("where")

                            if type(where) is dict:

                                where = demand_body_custom(where)

                                wheres: str = demand_where_custom(where)

                                wheres: str = "WHERE {}".format(wheres)

                                data: dict = demand_body_custom(body)

                                items: str = str.join(",", map(lambda x: str.join("=", [ \
                                    "`{}`".format(x.__getitem__(0)), \
                                    "'{}'".format(x.__getitem__(1)) \
                                ]), data.items()))

                                context = "UPDATE `fd_table` SET {} {};".format(items, wheres)

                                print(context)

                                cursor.execute(context)

                                return {

                                    "code": 2,
                                    "status": "success",
                                    "message": "has been update",
                                    "dataModels": [
                                        dict(data).update(where)
                                    ]
                                }

                        return {

                            "code": 1,
                            "status": "done",
                            "message": "nothing todo",
                            "dataModels": []
                        }

                    return {

                        "code": 0,
                        "status": "dump",
                        "message": "failed",
                        "dataModels": []
                    }

                def delete_in_table(body: Any):

                    if type(body) is dict:

                        if "where" in body:

                            where: Any = body.__getitem__("where")

                            if type(where) is dict:

                                wheres: str = demand_where_custom(where)

                                wheres: str = "WHERE {}".format(wheres)

                                context = "DELETE FROM `fd_table` {};".format(wheres)

                                print(context)

                                cursor.execute(context)

                                return {

                                    "code": 2,
                                    "status": "success",
                                    "message": "has been remove",
                                    "dataModels": []
                                }

                        return {

                            "code": 1,
                            "status": "done",
                            "message": "nothing todo",
                            "dataModels": []
                        }

                    return {

                        "code": 0,
                        "status": "dump",
                        "message": "failed",
                        "dataModels": []
                    }

                with Manager() as manager:

                    d: Any = manager.dict()

                    print(str.join(":", serverApiConfig.values()))

                    serverApiHost: Value = Value(ctypes.c_wchar_p, serverApiConfig.__getitem__("host"))
                    serverApiPort: Value = Value(ctypes.c_wchar_p, serverApiConfig.__getitem__("port"))

                    queue: Queue = Queue()
                    lock: Lock = Lock()

                    d["request"] = False
                    d["response"] = False
                    d["body"] = {}

                    t: Process = Process(target=serverApiMp, args=(serverApiHost, serverApiPort, d, queue, lock))

                    t.start()

                    print("PID", t.pid)

                    def response(body: dict):

                            d.update(body)

                            queue.put("DONE")

                            d["request"] = False
                            d["response"] = True

                            print("SEND DATA")

                    while True:

                        if d["request"]:

                            with lock:

                                if not queue.empty():

                                    post: str = queue.get()

                                    print(post)

                                    match(post):

                                        case "SELECT":

                                            response({

                                                "body": select_from_table(d["body"])

                                            })

                                        case "INSERT":

                                            response({

                                                "body": insert_in_table(d["body"])

                                            })

                                        case "UPDATE":

                                            response({

                                                "body": update_in_table(d["body"])

                                            })

                                        case "DELETE":

                                            response({

                                                "body": delete_in_table(d["body"])

                                            })
                            
                            timeout: int = 1e3 * 5e3

                            while True:

                                if timeout <= 0:

                                    break

                                if not d["response"]:

                                    break

                                timeout -= 1

                        if type(t.exitcode) is int:

                            print("GOOD BYE!")
                            break

            finally:

                if hasattr(cursor, "close"):
                    cursor.close()

        finally:

            if hasattr(cnx, "commit"):
                cnx.commit()

            if hasattr(cnx, "close"):
                cnx.close()

    except mysql.connector.Error as err:

        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:

            print("Something is wrong with your user name or password")

        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:

            print("Database does not exist")

        else:

            print(err)
