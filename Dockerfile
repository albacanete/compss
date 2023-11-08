ARG ROOT_CONTAINER=registry.gitlab.bsc.es/ppc/software/compss/conn-ubuntu-base:3.0-amd
FROM $ROOT_CONTAINER
MAINTAINER COMPSs Support <support-compss@bsc.es>

ARG ARCH=amd64
ARG FULL_ARCH=x86_64
ARG release=false

# Copy framework files for installation and testing
COPY . /framework

ENV GRADLE_HOME /opt/gradle
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-${ARCH}/

ENV EXTRAE_MPI_HEADERS /usr/include/${FULL_ARCH}-linux-gnu/mpi
ENV PATH $PATH:/opt/COMPSs/Runtime/scripts/user:/opt/COMPSs/Bindings/c/bin:/opt/COMPSs/Runtime/scripts/utils:/opt/gradle/bin
ENV CLASSPATH $CLASSPATH:/opt/COMPSs/Runtime/compss-engine.jar
ENV LD_LIBRARY_PATH /opt/COMPSs/Bindings/bindings-common/lib:$JAVA_HOME/jre/lib/${ARCH}/server
ENV COMPSS_HOME=/opt/COMPSs/

# Install Kubernetes connector
COPY utils/kubernetes/kubernetes-conn.jar /tmp/kubernetes-conn.jar
RUN mvn install:install-file -DgroupId=es.bsc.conn -DartifactId=kubernetes-conn -Dversion=1.8-11 -Dpackaging=jar -Dfile=/tmp/kubernetes-conn.jar

# Install COMPSs
# Install Kubernetes connector
COPY utils/kubernetes/k8s-conn.jar /tmp/k8s-conn.jar
RUN mvn install:install-file -DgroupId=es.bsc.conn -DartifactId=k8s-conn -Dversion=1.8-9 -Dpackaging=jar -Dfile=/tmp/k8s-conn.jar

RUN cd /framework && \
    apt update -y && apt install git -y && \
    export EXTRAE_MPI_HEADERS=/usr/include/${FULL_ARCH}-linux-gnu/mpi && \
    /framework/builders/buildlocal /opt/COMPSs && \
    mv /root/.m2 /home/jenkins && \
    chown -R jenkins: /framework && \
    chown -R jenkins: /home/jenkins/ 

RUN mv /tmp/k8s-conn.jar /opt/COMPSs/Runtime/cloud-conn/k8s-conn.jar 

# Expose SSH port and run SSHD
EXPOSE 22
CMD ["/usr/sbin/sshd","-D"]