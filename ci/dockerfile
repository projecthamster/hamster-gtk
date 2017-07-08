FROM debian:stretch-slim

LABEL maintainer="Eric Goller"

RUN apt-get update -qq
RUN apt-get install --no-install-recommends -y\
 git\
 python-setuptools\
 python-pip\
 python-dev\
 python3-dev\
 build-essential\
 python-wheel\
 xvfb\
 xauth\
 curl\
 locales\
 gir1.2-pango-1.0\
 gir1.2-gtk-3.0\
 libglib2.0-dev\
 libgtk-3-dev\
 python-gi\
 python3-gi\
 python-cairo\
 python-gi-cairo

RUN locale-gen C.UTF-8 && /usr/sbin/update-locale LANG=C.UTF-8
ENV LANG=C.UTF-8 LANGUAGE=C.UTF-8 LC_ALL=C.UTF-8

RUN mkdir hamster-gtk
WORKDIR hamster-gtk
