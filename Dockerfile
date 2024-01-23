FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

# RUN rm /bin/sh && ln -s /bin/bash /bin/sh
# SHELL ["/bin/bash", "-c"]

# setup timezone
ENV TZ=Europe/Helsinki
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTONUNBUFFERED 1

# download openfoam and update repos
RUN apt-get update
RUN apt-get -y install software-properties-common 
RUN apt-get -y install ca-certificates
RUN apt-get -y install wget
RUN apt-get install -y python3-pip

RUN sh -c "wget -O - https://dl.openfoam.org/gpg.key | apt-key add -"
RUN apt-get update
RUN add-apt-repository http://dl.openfoam.org/ubuntu
RUN apt-get update
RUN apt-get -y install openfoam7

RUN apt-get install -y libgl1-mesa-glx xvfb

# add user "foam"
RUN useradd --user-group --create-home --shell /bin/bash foam ; echo "foam ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER foam

WORKDIR /home/foam/app
COPY --chown=foam:foam . /home/foam/app

ENV PYVISTA_OFF_SCREEN=true
RUN pip3 install -r requirements.txt

WORKDIR /home/foam/app/OFoamDjango

CMD ["./run_server.sh"]

EXPOSE 8000
