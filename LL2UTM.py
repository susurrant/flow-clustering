#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

import math

# 常量定义
a_84 = 6378137.0
b_84 = 6356752.3142451
f_84 = (a_84 - b_84)/a_84
lonOrigin_Beijing = 117.0

# for convenient only
sin = math.sin
cos = math.cos
tan = math.tan
sqrt = math.sqrt
radians = math.radians
degrees = math.degrees
pi = math.pi


def LL2UTM_USGS(lat, lon, lonOrigin=117, FN=0):
    '''
    ** Input：(a, f, lat, lon, lonOrigin, FN)
    ** a 椭球体长半轴
    ** f 椭球体扁率 f=(a-b)/a 其中b代表椭球体的短半轴
    ** lat 经过UTM投影之前的纬度（角度）
    ** lon 经过UTM投影之前的经度（角度）
    ** lonOrigin 中央经度线（角度）
    ** FN 纬度起始点，北半球为0，南半球为10000000.0m
    ---------------------------------------------
    ** Output:(UTMNorthing, UTMEasting)
    ** UTMNorthing 经过UTM投影后的纬度方向的坐标
    ** UTMEasting 经过UTM投影后的经度方向的坐标
    ---------------------------------------------
    ** 功能描述：经纬度坐标投影为UTM坐标，采用美国地理测量部(USGS)提供的公式
    ** 作者： Ace Strong
    ** 单位： CCA NUAA
    ** 创建日期：2008年7月19日
    ** 版本：1.0
    ** 本程序实现的公式请参考
    ** "Coordinate Conversions and Transformations including Formulas" p35.
    ** & http://www.uwgb.edu/dutchs/UsefulData/UTMFormulas.htm
    '''

    # e表示WGS84第一偏心率,eSquare表示e的平方
    eSquare = 2*f_84 - f_84*f_84
    k0 = 0.9996

    # 确保longtitude位于-180.00----179.9之间
    lonTemp = (lon+180)-int((lon+180)/360)*360-180
    latRad = radians(lat)
    lonRad = radians(lonTemp)
    lonOriginRad = radians(lonOrigin)
    e2Square = eSquare/(1-eSquare)

    V = a_84/sqrt(1-eSquare*sin(latRad)**2)
    T = tan(latRad)**2
    C = e2Square*cos(latRad)**2
    A = cos(latRad)*(lonRad-lonOriginRad)
    M = a_84*((1-eSquare/4-3*eSquare**2/64-5*eSquare**3/256)*latRad
    -(3*eSquare/8+3*eSquare**2/32+45*eSquare**3/1024)*sin(2*latRad)
    +(15*eSquare**2/256+45*eSquare**3/1024)*sin(4*latRad)
    -(35*eSquare**3/3072)*sin(6*latRad))

    # x
    UTMEasting = k0*V*(A+(1-T+C)*A**3/6
    + (5-18*T+T**2+72*C-58*e2Square)*A**5/120)+ 500000.0
    # y
    UTMNorthing = k0*(M+V*tan(latRad)*(A**2/2+(5-T+9*C+4*C**2)*A**4/24
    +(61-58*T+T**2+600*C-330*e2Square)*A**6/720))
    # 南半球纬度起点为10000000.0m
    UTMNorthing += FN
    return UTMEasting, UTMNorthing


def LL2UTM_Army(lat_ll, lon_ll, FN=0):
    '''
    ** Input：(a, b, lat, lon, FN)
    ** a 椭球体长半轴
    ** b 椭球体短半轴
    ** lat_ll 经过UTM投影之前的纬度(角度为单位)
    ** lon_ll 经过UTM投影之前的经度(角度为单位)
    ** FN 纬度起始点，北半球为0，南半球为10000000.0m
    ---------------------------------------------
    ** Output:(UTMEasting, UTMNorthing)
    ** UTMNorthing 经过UTM投影后的纬度方向的坐标
    ** UTMEasting 经过UTM投影后的经度方向的坐标
    ---------------------------------------------
    ** 功能描述：经纬度坐标投影为UTM坐标，采用美国军方提供的公式
    ** 作者： Ace Strong
    ** 单位： CCA NUAA
    ** 创建日期：2009年1月14日
    ** 版本：1.0
    ** 本程序实现的公式请参考
    ** http://www.uwgb.edu/dutchs/UsefulData/UTMFormulas.htm
    '''

    lat = radians(lat_ll)
    lon0_ll = 6*(int(lon_ll/6)+31)-183
    k0 = 0.9996
    e = sqrt(1-b_84**2/a_84**2)
    e2 = e**2/(1-e**2)
    n = (a_84-b_84)/(a_84+b_84)
    nu = a_84/((1-(e*sin(lat))**2)**(1.0/2))
    p = (lon_ll-lon0_ll)*3600/10000
    sin1 = pi/(180*60*60)

    A = a_84*(1 - n + (5.0/4)*(n**2 - n**3) + (81.0/64)*(n**4 - n**5))
    B = (3*a_84*n/2)*(1 - n + (7.0/8)*(n**2 - n**3) + (55.0/64)*(n**4 - n**5))
    C = (15*a_84*n**2/16)*(1 - n + (3.0/4)*(n**2 - n**3))
    D = (35*a_84*n**3/48)*(1 - n + (11.0/16)*(n**2 - n**3))
    E = (315*a_84*n**4/51)*(1 - n)
    S = A*lat - B*sin(2*lat) + C*sin(4*lat) - D*sin(6*lat) + E*sin(8*lat)

    # y
    K1 = S*k0
    K2 = nu*sin(lat)*cos(lat)*sin1**2*k0*(100000000)/2
    K3 = (sin1**4*nu*sin(lat)*cos(lat)**3/24)*(5 - tan(lat)**2 + 9*e2*cos(lat)**2 + 4*e2**2*cos(lat)**4)*k0*(10000000000000000)
    UTMNorthing = K1 + K2*p**2 + K3*p**4
    # 南半球纬度起点为10000000.0m
    UTMNorthing += FN
    # x
    K4 = k0*sin1*nu*cos(lat)*10000
    K5 = (sin1*cos(lat))**3*(nu/6)*(1 - tan(lat)**2 + e2*cos(lat)**2)*k0*1000000000000
    UTMEasting = K4*p + K5*p**3 + 500000
    return UTMEasting, UTMNorthing



def UTM2LL_USGS(x, y, lon0=117.0):
    '''
    ** Input：(a, b, x, y, lon0)
    ** a 椭球体长半轴
    ** b 椭球体短半轴
    ** x 经过UTM投影后的经度方向的坐标，也就是UTMEasting
    ** y 经过UTM投影后的纬度方向的坐标，也就是UTMNorthing
    ** lon0 中央经度线
    ---------------------------------------------
    ** Output:(lat, lon)
    ** lat 维度（角度为单位）
    ** lon 经度（角度为单位）
    ---------------------------------------------
    ** 功能描述：UTM坐标转换为经纬度坐标
    ** 作者： Ace Strong
    ** 单位： CCA NUAA
    ** 创建日期：2009年1月16日
    ** 版本：1.0
    ** 本程序实现的公式请参考
    ** http://www.uwgb.edu/dutchs/UsefulData/UTMFormulas.htm
    '''

    x = 500000 - x
    k0 = 0.9996
    e = sqrt(1-b_84**2/a_84**2)
    # calculate the meridional arc
    M = y/k0
    # calculate footprint latitude
    mu = M/(a_84*(1 - e**2/4 - 3*e**4/64 - 5*e**6/256))
    e1 = (1 - (1 - e**2)**(1.0/2))/(1 + (1 - e**2)**(1.0/2))

    J1 = (3*e1/2 - 27*e1**3/32)
    J2 = (21*e1**2/16 - 55*e1**4/32)
    J3 = (151*e1**3/96)
    J4 = (1097*e1**4/512)
    fp = mu + J1*sin(2*mu) + J2*sin(4*mu) + J3*sin(6*mu) + J4*sin(8*mu)

    # Calculate Latitude and Longitude

    e2 = e**2/(1-e**2)
    C1 = e2*cos(fp)**2
    T1 = tan(fp)**2
    R1 = a_84*(1-e**2)/(1-(e*sin(fp))**2)**(3.0/2) # This is the same as rho in the forward conversion formulas above, but calculated for fp instead of lat.
    N1 = a_84/(1-(e*sin(fp))**2)**(1.0/2)   # This is the same as nu in the forward conversion formulas above, but calculated for fp instead of lat.
    D = x/(N1*k0)

    Q1 = N1*tan(fp)/R1
    Q2 = (D**2/2)
    Q3 = (5 + 3*T1 + 10*C1 - 4*C1**2 -9*e2)*D**4/24
    Q4 = (61 + 90*T1 + 298*C1 +45*T1**2  - 3*C1**2 -252*e2)*D**6/720
    lat = degrees(fp - Q1*(Q2 - Q3 + Q4))

    Q5 = D
    Q6 = (1 + 2*T1 + C1)*D**3/6
    Q7 = (5 - 2*C1 + 28*T1 - 3*C1**2 + 8*e2 + 24*T1**2)*D**5/120
    lon = lon0 - degrees((Q5 - Q6 + Q7)/cos(fp))
    return lat, lon


if __name__ == '__main__':
    lat = 31.936488
    lon = 118.78544
    UTMEasting, UTMNorthing = LL2UTM_USGS(lat, lon)
    print("UGCS: E:%f, N:%f"%(UTMEasting, UTMNorthing))
    lat_convert, lon_convert = UTM2LL_USGS(UTMEasting, UTMNorthing)
    print("After convert: E:%f, N:%f" % (lon_convert, lat_convert))
    UTMEasting, UTMNorthing = LL2UTM_Army(lat, lon)
    print("Army: E:%f, N:%f"%(UTMEasting, UTMNorthing))
    lat_convert, lon_convert = UTM2LL_USGS(UTMEasting, UTMNorthing)
    print("After convert: E:%f, N:%f" % (lon_convert, lat_convert))
