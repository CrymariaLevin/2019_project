__author__ = 'tangyj'


FOR_TEST = True
#FOR_TEST = False

if FOR_TEST:
    dbcfg = {
        "host": "39.105.9.20",
        "port": 3306,
        "user": "root",
        "pass": "bigdata_oil",
        "db": "cxd_data"
    }

else:
    dbcfg = {
        "host": "47.92.25.70",
        "port": 3306,
        "user": "root",
        "pass": "Wfn031641",
        "db": "cxd_data"
    }

