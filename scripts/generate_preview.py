#!/usr/bin/env python3
"""Create an illustrative image for the README from the same generated demo values.

This is an illustration of the interface, not a browser screenshot. Browser
screenshots should be captured from a running instance if needed.
"""
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from gridlens.data import demo_data,overview

OUT=Path(__file__).resolve().parents[1]/'docs/dashboard-preview.png'
W,H=1480,970
im=Image.new('RGB',(W,H),'#09111c')
d=ImageDraw.Draw(im)
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
boldpath='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def f(size,bold=False):return ImageFont.truetype(boldpath if bold else fontpath,size)
def label(x,y,text,size=14,color='#ebf5f5',bold=False):d.text((x,y),text,font=f(size,bold),fill=color)
def rect(box,fill,radius=14,outline=None):d.rounded_rectangle(box,radius=radius,fill=fill,outline=outline,width=1 if outline else 0)
def line(points,fill='#63e6c5',width=3):d.line(points,fill=fill,width=width,joint='curve')
# Frame / sidebar
rect((0,0,238,H),'#0d1724',0)
d.line((238,0,238,H),fill='#283848',width=1)
rect((27,32,66,72),'#173b3a',9)
line([(34,57),(43,57),(48,43),(56,62),(63,49)],width=3)
label(82,29,'grid',29,bold=True);label(141,29,'lens',29,color='#63e6c5',bold=True)
label(82,62,'ENERGY ANALYTICS LAB',8,'#849bb0',True)
label(27,132,'WORKSPACE',10,'#637e93',True)
rect((19,163,221,203),'#16362f',8)
for y,text,active in [(176,'Overview',True),(230,'Consumption patterns',False),(284,'Forecast studio',False),(338,'Behind the model',False)]:
 label(37,y,'◈' if active else '◦',16,'#69e5c5' if active else '#758da1');label(67,y+2,text,12,'#b5efdb' if active else '#92a6b7')
d.line((27,400,211,400),fill='#263649',width=1)
label(27,423,'DATA SOURCE',10,'#688398',True)
rect((20,455,219,500),'#162638',9,outline='#37505e')
label(32,467,'Generated demo facility',11,'#c7d7e1')
label(33,519,'•  2,880 hourly observations',10,'#86bbad')
rect((20,557,219,660),'#122532',11,outline='#456273')
label(111,570,'↑',25,'#6ae5c7');label(40,605,'Upload your own CSV',13,'#eef6fa',True);label(54,630,'Hourly readings',10,'#7a91a5')
rect((20,818,219,908),'#152c2e',12,outline='#28524a')
label(35,833,'OPEN TO INSPECT',10,'#a0e8d9',True)
label(35,858,'Transparent model.',11,'#bdcdd2');label(35,877,'Readable Python tests.',11,'#8babb3')
# top bar
label(275,27,'Portfolio project  /  Energy analytics',12,'#889caf')
label(1260,27,'●   Local demo',11,'#78d7c2')
d.line((239,65,W,65),fill='#203343',width=1)
label(283,105,'ENERGY INTELLIGENCE / 01',11,'#75dac2',True)
label(280,142,'Understand the load.',44,'#f2f7f7',True)
label(280,201,'See what comes next.',44,'#65e7c8',True)
label(283,278,'Explore electricity consumption, spot meaningful patterns,',13,'#90a8b9')
label(283,300,'and test a transparent 24-hour forecasting model.',13,'#90a8b9')
rect((282,348,485,387),'#67e2c5',9)
label(296,359,'Explore the forecast  ↗',12,'#0b2b22',True)
rect((501,348,675,387),'#142638',9,outline='#345468')
label(518,359,'Export to Power BI  ↘',12,'#e1eeed',True)
# hero decorative signal
path=[(x,y) for x,y in [(913,305),(946,292),(974,325),(1001,267),(1025,314),(1050,242),(1080,280),(1113,222),(1140,290),(1170,183),(1200,239),(1230,140),(1260,244),(1292,200),(1322,224),(1361,184),(1409,205)]]
for wi,shade in [(13,'#173d3e'),(3,'#69e5c7')]: line(path,shade,wi)
rect((278,429,1395,430),'#243748',0)
label(282,457,'AT A GLANCE',10,'#7de1c9',True)
label(282,478,'Energy overview',24,'#f2f6f7',True)
label(1196,484,'SEP — DEC 2025',10,'#8399a8')
info=overview(demo_data(),'Generated demo facility')
items=[('Total consumption',f"{info['total_mwh']:,.2f}",'MWh'),('Average hourly load',f"{info['mean_kw']:,.1f}",'kW'),('Highest hourly load',f"{info['peak_kw']:,.1f}",'kW')]
for i,(name,val,unit) in enumerate(items):
 x=280+i*376
 rect((x,535,x+355,690),'#121f2e',12,outline='#2b4252')
 label(x+19,552,name,13,'#b6c6d1')
 label(x+18,590,val,32,'#f2f7f8',True)
 label(x+220,602,unit,13,'#8fa8b2')
 label(x+19,653,'Based on generated demo observations',10,'#839cab')
# trend chart panel
rect((280,712,1397,950),'#101d2b',14,outline='#2b4252')
label(304,727,'DEMAND TRACKER',10,'#68ddc3',True)
label(304,747,'Consumption over time',19,'#f1f6f8',True)
label(304,775,'Daily energy use, summed from hourly readings',11,'#7d96a8')
daily=info['daily'][-90:]
vals=np.array([v['kwh'] for v in daily],dtype=float)
left,right,top,bottom=310,1360,818,914
for i in range(4):
 yy=bottom-(bottom-top)*i/3
 d.line((left,yy,right,yy),fill='#263947',width=1)
minv,maxv=float(vals.min()),float(vals.max());rg=maxv-minv
pts=[(left+(right-left)*i/(len(vals)-1),bottom-((float(v)-minv)/rg*.72+.11)*(bottom-top)) for i,v in enumerate(vals)]
line(pts,'#66e5c7',3)
label(308,923,'01 Oct',10,'#8197a6');label(1324,923,'29 Dec',10,'#8197a6')
OUT.parent.mkdir(exist_ok=True)
im.save(OUT,optimize=True)
print('Wrote',OUT)
