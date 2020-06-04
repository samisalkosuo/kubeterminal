#create KubeTerminal Linux executable

FROM kazhar/python:latest as build


WORKDIR /root

COPY requirements.txt .
RUN python3.8 -m pip install -r requirements.txt

COPY kubeterminal.py .
COPY application/ ./application/
COPY kubectl/ ./kubectl/

COPY hook.py .

RUN pyinstaller --onefile --additional-hooks-dir=. kubeterminal.py

FROM busybox:1.31.1

COPY --from=build /root/dist/kubeterminal .

