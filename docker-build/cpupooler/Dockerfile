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

ARG DEPENDENCY_MANAGER
ENV DEP_VERSION=$DEPENDENCY_MANAGER
ARG CPUPOOLER
ENV CPUPOOLER_VERSION=$CPUPOOLER
ENV GOPATH /build
ENV PATH /usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV BUILD_DIR="$GOPATH/src/github.com/nokia/CPU-Pooler"

RUN apk update \
&&  apk upgrade \
&&  apk add --no-cache --virtual .build-deps build-base git mercurial go glide bash tar \
&&  apk add --no-cache curl \
&&  curl -fsSL -o /usr/local/bin/dep https://github.com/golang/dep/releases/download/v${DEP_VERSION}/dep-linux-amd64 \
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
&&  rm -rf /build \
&&  rm -rf /root/.glide
