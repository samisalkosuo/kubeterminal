#create KubeTerminal Linux executable

FROM kazhar/python:latest as build


WORKDIR /root

COPY requirements.txt .
RUN python3.8 -m pip install -r requirements.txt

COPY kubeterminal.py .
COPY kubeterminal/ ./kubeterminal/

RUN pyinstaller --onefile kubeterminal.py

FROM busybox:1.31.1

COPY --from=build /root/dist/kubeterminal .

