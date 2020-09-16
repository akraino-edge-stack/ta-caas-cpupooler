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

%define COMPONENT cpupooler
%define RPM_NAME caas-%{COMPONENT}
%define RPM_MAJOR_VERSION 0.3.1
%define RPM_MINOR_VERSION 15
%define CPUPOOLER_VERSION 0adced79e87e4cb87c41a70a654be377ca2d505f
%define IMAGE_TAG %{RPM_MAJOR_VERSION}-%{RPM_MINOR_VERSION}
%define PROCESS_STARTER_INSTALL_PATH /opt/bin/
%define PROJECT_NAME CPU-Pooler
%define PROJECT_BUILD_ROOT %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}

Name:           %{RPM_NAME}
Version:        %{RPM_MAJOR_VERSION}
Release:        %{RPM_MINOR_VERSION}%{?dist}
Summary:        Containers as a Service cpu-pooler component
License:        %{_platform_license} and BSD 3-Clause License
URL:            https://github.com/nokia/%{PROJECT_NAME}
BuildArch:      %{_arch}
Vendor:         %{_platform_vendor} and Nokia
Source0:        %{name}-%{version}.tar.gz
Source1:        %{url}/archive/%{CPUPOOLER_VERSION}.tar.gz

Requires: docker-ce >= 18.09.2, rsync
BuildRequires: docker-ce-cli >= 18.09.2, xz, wget

# I was able to pack an executable via this.
# more info at https://fedoraproject.org/wiki/Packaging:Debuginfo
%global debug_package %{nil}

%description
This RPM contains the cpu-pooler container image, process-starter binary and related deployment artifacts for the CaaS subsystem.

%prep
wget --progress=dot:giga --directory-prefix=%{_sourcedir} %{url}/archive/%{CPUPOOLER_VERSION}.tar.gz
%autosetup
# Autosetup extracts Source1 tar.gz to build directory and changes directory into it
%autosetup -b 1 -T -n %{PROJECT_NAME}-%{CPUPOOLER_VERSION}

%build
# build the cpu-pooler multi-binary image
docker build \
  --build-arg http_proxy \
  --build-arg https_proxy \
  --build-arg no_proxy \
  --tag %{COMPONENT}:%{IMAGE_TAG} \
  -f %{PROJECT_BUILD_ROOT}/docker-build/%{COMPONENT}/Dockerfile \
  %{_builddir}/%{PROJECT_NAME}-%{CPUPOOLER_VERSION}

# build the builder image containing the binaries
docker build \
  --build-arg http_proxy \
  --build-arg https_proxy \
  --build-arg no_proxy \
  --target builder \
  --tag %{COMPONENT}:builder \
  -f %{PROJECT_BUILD_ROOT}/docker-build/%{COMPONENT}/Dockerfile \
  %{_builddir}/%{PROJECT_NAME}-%{CPUPOOLER_VERSION}

# create a directory for process-starter binary
mkdir -p %{PROJECT_BUILD_ROOT}/results

# run the builder container for process-starter binary
docker create --name=%{COMPONENT}-temp %{COMPONENT}:builder

# extract process-starter binary
docker cp %{COMPONENT}-temp:/process-starter %{PROJECT_BUILD_ROOT}/results/

# rm container
docker rm -v %{COMPONENT}-temp

# create a save folder
mkdir -p %{PROJECT_BUILD_ROOT}/docker-save/

# save the cpu poooler container
docker save %{COMPONENT}:%{IMAGE_TAG} | xz -z -T2 > %{PROJECT_BUILD_ROOT}/docker-save/%{COMPONENT}:%{IMAGE_TAG}.tar

# remove docker images, containers
docker rmi -f %{COMPONENT}:%{IMAGE_TAG} %{COMPONENT}:builder
docker container prune --force
docker image prune --force

%install
mkdir -p %{buildroot}/%{_caas_container_tar_path}/
rsync -av %{PROJECT_BUILD_ROOT}/docker-save/%{COMPONENT}:%{IMAGE_TAG}.tar %{buildroot}/%{_caas_container_tar_path}/

mkdir -p %{buildroot}%{PROCESS_STARTER_INSTALL_PATH}
rsync -av %{PROJECT_BUILD_ROOT}/results/process-starter %{buildroot}/%{PROCESS_STARTER_INSTALL_PATH}/

mkdir -p %{buildroot}/%{_playbooks_path}/
rsync -av %{PROJECT_BUILD_ROOT}/ansible/playbooks/cpupooler.yaml %{buildroot}/%{_playbooks_path}/

mkdir -p %{buildroot}/%{_roles_path}/
rsync -av %{PROJECT_BUILD_ROOT}/ansible/roles/cpupooler %{buildroot}/%{_roles_path}/

%files
%{_caas_container_tar_path}/%{COMPONENT}:%{IMAGE_TAG}.tar
%{PROCESS_STARTER_INSTALL_PATH}/process-starter
%{_playbooks_path}/cpupooler.yaml
%{_roles_path}/cpupooler

%preun

%post
mkdir -p %{_postconfig_path}/
ln -sf %{_playbooks_path}/cpupooler.yaml %{_postconfig_path}/

%postun
if [ $1 -eq 0 ]; then
    rm -f %{_postconfig_path}/cpupooler.yaml
fi

%clean
rm -rf ${buildroot}