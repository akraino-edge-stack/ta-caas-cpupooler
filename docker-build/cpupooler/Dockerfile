# Copyright 2019 Nokia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM alpine:3.9
MAINTAINER Balazs Szekeres <balazs.szekeres@nokia.com>

ARG DEP_MAN_VERSION
ARG CPUPOOLER_VERSION
ARG go_install_dir="/usr/local/go"
ARG go_version
ENV GOPATH /build
ENV PATH $go_install_dir/bin:$PATH
ENV BUILD_DIR="$GOPATH/src/github.com/nokia/CPU-Pooler"

RUN apk update \
&&  apk upgrade \
&&  apk add --no-cache --virtual .build-deps build-base git mercurial go glide bash tar \
&&  apk add --no-cache curl \
&&  mkdir -p $go_install_dir \
&&  curl -fsSL -k https://dl.google.com/go/go${go_version}.src.tar.gz | tar zx --strip-components=1 -C ${go_install_dir} \
&&  cd ${go_install_dir}/src/ \
&&  ./make.bash \
&&  curl -fsSL -o /usr/local/bin/dep https://github.com/golang/dep/releases/download/v${DEP_MAN_VERSION}/dep-linux-amd64 \
&&  chmod +x /usr/local/bin/dep \
&&  mkdir -p $BUILD_DIR \
&&  git clone https://github.com/nokia/CPU-Pooler.git $BUILD_DIR \
&&  cd $BUILD_DIR \
&&  git fetch --tags \
&&  git checkout ${CPUPOOLER_VERSION} \
&&  dep ensure --vendor-only \
# cpu-device-plugin
&&  CGO_ENABLED=0 GOOS=linux go build -a -ldflags '-extldflags "-static"' -o cpu-device-plugin ./cmd/cpu-device-plugin \
&&  mv $BUILD_DIR/cpu-device-plugin /cpu-device-plugin \
# cpu-setter
&&  CGO_ENABLED=0 GOOS=linux go build -a -ldflags '-extldflags "-static"' -o cpu-setter ./cmd/cpusetter \
&&  mv $BUILD_DIR/cpu-setter /cpu-setter \
# cpu-webhook
&&  CGO_ENABLED=0 GOOS=linux go build -a -ldflags '-extldflags "-static"' -o cpu-device-webhook ./cmd/webhook \
&&  mv $BUILD_DIR/cpu-device-webhook /cpu-device-webhook \
&&  apk del .build-deps \
&&  rm -rf $GOPATH \
&&  rm -rf $go_install_dir \
&&  rm -rf /build \
&&  rm -rf /root/.glide
