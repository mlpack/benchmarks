FROM frolvlad/alpine-python3

RUN apk add --update make \
    cmake \
    swig \
    bash \
    python3-dev \
    build-base \
    openblas-dev

RUN pip install --upgrade pip 

RUN pip install --upgrade PyYAML \
    numpy \
    timeout_decorator \
    scipy \
    sklearn \
    simplejson

WORKDIR /usr/src/benchmarks
COPY . .

RUN make setup

RUN rm -rf ./libraries/*.tar.gz \
    rm -rf ./libraries/*.zip \
    rm -rf ./libraries/*.jar
    
# TODO rm  libraries *.tar.gz
ENTRYPOINT ["/usr/bin/make", "run"]