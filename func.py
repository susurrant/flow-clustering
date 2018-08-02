# -*- coding: utf-8 -*-：
# python 2.7

import csv
import random
import psycopg2
import os
import sys

def sample(p=0.05):
    with open('sample ' + str(p) + '.csv', 'wb') as rf:
        sheet = csv.writer(rf)
        with open('taxi data(May 13)_processed.csv', 'r') as f:
            while True:
                line = f.readline().strip()
                if line:
                    if random.random() < p:
                        d = line.split(',')
                        sheet.writerow(d)
                else:
                    break
        
def stDataPreProcess(sourceFile, dataFile, wdFile, path):
    # 1、去除od重合、经纬度为0、时段重合的点
    # 2、添加gid
    # 3、将数据导入数据库
    print 'Running ', sys.argv[0]

    if not os.path.exists(dataFile):
        rf = file(dataFile, 'wb')
        sheet = csv.writer(rf)

        wf = file(wdFile, 'wb')
        wsheet = csv.writer(wf)

        with open(sourceFile, 'r') as f:
            i = 0
            while True:
                line = f.readline().strip()
                if line:
                    dl = line.split(',')
                    flag = False
                    wc = ''
                    if abs(float(dl[0]) - float(dl[2])) < 0.00001 and abs(float(dl[1]) - float(dl[3])) < 0.00001:
                        flag = True
                        wc = 'points coincide'
                    if float(dl[0]) == 0 or float(dl[2]) == 0 or float(dl[1]) == 0 or float(dl[3]) == 0:
                        flag = True
                        wc = 'null coordinates'
                    if int(dl[4]) >= int(dl[5]):
                        flag = True
                        wc = 'equal times'

                    if flag:
                        dl.insert(0, wc)
                        wsheet.writerow(dl)
                        continue

                    dl.insert(0, i)
                    i += 1
                    sheet.writerow(dl)
                else:
                    break

        rf.close()
        wf.close()

    conn = psycopg2.connect(database="flow clustering", user="postgres", password="123", host='localhost', port="5432")
    cur = conn.cursor()

    cur.execute('DELETE FROM taxi_odt;')
    cur.execute('ALTER TABLE taxi_odt DROP COLUMN midpnt;')
    cur.execute('copy taxi_odt from \''+ path + dataFile + '\' with csv;')
    cur.execute('ALTER TABLE taxi_odt ADD COLUMN midpnt geometry(POINT, 32650);')
    cur.execute(
        r"UPDATE taxi_odt SET midpnt = St_Transform(st_geomfromtext('POINT('||to_char((ox+dx)/2.0,'999D999999')||' '||to_char((oy+dy)/2.0,'99D999999')||')',4326),32650);")
    cur.execute('create index idx_mp1 on taxi_odt using gist(midpnt);')
    # cur.execute('VACUUM ANALYZE taxi_odt (midpnt);') #在数据库中手动执行
    conn.commit()
    cur.close()
    conn.close()

def impCluster2DB(clusterFile, path):
    print 'Import cluster data to database...'
    print 'sourcefile:', clusterFile
    print 'Database: flow clustering, Table: cluster'
    conn = psycopg2.connect(database="flow clustering", user="postgres", password="123", host='localhost', port="5432")
    cur = conn.cursor()

    cur.execute('DELETE FROM cluster;')
    cur.execute('ALTER TABLE cluster DROP COLUMN geom;')
    cur.execute('copy cluster from \'' + path + clusterFile + '\' with csv header;')
    cur.execute('ALTER TABLE cluster ADD COLUMN geom geometry(LineString,4326);')
    cur.execute(
        r"UPDATE cluster SET geom=st_geomfromtext('LINESTRING('||to_char(ox,'999999D999999')||' '||to_char(oy,'9999999D99999')||','||to_char(dx,'999999D999999')||' '||to_char(dy,'9999999D99999')||')',4326);")

    conn.commit()
    cur.close()
    conn.close()

    print '\nFinished!'


def impLData2DB(labeleddataFile, path):
    print 'Import labeled data to database...'
    print 'sourcefile:', labeleddataFile
    print 'Database: flow clustering, Table: stlflow'
    conn = psycopg2.connect(database="flow clustering", user="postgres", password="123", host='localhost', port="5432")
    cur = conn.cursor()

    cur.execute('DELETE FROM stlflow;')
    cur.execute('ALTER TABLE stlflow DROP COLUMN geom;')
    cur.execute('copy stlflow from \'' + path + labeleddataFile + '\' with csv header;')
    cur.execute('ALTER TABLE stlflow ADD COLUMN geom geometry(LineString,4326);')
    cur.execute(
        r"UPDATE stlflow SET geom=st_geomfromtext('LINESTRING('||to_char(x1,'999999D999999')||' '||to_char(y1,'9999999D99999')||','||to_char(x2,'999999D999999')||' '||to_char(y2,'9999999D99999')||')',4326);")

    conn.commit()
    cur.close()
    conn.close()

    print '\nFinished!'


def impData2DB(dataFile, path):
    print 'Import labeled data to database...'
    print 'sourcefile:', dataFile
    print 'Database: flow clustering, Table: flow'
    conn = psycopg2.connect(database="flow clustering", user="postgres", password="123", host='localhost', port="5432")
    cur = conn.cursor()

    cur.execute('DELETE FROM flow;')
    cur.execute('ALTER TABLE flow DROP COLUMN geom;')
    cur.execute('copy flow from \'' + path + dataFile + '\' with csv header;')
    cur.execute('ALTER TABLE flow ADD COLUMN geom geometry(LineString,4326);')
    cur.execute(
        r"UPDATE flow SET geom=st_geomfromtext('LINESTRING('||to_char(x1,'999999D999999')||' '||to_char(y1,'9999999D99999')||','||to_char(x2,'999999D999999')||' '||to_char(y2,'9999999D99999')||')',4326);")

    conn.commit()
    cur.close()
    conn.close()

    print '\nFinished!'


if __name__ == '__main__':
    # sample()


    path = './data/'

    # sourceFile = 'taxi data(May 13)_raw.csv'
    # dataFile = 'taxi data(May 13)_processed.csv'
    # wdFile = 'taxi data(May 13)_wrong.csv'
    # stDataPreProcess(sourceFile, dataFile, wdFile, path)

    impCluster2DB('tem_s_c(May 13) 25 4.0.csv', path)
    # impData2DB('sample 0.05.csv', path)
