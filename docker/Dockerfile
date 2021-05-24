FROM debian:buster
# By Courtesy of https://github.com/Pfuenzle

ENV PYTHONUNBUFFERED 1

# install apt dependencies
RUN apt-get update -y
RUN DEBIAN_FRONTEND=noninteractive \
    apt-get install -y unzip wget \
    xorg vnc4server autocutsel lxde-core novnc python-websockify \
    libffi-dev musl-dev libssl-dev python3-dev gcc \
    python3 python3-pip \
    chromium-driver=90.0.4430.212-1~deb10u1 \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
  && apt-get update -qqy \
  && apt-get -qqy install \
    ${CHROME_VERSION:-google-chrome-stable} \
  && rm /etc/apt/sources.list.d/google-chrome.list \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*


WORKDIR /app

# Copy project files in directory
COPY requirements.txt main.py ./
COPY impf/ ./impf/

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
