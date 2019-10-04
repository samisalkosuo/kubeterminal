#create KubeTerminal Linux executable

FROM ubuntu:16.04

RUN apt-get update
#RUN apt-get -y upgrade
RUN apt-get install -y build-essential libssl-dev libffi-dev python-dev
RUN apt-get install -y python3-pip

RUN pip3 install prompt_toolkit
RUN pip3 install pyinstaller
RUN pip3 install ascii_graph
RUN pip3 install pyperclip

WORKDIR /root

COPY kubeterminal.py .
COPY application/ ./application/
COPY kubectl/ ./kubectl/

RUN pyinstaller --onefile kubeterminal.py

CMD ["/bin/bash"]