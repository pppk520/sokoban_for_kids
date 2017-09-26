FROM python:3.5

RUN apt-get update

# Window Tools
RUN apt-get install -y python3-tk
# for exposing local xquartz socket on a TCP port
RUN apt-get install -y socat

# python environment
RUN pip install pip==9.0.1

# dependencies
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# install vim for later editing
RUN apt-get install -y vim

COPY .vimrc /root

CMD ["/bin/bash"]
