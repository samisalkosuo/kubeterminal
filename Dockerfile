#create KubeTerminal Linux executable

FROM kazhar/devcon:python-3.10.4 as build


WORKDIR /root

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

COPY kubeterminal.py .
COPY kubeterminal/ ./kubeterminal/

RUN pyinstaller --onefile kubeterminal.py

FROM busybox:1.31.1

COPY --from=build /root/dist/kubeterminal .

