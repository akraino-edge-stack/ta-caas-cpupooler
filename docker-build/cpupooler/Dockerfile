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

ARG BUILDER_BASE=golang:1.13-alpine
ARG FINAL_BASE=alpine:3.9.6
ARG PROJECT_PATH=github.com/nokia/CPU-Pooler

# Build stage
FROM ${BUILDER_BASE} AS builder
ARG PROJECT_PATH
ENV CGO_ENABLED=0
ENV GOOS=linux

RUN apk add curl git
WORKDIR ${GOPATH}/src/${PROJECT_PATH}/bin
WORKDIR ${GOPATH}/src/${PROJECT_PATH}
ADD go.* ./
RUN go mod download
ADD . ./
RUN go build -a -ldflags '-extldflags "-static"' -o bin/ ${PROJECT_PATH}/cmd/...
RUN mv bin/cpusetter bin/cpu-setter
RUN mv bin/webhook bin/cpu-device-webhook
RUN mv bin/process-starter /process-starter

# Multi-binary image stage
FROM ${FINAL_BASE}
MAINTAINER Gabor Mate <gabor.mate@nokia.com>
ARG PROJECT_PATH

RUN apk add util-linux
COPY --from=builder /go/src/${PROJECT_PATH}/bin/cpu-* /

ENTRYPOINT ["/bin/sh"]