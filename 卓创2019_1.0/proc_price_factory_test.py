# coding=utf-8

__author__ = 'tangyj'

import pandas as pd
import numpy as np
import redis
import os
import pymysql
from pandas import Timestamp
from bson import ObjectId
from sqlalchemy import create_engine, MetaData
import robint
import logging
import re
from dbconf_t import *
import glob

logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("cxd_todb")

g_rtr = robint.RunTimer()

DBCONSZ = "mysql+pymysql://{0}:{1}@{2}:{3}/{4}?charset=utf8"\
    .format(dbcfg["user"], dbcfg["pass"], dbcfg["host"], dbcfg["port"], dbcfg["db"])
ENGINE = create_engine(DBCONSZ, echo=False)
METADATA = MetaData(ENGINE)
logger.info("{0}: {1}".format(__name__, DBCONSZ))

g_rcli_k = redis.Redis(decode_responses=True, db=1)
g_rcli_v = redis.Redis(decode_responses=True, db=2)

g_runt = robint.RunTimer()

g_dic_province = {}
g_dic_province_s = {}
g_dic_region = {}
g_dic_key = {}
g_dic_value = {}

def _init_dics():
    global g_dic_province
    global g_dic_province_s
    global g_dic_region
    global g_dic_key
    global g_dic_value

    df_dic_province = pd.read_sql("select * from dic_province", ENGINE)
    g_dic_province = dict(zip(df_dic_province["name"], df_dic_province["id"]))
    g_dic_province_s = dict(zip(df_dic_province["s_name"], df_dic_province["id"]))

    df_dic_region = pd.read_sql("select * from dic_region", ENGINE)
    g_dic_region = dict(zip(df_dic_region["name"], df_dic_region["id"]))

    df_dic_key = pd.read_sql("select id, factory, type from out_price_factory_key where source_id = 3", ENGINE)
    sr_dic_id = df_dic_key["id"]
    sr_dic_fac = df_dic_key["factory"]
    sr_dic_type = df_dic_key["type"]
    g_dic_key = dict(zip(sr_dic_fac + "/" + sr_dic_type, sr_dic_id))

    df_dic_value = pd.read_sql("""select id, ref_key_id, date from out_price_factory_value where ref_key_id in
    (select distinct id from out_price_factory_key where source_id = 3)""", ENGINE)
    sr_dic_ref = df_dic_value["ref_key_id"]
    sr_dic_date = df_dic_value["date"].map(str)
    g_dic_value = dict(zip(sr_dic_ref + "/" + sr_dic_date, df_dic_value["id"]))

ReBadProvinceName = re.compile("\[\d+\]\s+(.*)")

def get_province_id(pname):
    if pd.isnull(pname):
        return None
    m = ReBadProvinceName.match(pname)
    if m: pname = m.group(1)
    if pname in g_dic_province:
        return g_dic_province[pname]
    elif pname in g_dic_province_s:
        return g_dic_province_s[pname]
    elif pname[-1] == "省": # 例如广西省
        return g_dic_province_s[pname[:-1]]
    return None

# 生成 企业名称/品类的 key
def gen_df_name_key(df_in, cols, sep="/"):
    return df_in[cols].apply(lambda s: "/".join([str(i) for i in s]), axis=1)

# add id
def make_df_object_id(df_in, id_name="id", id_dic=None, sr_key=None, cols=None, sep="/"):
    df_out = df_in.copy()
    if id_dic: # 有字典
        if sr_key is None and cols: # 没key，尝试生成key
            sr_key = gen_df_name_key(df_out, cols, sep)
        if sr_key is not None and len(sr_key) == len(df_out):
            lst_id = sr_key.map(lambda k: id_dic[k] if k in id_dic else str(ObjectId()))
            df_out[id_name] = lst_id
            return df_out
        else:
            print("invalid param: id_dic={0}, sr_key={1}, cols={2}, sep={3}"\
                .format(id_dic, sr_key, cols, sep))
    # 默认情况，是全自动生成
    df_out[id_name] = [str(ObjectId()) for i in range(len(df_out))]
    return df_out

# # proc key table
# def proc_df_factory_key(df_in, name, fac_type):
#     df_key = df_in.copy()
#     df_key["r_id"] = df_key["区域"].map(lambda r: g_dic_region.get(r))
#     df_key["province_id"] = df_key["省"].map(get_province_id)
#     df_key["source_id"] = [3] * len(df_key)
#     df_key["factory_type"] = [fac_type] * len(df_key)
#     return df_key
#
# # proc value table
# def proc_df_factory_value(df_in, scope=(4,12), ref_name="id", unit="元/吨", duration="1d"):
#     df_tmp = df_in.iloc[:, scope[0]:scope[1]]
#     del df_tmp["涨跌"]
#     del df_tmp["单位"]
#
#     df_tmp = df_tmp.set_index(ref_name)
#     sr_tmp = df_tmp.stack()
#     sr_tmp.index = sr_tmp.index.set_names(names=["ref_key_id", "date"])
#     df_val = sr_tmp.to_frame(name="price")
#     df_val = df_val.reset_index()
#     df_val["unit"] = [unit] * len(df_val)
#     df_val["duration"] = [duration] * len(df_val)
#
#     return df_val

def batch_oil_history_data(infile, outfile_pre, infile_ext=".xlsx", outfile_ext=".xlsx",
                           duration="1d", fac_type="主营炼厂", good_type="汽油"):
    # 读入数据
    if infile_ext.lower() == ".csv":
        df_raw = pd.read_csv(infile, engine="python") # 得设定engine为python
    else:
        df_raw = pd.read_excel(infile)
    df_raw = df_raw[(df_raw["平均价"].notnull() & df_raw["产品名称"].notnull())] # 价格数据不能为空，减少冗余数据录入
    if "产品名称" not in df_raw.columns:
        df_raw["产品名称"] = [good_type] * len(df_raw)

    # 创建key表
    df_key = df_raw[["区域", "省", "市", "生产企业", "产品名称", "型号"]].copy()

    # 取出无重复的id区分信息
    grp_key = df_key.groupby(["生产企业", "型号"])
    lst_idx = []
    for k, v in grp_key.groups.items():
        lst_idx.append(v[0])
    df_key = df_key.loc[lst_idx]

    # 填充附属信息
    df_key["r_id"] = df_key["区域"].map(lambda r: g_dic_region.get(r))
    df_key["province_id"] = df_key["省"].map(get_province_id)
    df_key["source_id"] = [3] * len(df_key)
    df_key["factory_type"] = [fac_type] * len(df_key)

    # 复用或生成key表记录的id
    sr_key = gen_df_name_key(df_key, cols=["生产企业", "型号"])
    df_key = make_df_object_id(df_key, id_name="id", id_dic=g_dic_key, sr_key=sr_key)

    # 更新 生产企业/型号 => key_id 的字典
    dic_key_id = dict(zip(sr_key, df_key["id"]))
    g_dic_key.update(dic_key_id)
    g_rcli_k.mset(dic_key_id)

    # 创建value表
    df_value = df_raw[["生产企业", "型号", "时间", "平均价", "单位"]].copy()

    # 填充附属信息
    df_value["duration"] = [duration] * len(df_value)
    df_value["date"] = df_value["时间"].map(np.datetime64)

    # 填充ref的id值
    sr_value_ref_txt = gen_df_name_key(df_value, cols=["生产企业", "型号"])
    sr_value_ref_id = sr_value_ref_txt.map(lambda k: g_dic_key.get(k))
    df_value["ref_key_id"] = sr_value_ref_id
    # df_value = df_value.dropna()

    # 复用或生成value表记录的id
    sr_value = gen_df_name_key(df_value, cols=["ref_key_id", "时间"])
    df_value = make_df_object_id(df_value, id_dic=g_dic_value, sr_key=sr_value)

    # 更新 ref_key_id/date => key_id 的字典
    dic_value_id = dict(zip(sr_value, df_value["id"]))
    g_dic_value.update(dic_value_id)
    g_rcli_v.mset(dic_value_id)

    # 重命名列名
    df_key.rename(columns={'区域':'region', '生产企业':'factory', '产品名称':'name', '型号':'type'}, inplace=True)
    df_value.rename(columns={'平均价':'price', '单位':'unit'}, inplace=True)

    df_key.to_excel(outfile_pre+"_key"+outfile_ext)
    df_value.to_excel(outfile_pre+"_value"+outfile_ext)

    return df_key, df_value

# def job_20180601():
#     # lst_good = ["MTBE", "天然气", "沥青", "燃料油", "芳烃"]
#     lst_good = ["天然气", "沥青", "燃料油", "芳烃"]
#     lst_info = [good+"_主营出厂价_全国_2017-1-1_2018-6-1" for good in lst_good]
#     infile_pre = "./20180601/卓创_价格_"
#     infile_ext = ".xls"
#     outfile_pre = "./20180601/output/out_price_"
#     outfile_ext = ".xls"
#
#     lst_ret = []
#     for i in range(len(lst_good)):
#         g_runt.begin("proc_{0}".format(lst_good[i]))
#         k, v = batch_oil_history_data(infile_pre+lst_info[i]+infile_ext, outfile_pre+lst_good[i], outfile_ext)
#         g_runt.end()
#         lst_ret.append((k, v))
#         if lst_good[i] == "MTBE":
#             # print(v)
#             # v.to_pickle("./pd_tmp.pkl")
#             v.to_pickle("./20180601/pd_MTBE.pkl")

COLS_KEY = ["id", "region", "factory", "name", "type", "province_id", "r_id", "source_id", "factory_type"]
COLS_VALUE = ["id", "date", "price", "unit", "ref_key_id", "duration"]

def translate_key(v):
    if pd.isnull(v):
        return None
    elif isinstance(v, np.float64):
        return float(v)
    elif isinstance(v, np.int64):
        return int(v)
    else:
        return v

def upsert_key(sr):
    lst_col = COLS_KEY.copy()
    lst_val = ["%s"] * len(lst_col)
    lst_upd = ["{0}=%s".format(col) for col in lst_col]
    sql = "insert into out_price_factory_key ({0}) values ({1}) on duplicate key update {2}"\
        .format(",".join(lst_col), ",".join(lst_val), ",".join(lst_upd))
    par = sr[lst_col].map(translate_key).tolist() * 2

    conn = ENGINE.raw_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql, par)
        conn.commit()
    except pymysql.Error as ex:
        logger.error("upsert_key(), MySql Error: %s, data=%s" % (ex, par))
    except Exception as ex:
        logger.error("upsert_key(), Other Error: %s" % ex)
    finally:
        cur.close()
        conn.close()

def translate_value(v):
    if pd.isnull(v):
        return None
    elif isinstance(v, Timestamp):
        return v.strftime("%Y-%m-%d")
    elif isinstance(v, np.float64):
        return float(v)
    elif isinstance(v, np.int64):
        return int(v)
    else:
        return v

def upsert_value(sr):
    lst_col = COLS_VALUE.copy()
    lst_val = ["%s"] * len(lst_col)
    lst_upd = ["{0}=%s".format(col) for col in lst_col]
    sql = "insert into out_price_factory_value ({0}) values ({1}) on duplicate key update {2}"\
            .format(",".join(lst_col), ",".join(lst_val), ",".join(lst_upd))
    par = sr[lst_col].map(translate_value).tolist() * 2

    conn = ENGINE.raw_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql, par)
        conn.commit()
    except pymysql.Error as ex:
        logger.error("upsert_value(), MySql Error: %s, data=%s" % (ex, par))
    except Exception as ex:
        logger.error("upsert_value(), Other Error: %s" % ex)
    finally:
        cur.close()
        conn.close()

def job_common(lst_good_ftype, infile_pre, outfile_pre, outdir, infile_ext=".xls", outfile_ext=".xls"):
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    for good, ftype, gtype in lst_good_ftype:
        infile = infile_pre + good + infile_ext
        outfile = outfile_pre + good + outfile_ext
        # k, v = batch_oil_history_data(infile, outfile_pre, outfile_ext)
        g_rtr.begin("proc {0}".format(good))
        k, v = batch_oil_history_data(infile, outfile, infile_ext=infile_ext,
                                      outfile_ext=outfile_ext, fac_type=ftype, good_type=gtype)
        g_rtr.end()

        # continue

        g_rtr.begin("upsert_key {0}".format(good))
        k = k[(k["name"] != "") & (k["factory"] != "")]
        logger.info("{0}: to upsert {1} keys".format(good, len(k)))
        step = len(k)//10
        step = step if step > 0 else 1
        for i in range(len(k)):
            upsert_key(k.iloc[i])
            if (i+1) % step == 0:
                logger.info("{0}: upserted {1}% {2}/{3} keys"
                            .format(good, (i+1)*100/len(k), (i+1), len(k)))
        g_rtr.end()
        g_rtr.begin("upsert_value {0}".format(good))
        # v = v.dropna()
        v = v[v["price"].notnull()]
        logger.info("{0}: to upsert {1} values".format(good, len(v)))
        step = len(v)//10
        step = step if step > 0 else 1
        for i in range(len(v)):
            upsert_value(v.iloc[i])
            if (i+1) % step == 0:
                logger.info("{0}: upserted {1}% {2}/{3} values"
                          .format(good, (i+1)*100/len(v), (i+1), len(v)))
        g_rtr.end()


# def job_20180606():
#     lst_good_ftype = [
#         ("成品油_2018-06-01_2018-06-07", "主营炼厂"),
#         ("燃料油_2018-06-07", "主营炼厂")
#     ]
#     # infile = "./20180606/卓创_价格_燃料油_2018-06-01_2018-06-06.xls"
#     infile_pre = "./20180606/卓创_价格_"
#     # outfile_pre = "./20180606/output/out_price_燃料油"
#     outfile_pre = "./20180606/output/out_price_"
#     outdir = "./20180606/output"
#     job_common(lst_good_ftype, infile_pre, outfile_pre, outdir)
#
# def job_20180608():
#     lst_good_ftype = [
#         ("主营柴油_2018-05-31", "主营炼厂"),
#         ("主营汽油_2018-05-31", "主营炼厂"),
#         # ("主营柴油_2018-06-01", "主营炼厂"),
#         # ("地炼柴油_2017-01-01", "地方炼厂"),
#         # ("地炼汽油_2017-01-01_part1", "地方炼厂"),
#         # ("地炼汽油_2017-01-01_part2", "地方炼厂"),
#     ]
#     # infile = "./20180606/卓创_价格_燃料油_2018-06-01_2018-06-06.xls"
#     infile_pre = "./20180608/卓创_价格_"
#     # outfile_pre = "./20180606/output/out_price_燃料油"
#     outfile_pre = "./20180608/output/out_price_"
#     outdir = "./20180608/output"
#     job_common(lst_good_ftype, infile_pre, outfile_pre, outdir)
#
# def job_20180609():
#     lst_good_ftype = [
#         ("成品油_2018-06-08", "主营炼厂"),
#         ("燃料油_2018-06-08", "主营炼厂"),
#     ]
#     infile_pre = "./20180608/卓创_出厂价格_"
#     outfile_pre = "./20180608/output/out_price_"
#     outdir = "./20180608/output"
#     job_common(lst_good_ftype, infile_pre, outfile_pre, outdir)
#
# def job_20180611():
#     lst_good_ftype = [
#         # ("成品油_2018-05-20", "主营炼厂"),
#         # ("成品油_2018-06-09_2018-06-11", "主营炼厂"),
#         # ("燃料油_2018-06-09_2018-06-11", "主营炼厂"),
#         ("主营柴油_2018-05-15", "主营炼厂"),
#         ("地炼柴油_2018-05-15", "地方炼厂"),
#     ]
#     infile_pre = "./20180611/卓创_出厂价格_"
#     outfile_pre = "./20180611/output/out_price_"
#     outdir = "./20180611/output"
#     job_common(lst_good_ftype, infile_pre, outfile_pre, outdir)
#
# def job_20180612():
#     lst_good_ftype = [
#         # ("地炼柴油_2018-05-28_2018-06-12", "地方炼厂"),
#         # ("地炼汽油_2018-05-28_2018-06-12", "地方炼厂"),
#         # ("煤油_2018-05-28_2018-06-12", "主营炼厂"),
#         # ("燃料油_2018-05-28_2018-06-12", "主营炼厂"),
#         ("主营92#汽油_2018-05-28_2018-06-12", "主营炼厂"),
#         ("主营95#汽油_2018-05-28_2018-06-12", "主营炼厂"),
#         ("主营柴油_2018-05-28_2018-06-12", "主营炼厂"),
#     ]
#     infile_pre = "./20180612/卓创_出厂价格_"
#     outfile_pre = "./20180612/output/out_price_"
#     outdir = "./20180612/output"
#     job_common(lst_good_ftype, infile_pre, outfile_pre, outdir)
#
# def job_20180613():
#     lst_good_ftype = [
#         ("地炼柴油_2018-05-29_2018-06-13", "地方炼厂"),
#         ("地炼汽油_2018-05-29_2018-06-13", "地方炼厂"),
#         ("煤油_2018-05-29_2018-06-13", "主营炼厂"),
#         ("燃料油_2018-05-29_2018-06-13", "主营炼厂"),
#         ("主营92#汽油_2018-05-29_2018-06-13", "主营炼厂"),
#         ("主营95#汽油_2018-05-29_2018-06-13", "主营炼厂"),
#         ("主营柴油_2018-05-29_2018-06-13", "主营炼厂"),
#     ]
#     infile_pre = "./20180613/卓创_出厂价格_"
#     outfile_pre = "./20180613/output/fty_"
#     outdir = "./20180613/output"
#     job_common(lst_good_ftype, infile_pre, outfile_pre, outdir)
#
# def job_20180615():
#     lst_good_ftype = [
#         ("地炼柴油_2018-05-31_2018-06-15", "地方炼厂"),
#         # ("地炼汽油_2018-05-31_2018-06-15", "地方炼厂"),
#         # ("煤油_2018-05-31_2018-06-15", "主营炼厂"),
#         # ("燃料油_2018-05-31_2018-06-15", "主营炼厂"),
#         # ("主营92#汽油_2018-05-31_2018-06-15", "主营炼厂"),
#         # ("主营95#汽油_2018-05-31_2018-06-15", "主营炼厂"),
#         # ("主营柴油_2018-05-31_2018-06-15", "主营炼厂"),
#     ]
#     infile_pre = "./20180615/卓创_出厂价格_"
#     outfile_pre = "./20180615/output/fty_"
#     outdir = "./20180615/output"
#     job_common(lst_good_ftype, infile_pre, outfile_pre, outdir)

ReGoodInFile = re.compile(r".+卓创_出厂价格_(.+)(\.[a-z]+)")
ReGoodType = re.compile(r".*(汽油|柴油|煤油|燃料油|芳烃|沥青|MTBE).*")

def get_good_type(text):
    m = ReGoodType.match(text)
    if m:
        return m.group(1)
    else:
        return None

def job_datadir(datadir):
    # lst_file = glob.glob("{0}/卓创_出厂价格_*.*".format(datadir))
    # infile_ext = ".xls"
    # if not lst_file:
    #     lst_file = glob.glob("{0}/卓创_出厂价格_*.csv".format(datadir))
    #     infile_ext = ".csv"
    lst_file = glob.glob("{0}/卓创_出厂价格_*.*".format(datadir))
    print(lst_file)
    infile_ext = None
    lst_good = []
    for fn in lst_file:
        m = ReGoodInFile.match(fn)
        if not m: continue
        ftype = "地方炼厂" if "地炼" in fn else "主营炼厂"
        infile_ext = infile_ext if infile_ext else m.group(2)
        lst_good.append((m.group(1), ftype, get_good_type(fn)))
    if not lst_good:
        logger.warning("job_datadir(), no datafile in {0}".format(datadir))
        return
    # print(lst_good)
    infile_pre = "{0}/卓创_出厂价格_".format(datadir)
    outfile_pre = "{0}/output/fty_t_".format(datadir)
    outdir = "{0}/output".format(datadir)
    job_common(lst_good, infile_pre, outfile_pre, outdir, infile_ext=infile_ext)

def init_data():
    g_runt.begin("_init_dics")
    _init_dics()
    g_runt.end()

if __name__ == "__main__":
    init_data()

    # job_20180601()
    # job_20180606()
    # job_20180608()
    # job_20180609()
    # job_20180611()
    # job_20180612()
    # job_20180613()
    # job_20180615()
    job_datadir("./20180617")
