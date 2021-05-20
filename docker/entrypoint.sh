#!/bin/bash
source /root/.profile
rm -f /tmp/.X1-lock

echo -n ${VNC_PASSWORD:-rausys} | vncpasswd -f > /root/.vnc/passwd
chmod 400 ~/.vnc/passwd
vncserver :1 -geometry 1280x960 -depth 24 && websockify -D --web=/usr/share/novnc/ 6901 localhost:5901
tail -n 0 -f /app/bot.log