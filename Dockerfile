FROM ubuntu
WORKDIR /app
RUN ["apt", "update"]
RUN ["apt", "install" ,"python3.8", "-y"]
RUN ["apt-get", "install" ,"python3-pip", "-y"]
COPY requirements.txt requirements.txt
COPY . .
RUN ["pip3", "install", "-r" ,"/app/requirements.txt"]
RUN ["apt-get", "install", "cron", "-y"]
COPY crontab /etc/cron.d/cjob
RUN ["chmod", "0644", "/etc/cron.d/cjob"]
RUN ["crontab", "/etc/cron.d/cjob"]
ENTRYPOINT ["cron", "-f"]