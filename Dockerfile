FROM ubuntu

USER root
RUN apt update && apt upgrade -y && apt install -y curl debian-keyring debian-archive-keyring apt-transport-https

RUN curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
RUN curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list

RUN apt update && apt install -y caddy supervisor python3 python3-pip
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN chown -R caddy:caddy /etc/caddy
RUN apt install -y libnss3-tools
RUN id -u user >/dev/null 2>&1 || useradd -ms /bin/bash user
RUN echo "user:user" | chpasswd
RUN usermod -aG user caddy

USER user
WORKDIR /home/user

COPY --chown=user:user backend/requirements.txt backend/requirements.txt
RUN pip3 install -r backend/requirements.txt

COPY --chown=user:user backend backend

USER root
COPY Caddyfile /etc/caddy/Caddyfile

ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]