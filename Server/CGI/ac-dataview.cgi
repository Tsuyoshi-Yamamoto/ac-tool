#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import cgi,cgitb
from datetime import datetime,timedelta

cgitb.enable()

html='''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
<head><TITLE>Niseko Land Yacht Club</title></head>
<body>
<h3> HEPCO Powerline Frequency Data for _TARGETDATE_</h3>
<table>
<tr>
  <td>
    <a href="ac-graph.cgi?camera=_CAMERA_&ymd=_TARGETDATE_" > Graph View </a>
  </td>
  <td width=30> </td>
  <td>
    <a href="ac-dataview.cgi?camera=_CAMERA_&ymd=_YESTERDAY_" > Previous day </a>
  </td>
  <td width=30> </td>
  <td>
    <a href="ac-dataview.cgi?camera=_CAMERA_&ymd=_TOMORROW_" > Next day </a>
  </td>
</tr>
<table border=1>
<tr><td align=center>Time</td>
<td align=center>Lowest Freq</td>
<td align=center>Highest Freq</td>
<td align=center>Average Freq</td></tr>
_TABLECODE_
</table>
</body></html>
'''
datalist=[]
tablecode=''

def readData(srcpath):
    try:
        with open(srcpath) as fi:
            for entry in fi:
                line=entry.rstrip('\n').split(',')
                if len(line) >= 7:
                    datalist.append([line[1],line[4],line[5],line[6]])
    except IOError:
        pass        # ignore error

def compose_table_code(srcpath):
    global tablecode
    datalist.reverse()
    for line in datalist:
        tablecode+='<tr><td>'+line[0]+'</td>'
        tablecode+='<td align="right">'+line[2]+' Hz</td>'
        tablecode+='<td align="right">'+line[3]+' Hz</td>'
        tablecode+='<td align="right">'+line[1]+' Hz</td></tr>\n'

def print_html(camera,ymd):
    dt=datetime.strptime(ymd,'%Y-%m-%d')
    dt_yesterday=dt+timedelta(days=-1)
    dt_tomorrow=dt+timedelta(days=1)
    source=html.replace('_CAMERA_',camera)
    source=source.replace('_TARGETDATE_',datetime.strftime(dt,'%Y-%m-%d'))
    source=source.replace('_YESTERDAY_',datetime.strftime(dt_yesterday,'%Y-%m-%d'))
    source=source.replace('_TOMORROW_',datetime.strftime(dt_tomorrow,'%Y-%m-%d'))
    source=source.replace('_TABLECODE_',tablecode)
    print('content-Type: text/html; charset=UTF-8')
    print()
    print(source)    # output html sentence

if __name__ == '__main__':
    form = cgi.FieldStorage()
#    argvs = sys.argv
#    argn = len(argvs)
    camera_default="nlyc"
    ymd_default=datetime.strftime(datetime.today(),'%Y-%m-%d')
    camera=form.getvalue('camera',camera_default)
    ymd=form.getvalue('ymd',ymd_default)
    readData('data/'+camera+'/'+ymd.replace('-','')+'.csv')
    compose_table_code('data/'+camera+'/'+ymd.replace('-','')+'.csv')
    print_html(camera,ymd)
 
