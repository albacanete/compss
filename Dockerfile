ARG DEBIAN_FRONTEND=noninteractive

ARG BASE=base20
ARG VERSION=3.0

FROM registry.gitlab.bsc.es/ppc/software/compss/conn-ubuntu-base:3.0-amd

ENV GRADLE_HOME /opt/gradle
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
ENV PATH $PATH:/opt/gradle/bin
ENV EXTRAE_MPI_HEADERS /usr/include/x86_64-linux-gnu/mpi

COPY . /framework

ENV GRADLE_HOME /opt/gradle
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
ENV PATH $PATH:/opt/COMPSs/Runtime/scripts/user:/opt/COMPSs/Bindings/c/bin:/opt/COMPSs/Runtime/scripts/utils:/opt/gradle/bin
ENV CLASSPATH $CLASSPATH:/opt/COMPSs/Runtime/compss-engine.jar
ENV LD_LIBRARY_PATH /opt/COMPSs/Bindings/bindings-common/lib:$JAVA_HOME/jre/lib/amd64/server
ENV COMPSS_HOME=/opt/COMPSs/

# Install COMPSs
RUN cd /framework && \
    # ./submodules_get.sh && \
    export EXTRAE_MPI_HEADERS=/usr/include/x86_64-linux-gnu/mpi && \
    /framework/builders/buildlocal /opt/COMPSs && \
    mv /root/.m2 /home/jenkins && \
    chown -R jenkins: /framework && \
    chown -R jenkins: /home/jenkins/ 

# Expose SSH port and run SSHD
EXPOSE 22
CMD ["/usr/sbin/sshd","-D"]