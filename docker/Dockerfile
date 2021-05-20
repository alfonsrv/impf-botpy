FROM debian:buster
# By Courtesy of https://github.com/Pfuenzle

ENV PYTHONUNBUFFERED 1

# install apt dependencies
RUN apt-get update -y
RUN DEBIAN_FRONTEND=noninteractive \
    apt-get install -y unzip wget chromium=90.0.4430.212-1~deb10u1 \
    xorg vnc4server autocutsel lxde-core novnc python-websockify \
    libffi-dev musl-dev libssl-dev python3-dev gcc \
    python3 python3-pip \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/90.0.4430.24/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/

WORKDIR /app

# Copy project files in directory
COPY . .

RUN pip3 install -r /app/requirements.txt

# Setup Environment
RUN echo "#!/bin/bash\nexport USER=root\nexport DOCKER_ENV=1\nexport DISPLAY=:1" >> /root/.profile

# Setup VNC
RUN echo "# XScreenSaver Preferences File\nmode:		off\nselected:  -1" > /root/.xscreensaver \
  && mkdir /root/.vnc/ \
  && mv /usr/share/novnc/vnc.html /usr/share/novnc/index.html

COPY ./docker/xstartup.sh /root/.vnc/xstartup
COPY ./docker/entrypoint.sh /root/entrypoint.sh

RUN chmod +x /root/.vnc/xstartup \
    && chmod +x /root/entrypoint.sh \
    && chmod go-rwx /root/.vnc

RUN cat /root/.xscreensaver \
    && cat /root/.vnc/xstartup \
    && cat /root/entrypoint.sh

EXPOSE 5901
EXPOSE 6901

CMD ["/root/entrypoint.sh"]
