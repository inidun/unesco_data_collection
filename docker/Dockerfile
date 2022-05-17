# OCRmyPDF with Tesseract 5 and tessdata_best
# Modified from
# https://github.com/ocrmypdf/OCRmyPDF/blob/master/.docker/Dockerfile
# https://hub.docker.com/r/jbarlow83/ocrmypdf/dockerfile

FROM ubuntu:20.04 as base

RUN apt-get update && apt-get install -y \
    software-properties-common && \
    add-apt-repository ppa:alex-p/tesseract-ocr5

# FROM base as builder

ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential autoconf automake libtool \
    libleptonica-dev \
    zlib1g-dev \
    python3-dev \
    python3-distutils \
    libffi-dev \
    libqpdf-dev \
    ca-certificates \
    curl \
    git

# Get the latest pip (Ubuntu version doesn't support manylinux2010)
RUN \
    curl https://bootstrap.pypa.io/get-pip.py | python3

# Compile and install jbig2
# Needs libleptonica-dev, zlib1g-dev
RUN \
    mkdir jbig2 \
    && curl -L https://github.com/agl/jbig2enc/archive/ea6a40a.tar.gz | \
    tar xz -C jbig2 --strip-components=1 \
    && cd jbig2 \
    && ./autogen.sh && ./configure && make && make install \
    && cd .. \
    && rm -rf jbig2

WORKDIR /
RUN git clone https://github.com/ocrmypdf/OCRmyPDF.git
RUN /bin/mv OCRmyPDF app

WORKDIR /app

RUN pip3 install --no-cache-dir .[test,webservice,watcher]

# FROM base

ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    ghostscript \
    img2pdf \
    liblept5 \
    libsm6 libxext6 libxrender-dev \
    zlib1g \
    pngquant \
    python3 \
    qpdf \
    tesseract-ocr \
    tesseract-ocr-eng \
    unpaper \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# COPY --from=builder /usr/local/lib/ /usr/local/lib/
# COPY --from=builder /usr/local/bin/ /usr/local/bin/

# COPY --from=builder /app/misc/webservice.py /app/
# COPY --from=builder /app/misc/watcher.py /app/

# # Copy minimal project files to get the test suite.
# COPY --from=builder /app/setup.cfg /app/setup.py /app/README.md /app/
# COPY --from=builder /app/tests /app/tests
# COPY --from=builder /app/src /app/src

# Add language packs (training data) from tessdata_best
# ADD https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/main/eng.traineddata /usr/share/tesseract-ocr/5/tessdata/
# ADD https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/main/osd.traineddata /usr/share/tesseract-ocr/5/tessdata/


RUN wget -qO /usr/share/tesseract-ocr/5/tessdata/eng.traineddata https://github.com/tesseract-ocr/tessdata_best/blob/main/eng.traineddata?raw=true
RUN wget -qO /usr/share/tesseract-ocr/5/tessdata/osd.traineddata https://github.com/tesseract-ocr/tessdata_best/blob/main/osd.traineddata?raw=true

ENTRYPOINT ["/usr/local/bin/ocrmypdf"]
