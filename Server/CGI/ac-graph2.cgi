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
	<title>HEPCO Frequency Monitor</title>
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
		var graph_left = 60;
		var graph_top = 50;

		var hour_range = _HOURRANGE_;
		var y_step = _YSTEP_;
		var y_min = _YMIN_;
		var y_max = _YMAX_;
		var y_height = y_max - y_min;

		var start = _START_;
		var x_min = _START_;
		var x_max = x_min + hour_range*3600;
		var x_width = hour_range*3600;
		var x_scale = graph_width/x_width;
		var y_scale = graph_height/y_height;

		var database=_DATABASE_;

/*	Translate graph coordinate to canvas coordinate	*/
		function gx2x(gx){
			if(gx < 0) return graph_left;
			if(gx > graph_width) return graph_width+graph_left;
			return gx+graph_left;
		}

		function gy2y(gy){
			if(gy < 0) return graph_height + graph_top;
			if(gy > graph_height) return graph_top;
			return graph_height + graph_top - gy;
		}

/*	Translate value coordinate to canvas coordinate	*/
		function rx2x(rx){
			return gx2x((rx-x_min)*x_scale);
		}

		function ry2y(ry){
			return gy2y((ry-y_min)*y_scale);
		}

/*	Translate to graph coordinates	*/
		function mx2gx(x){
			return Math.floor(x-graph_left);
		}

		function my2gy(y){
			return Math.floor(y-graph_height-graph_top);
		}

		function clickEventHandler(e){
			var rect=e.target.getBoundingClientRect();
			gx = mx2gx(e.clientX - rect.left);
			gy = my2gy(e.clientY - rect.top);
			if(gx < graph_width/2)
				start=start-3600;
			else 
				start=start+3600;
			if(start < 0)
				start=0;
			x_min = start;
			x_max = start + hour_range*3600;
			draw();	// redraw
		}

		function onClickButton(arg){
			start=start + arg*3600;
			if(start< 0)
				start=0;
			x_min = start;
			x_max = start + hour_range*3600;
			draw();	// redraw
		}

/*	Drawing codes	*/
		function init_canvas(ctx){
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
   		 	ctx.fillRect(graph_left,graph_top,graph_width,graph_height);
			};

		function draw_grids(ctx){
   		 	/* Draw Graph Grid */
   		 	ctx.strokeStyle = 'rgb(64, 64, 64)';
   	 		for(var y=y_min; y<=y_max; y += y_step){
				ctx.beginPath();
				ctx.moveTo(rx2x(x_min),ry2y(y));
				ctx.lineTo(rx2x(x_min+x_width),ry2y(y));
				ctx.stroke();
			};
			for(var x=0; x<=x_width; x += 5*60){
				ctx.beginPath();
				ctx.moveTo(rx2x(x_min+x),ry2y(y_min));
				ctx.lineTo(rx2x(x_min+x),ry2y(y_max));
				ctx.stroke();
			};
            ctx.strokeStyle = 'rgb(255,0,0)';
            ctx.beginPath();
            ctx.moveTo(rx2x(0),ry2y((y_min+y_max)*0.5));
            ctx.lineTo(rx2x(x_max),ry2y((y_min+y_max)*0.5));
            ctx.stroke();
		}

		function draw_comments(ctx){
			ctx.strokeStyle = 'rgb(0, 0, 0)';
			for(var y=y_min; y<=y_max; y += y_step){
				yy=Math.round(y*100)/100.0;
				ctx.strokeText(String(yy).substring(0,5),rx2x(0)-30, ry2y(y));
			};
			if(hour_range==2){
				hour_start=start/3600;
				ctx.strokeText(String(hour_start)+":00",
								graph_left,ry2y(y_min)+24);
				ctx.strokeText(String(hour_start+1)+":00",
								graph_left+graph_width/2,ry2y(y_min)+24);
				for(var x=0; x<=120; x += 5){
					ix = x % 60;
					rx=start+x*60;
					ctx.strokeText(String(ix),graph_left+x*6,ry2y(y_min)+12);
				}
			}
			else {
				for(var x=0; x<=x_width; x += x_width/24){
					ctx.strokeText(String(x/60),rx2x(x),ry2y(y_min)+12);
				}
			};
			ctx.strokeStyle = 'rgb(0, 0, 0)';
			ctx.strokeText("2 hour view", 400, 40);
		}

		function draw_graph(ctx,ch,color){
			if(database.length<=1)
				return;
			ctx.strokeStyle=color;
			ctx.beginPath();
			var check_start=0;
			for(i=0;i<database.length;i++){
				if(database[i][0]>=start && database[i][0] <= start+2*60*60){
					if(check_start == 0){
						ctx.moveTo(rx2x(database[i][0]),ry2y(database[i][ch]));
						check_start=1;
					}
					else {
						ctx.lineTo(rx2x(database[i][0]),ry2y(database[i][ch]));
					}
				}
			}
			ctx.stroke();
		}
			
   		function draw(){	/* canvas ndde object */
			var canvas = document.getElementById('canvassample');

			if(!canvas || !canvas.getContext){
				return false;
			}
			/* 2D Context */
			var ctx = canvas.getContext('2d');
			canvas.addEventListener('click',clickEventHandler,false);
			ctx.clearRect(0, 0, canvas.width, canvas.height);
			init_canvas(ctx);
			draw_grids(ctx);
			draw_comments(ctx);
			draw_graph(ctx,1,'rgb(255,255,0)');
			draw_graph(ctx,2,'rgb(255,0,255)');
			draw_graph(ctx,3,'rgb(255,255,255)');
		}
	</script>
</head>
<body>
	<h3> Powerline Frequency of _TARGETDATE_<BR>
	Device: _DEVICE_ </h3>
	<form name="info">
	<table>
	<tr>
	  <td>
		<a href="hepco-sensor.cgi?camera=_CAMERA_&ymd=_TARGETDATE_">Data View</a></h3>
	  <td>
	  <td width=30></td>
	  <td>
		<input type="button"  onClick="onClickButton(-1)" value="1 hour before">
	  </td>
	  <td width=30></td>
	  <td>
		<input type="button"  onClick="onClickButton(+1)" value="1 hour after">
	  </td> 
	  <td><td width=30></td>
	 <td><a href="ac-graph.cgi?camera=_CAMERA_&ymd=_TARGETDATE_">Back to 24 hour view </td>
	</tr>
	</table></form><p>
	<canvas id="canvassample" width="800" height="600"></canvas>
</body>
</html>
'''
dbcode=''

datalist=[]

def timestr2sec(timestr):
	tm=timestr.split(':')
	if tm[0] == '':
		return 0
	elif tm[1] == '':
		return int(tm[0])*3600
	elif tm[2] == '':
		return int(tm[0])*3600+int(tm[1])*60
	return int(tm[0])*3600+int(tm[1])*60+int(tm[2])
				
def hourinsec(timestr):
	tm=timestr.split(':')
	if tm[0] == '':
		return 0
	return int(tm[0])*3600

def readData(srcpath):
	try:
		with open(srcpath) as fi:
			lc=0
			for line in fi:
				line_list=line.rstrip('\n').split(',')
				if len(line_list) >= 7 and line_list[6] != '':
					tms=timestr2sec(line_list[1])
					s0=float(line_list[5])
					s4=float(line_list[6])
					sx=float(line_list[4])
					datalist.append([tms,s0,s4,sx])
	except IOError:
		pass		# ignore error

def compose_dbcode():
	global dbcode
	dbcode += "["
	for i in range(len(datalist)):
		if i == 0:
			dbcode+= str(datalist[i])+"\n"
		else:
			dbcode+= ','+str(datalist[i])+"\n"
	dbcode += "];\n"


def print_html(camera,ymd,start_in_sec):
	start_in_hour=int(start_in_sec/3600)
	dt=datetime.strptime(ymd,'%Y-%m-%d')
	dt_yesterday=dt+timedelta(days=-1)
	dt_tomorrow=dt+timedelta(days=1)
	source = html.replace('_YMAX_','50.4')
	source=source.replace('_YMIN_','49.6')
	source=source.replace('_YSTEP_','0.04')
	source=source.replace('_HOURRANGE_','2')
	source=source.replace('_START_',str(start_in_sec))
	source=source.replace('_CAMERA_',camera)
	source=source.replace('_DEVICE_',camera)
	source=source.replace('_TARGETDATE_',datetime.strftime(dt,'%Y-%m-%d'))
	source=source.replace('_BEFORE_',str(start_in_hour-1))
	source=source.replace('_AFTER_',str(start_in_hour+1))
	source=source.replace('_DATABASE_',dbcode)
	print('content-Type: text/html; charset=UTF-8')
	print()
	print(source)	# output html source

if __name__ == '__main__':
	form = cgi.FieldStorage()
#	argvs = sys.argv
#	argn = len(argvs)
	camera_default="ac-27eba3da"
	ymd_default=datetime.strftime(datetime.today(),'%Y-%m-%d')
	now_hour=int(datetime.now().strftime("%H"))
	default_start_hour=now_hour-1;
	if default_start_hour < 0:
		default_start_hour = 0
	camera=form.getvalue('camera',camera_default)
	ymd=form.getvalue('ymd',ymd_default)
	start_in_hour=int(form.getvalue('start',str(default_start_hour)))
	start_in_sec=start_in_hour*3600
	readData('data/'+camera+'/'+ymd.replace('-','')+'.csv')
	compose_dbcode()
	print_html(camera,ymd,start_in_sec)
 
