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

ARG CENTOS_BASE
FROM $CENTOS_BASE
MAINTAINER Balazs Szekeres <balazs.szekeres@nokia.com>

ARG DEP_MAN_VERSION
ARG go_install_dir="/usr/local/go"
ARG go_version
ENV GOBIN=/usr/local/bin
ENV GOPATH /build
ENV PATH="$GOPATH/bin:$go_install_dir/bin:$PATH"
ARG CPUPOOLER_VERSION

RUN yum update -y \
&&  yum install -y \
      git \
      bash \
      glide \
      libtool \
      autoconf \
      coreutils \
      curl \
      binutils \
      tar \
      grep \
      make \
      gcc \
      gcc-c++ \
&&  mkdir -p $go_install_dir \
&&  if [ $(uname -m) == 'aarch64' ]; then HOST_ARCH=arm64; else HOST_ARCH=amd64; fi \
&&  curl -fsSL -k https://dl.google.com/go/go${go_version}.linux-$HOST_ARCH.tar.gz | tar zx --strip-components=1 -C ${go_install_dir} \
&&  curl -fsSL -o /usr/local/bin/dep https://github.com/golang/dep/releases/download/v${DEP_MAN_VERSION}/dep-linux-$HOST_ARCH \
&&  chmod +x /usr/local/bin/dep \
&&  mkdir -p $GOPATH/src/github.com/nokia/CPU-Pooler \
&&  git clone https://github.com/nokia/CPU-Pooler.git $GOPATH/src/github.com/nokia/CPU-Pooler \
&&  cd $GOPATH/src/github.com/nokia/CPU-Pooler \
&&  git fetch --tags \
&&  git checkout ${CPUPOOLER_VERSION} \
&&  dep ensure --vendor-only \
# process-starter
&&  CGO_ENABLED=0 GOOS=linux go build -a -ldflags '-extldflags "-static"' -o process-starter ./cmd/process-starter \
&&  mv $GOPATH/src/github.com/nokia/CPU-Pooler/process-starter /process-starter \
&&  rm -rf $go_install_dir \
&&  rm -rf $GOPATH
