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
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<meta http-equiv="Content-Language" content="ja" />
	<meta http-equiv="Content-Style-Type" content="text/css" />
	<meta http-equiv="Content-Script-Type" content="text/javascript" />
	<title>Powerline Frequency Monitoring</title>
	<!--[if IE]>
		<script type="text/javascript" src="html5jp/excanvas/excanvas.js"></script>
	<![endif]-->
	<script type="text/javascript">
		onload = function(){
			draw();
		};

		var canvas_width = 800;
		var canvas_height = 600;
		var graph_width = 720;
		var graph_height = 500;
		var x_org = 60;
		var y_org = 550;
		var x_max = 24*60;

		var y_min = _YMIN_;
		var y_max = _YMAX_;
		var y_step = _YSTEP_;

		var x_scale = graph_width/x_max;
		var y_scale = graph_height/(y_max - y_min);

		function graph_moveTo(ctx, x, y){
			ctx.moveTo(x+x_org, y_org - y);
		}

		function graph_lineTo(ctx, x, y){
			ctx.lineTo(x+x_org, y_org - y);
		}

		function rx2x(x){
			var rx = x*x_scale + x_org;
			if(rx < 0) return 0;
			if(rx > canvas_width) return canvas_width;
			return rx;
		}

		function ry2y(y){
			var ry =  y_org - (y - y_min)*y_scale;
			if(ry < 0) return 0;
			if(ry > canvas_height) return canvas_height;
			return ry;
		}

		function clickEventHandler(e) {
			var rect=e.target.getBoundingClientRect();
			rx = Math.floor(e.clientX - rect.left - x_org);
			ry = Math.floor(e.clientY - rect.top - y_org + graph_height);
			hour = Math.floor(rx*24/720);
			console.log(String(rx)+","+String(ry)+", hour="+String(hour));
			window.open("ac-graph2.cgi?camera=_CAMERA_&ymd=_TARGETDATE_&start="+ String(hour));
		//	document.info.txtb.value=String(mx2x(x))+","+String(my2y(y));
		}


		function draw(){	/* canvas ndde object */
			var canvas = document.getElementById('canvassample');

			if(!canvas || !canvas.getContext){
				return false;
			}
			/* 2D Context */
			var ctx = canvas.getContext('2d');
			canvas.addEventListener('click',clickEventHandler,false);

			ctx.beginPath();
			ctx.strokeStyle = 'rgb(0, 0, 0)';
			ctx.moveTo(0,0);
			ctx.lineTo(canvas_width,0);
			ctx.lineTo(canvas_width,canvas_height);
			ctx.lineTo(0,canvas_height);
			ctx.closePath();
			ctx.stroke();

			var grad  = ctx.createLinearGradient(0,0, 0,graph_height);
			/* set control point of gradation */
			grad.addColorStop(0,'rgb(192, 80, 77)');	// red
			grad.addColorStop(0.5,'rgb(155, 187, 89)'); // green
			grad.addColorStop(1,'rgb(128, 100, 162)');  // purple
			/* set gradation to fillStyle */
			ctx.fillStyle = grad;
			/* Draw Rect */
			ctx.fillRect(x_org,y_org-graph_height, graph_width, graph_height);

			/* Draw Graph Mesh */
			ctx.strokeStyle = 'rgb(64, 64, 64)';
			for(var y=y_min; y<=y_max; y += y_step){
				ctx.beginPath();
				ctx.moveTo(rx2x(0),ry2y(y));
				ctx.lineTo(rx2x(x_max),ry2y(y));
				ctx.stroke();
			};
			for(var x=0; x<=x_max; x += 60){
				ctx.beginPath();
				ctx.moveTo(rx2x(x),ry2y(y_min));
				ctx.lineTo(rx2x(x),ry2y(y_max));
				ctx.stroke();
			};
			ctx.strokeStyle = 'rgb(255,0,0)';
			ctx.beginPath();
			ctx.moveTo(rx2x(0),ry2y((y_min+y_max)*0.5));
			ctx.lineTo(rx2x(x_max),ry2y((y_min+y_max)*0.5));
			ctx.stroke();

			ctx.strokeStyle = 'rgb(0, 0, 0)';
			for(var y=y_min; y<=y_max; y += y_step){
			yy=Math.round(y*100)/100.0;
				ctx.strokeText(String(yy).substring(0,5),rx2x(0)-30, ry2y(y));
			};

			for(var x=0; x<=x_max; x += 60){
				ctx.strokeText(String(x/60),rx2x(x),ry2y(y_min)+12);
			};
_DRAWCODES_

            ctx.strokeStyle = 'rgb(0, 0, 0)';
            ctx.font = "18px ' Times New Roman'";
            ctx.strokeText("24 hour view", 400, 40);

		}
	</script>
</head>
<body>
	<h3> Powerline Frequency of _TARGETDATE_<br>
	_DEVICELIST_
	<br>

	<form id="info">
	<table>
	<tr>
	  <td>
		<a href="ac-dataview.cgi?camera=_CAMERA_&ymd=_TARGETDATE_">Data View</a></h3>
	  <td>
	  <td width=30></td>
	  <td>
		<a href="ac-graph.cgi?camera=_CAMERA_&ymd=_YESTERDAY_">Previous day
	  </td>
	  <td width=30></td>
	  <td>
		<a href="ac-graph.cgi?camera=_CAMERA_&ymd=_TOMORROW_">Next day
	  </td>
	  <td width=30></td>
	  <td>
		<a href="ac-graph.cgi?camera=_CAMERA_"> Today
	  </td>
	</tr>
	</table></form><p>
	<canvas id="canvassample" width="800" height="600"></canvas>
</body>
</html>
'''
drawcode=''
devicehtml=''
datalist=[]

def readData(srcpath):
	try:
		with open(srcpath) as fi:
			lc=0
			for line in fi:
				line_list=line.rstrip('\n').split(',')
				if len(line_list) >= 7 and line_list[6] != '':
					tm=line_list[1].split(':')
					tmm=int(tm[0])*60+int(tm[1])
					s0=float(line_list[5])
					s4=float(line_list[6])
					sx=float(line_list[4])
					datalist.append([tmm,s0,s4,sx])
	except IOError:
		pass		# ignore error

def draw_lineTo(time_min,val):
	return "ctx.lineTo(rx2x("+str(time_min)+"),ry2y("+str(val)+"));\n"

def draw_moveTo(time_min,val):
	return "ctx.moveTo(rx2x("+str(time_min)+"),ry2y("+str(val)+"));\n"

def compose_drawing(pos,color):
	global drawcode
	drawcode = drawcode + "ctx.strokeStyle='rgb(" + color + ")';\n"
	drawcode += "ctx.beginPath();\n"
	for i in range(len(datalist)):
		data=datalist[i]
		if i==0:
			drawcode += draw_moveTo(data[0],data[pos])
		else:
			drawcode += draw_lineTo(data[0],data[pos])
	drawcode += "ctx.stroke();\n"

def compose_devicehtml(devlist, camera):
	global devicehtml
	devicehtml='<table><tr><td>Devices:</td>\n'
	for dev in devlist:
		if camera == dev:
			devicehtml+='<td bgcolor="#aaaa00"><a href="ac-graph.cgi?camera='+dev+'">'
			devicehtml+='['+dev+']</a></td>\n'
		else:
			devicehtml+='<td><a href="ac-graph.cgi?camera='+dev+'">'
			devicehtml+=dev+'</a></td>\n'
	devicehtml+='</tr></table>'

def get_device_list():
	return [s for s in os.listdir('data/') if 'ac-' in s]

def print_html(camera,ymd):
	dt=datetime.strptime(ymd,'%Y-%m-%d')
	dt_yesterday=dt+timedelta(days=-1)
	dt_tomorrow=dt+timedelta(days=1)
	source = html.replace('_YMAX_','50.4')
	source=source.replace('_YMIN_','49.6')
	source=source.replace('_YSTEP_','0.04')
	source=source.replace('_CAMERA_',camera)
	source=source.replace('_DEVICE_',camera)
	source=source.replace('_TARGETDATE_',datetime.strftime(dt,'%Y-%m-%d'))
	source=source.replace('_YESTERDAY_',datetime.strftime(dt_yesterday,'%Y-%m-%d'))
	source=source.replace('_TOMORROW_',datetime.strftime(dt_tomorrow,'%Y-%m-%d'))
	source=source.replace('_DRAWCODES_',drawcode)
	source=source.replace('_DEVICELIST_',devicehtml)
	print('content-Type: text/html; charset=UTF-8')
	print()
	print(source)	# output html source

if __name__ == '__main__':
	form = cgi.FieldStorage()
#	argvs = sys.argv
#	argn = len(argvs)
	camera_default="ac-27eba3da"
	ymd_default=datetime.strftime(datetime.today(),'%Y-%m-%d')
	camera=form.getvalue('camera',camera_default)
	ymd=form.getvalue('ymd',ymd_default)
	readData('data/'+camera+'/'+ymd.replace('-','')+'.csv')
	compose_drawing(1,'255,255,0')
	compose_drawing(2,'255,0,255')
	compose_drawing(3,'255,255,255')
	compose_devicehtml(get_device_list(),camera)
	print_html(camera,ymd)
