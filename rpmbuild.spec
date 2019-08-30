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
%define COMPONENT_PART process-starter
%define RPM_NAME caas-%{COMPONENT}
%define RPM_MAJOR_VERSION 0.3.0
%define RPM_MINOR_VERSION 2
%define CPUPOOLER_VERSION d94704e4b2f9f91ee712c6385038413fb7aa064a
%define DEPENDENCY_MANAGER_VERSION 0.5.0
%define IMAGE_TAG %{RPM_MAJOR_VERSION}-%{RPM_MINOR_VERSION}
%define PROCESS_STARTER_INSTALL_PATH /opt/bin/

Name:           %{RPM_NAME}
Version:        %{RPM_MAJOR_VERSION}
Release:        %{RPM_MINOR_VERSION}%{?dist}
Summary:        Containers as a Service cpu-pooler component
License:        %{_platform_license} and BSD 3-Clause License
URL:            https://github.com/nokia/CPU-Pooler
BuildArch:      x86_64
Vendor:         %{_platform_vendor} and Nokia
Source0:        %{name}-%{version}.tar.gz

Requires: docker-ce >= 18.09.2, rsync
BuildRequires: docker-ce-cli >= 18.09.2, xz

# I was able to pack an executable via this.
# more info at https://fedoraproject.org/wiki/Packaging:Debuginfo
%global debug_package %{nil}

%description
This RPM contains the cpu-pooler container image, process-starter binary and related deployment artifacts for the CaaS subsystem.

%prep
%autosetup

%build
# build the process-starter binary inside a builder conatiner
docker build \
  --network=host \
  --no-cache \
  --force-rm \
  --build-arg HTTP_PROXY="${http_proxy}" \
  --build-arg HTTPS_PROXY="${https_proxy}" \
  --build-arg NO_PROXY="${no_proxy}" \
  --build-arg http_proxy="${http_proxy}" \
  --build-arg https_proxy="${https_proxy}" \
  --build-arg no_proxy="${no_proxy}" \
  --build-arg DEPENDENCY_MANAGER="%{DEPENDENCY_MANAGER_VERSION}" \
  --build-arg CPUPOOLER="%{CPUPOOLER_VERSION}" \
  --tag %{COMPONENT_PART}:builder \
  %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/docker-build/%{COMPONENT_PART}/

# create a directory for process-starter binary
mkdir -p %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/results

# run the builder conatiner for process-starter binary
docker run \
  -id \
  --rm \
  --network=host \
  --privileged \
  -e HTTP_PROXY="${http_proxy}" \
  -e HTTPS_PROXY="${https_proxy}" \
  -e NO_PROXY="${no_proxy}" \
  -e http_proxy="${http_proxy}" \
  -e https_proxy="${https_proxy}" \
  -e no_proxy="${no_proxy}" \
  --entrypoint=/bin/sh \
  %{COMPONENT_PART}:builder

# get the process-starter binary
docker cp $(docker ps | grep "%{COMPONENT_PART}:builder" | awk -F' ' '{ print $1 }'):/process-starter %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/results/

# rm container
for container_ran in $(docker ps -a | grep "%{COMPONENT_PART}:builder" | awk -F' ' '{ print $1 }')
do
    docker rm -f $container_ran
done

# remove docker image
docker rmi -f %{COMPONENT_PART}:builder

# build the cpu pooler
docker build \
  --network=host \
  --no-cache \
  --force-rm \
  --build-arg HTTP_PROXY="${http_proxy}" \
  --build-arg HTTPS_PROXY="${https_proxy}" \
  --build-arg NO_PROXY="${no_proxy}" \
  --build-arg http_proxy="${http_proxy}" \
  --build-arg https_proxy="${https_proxy}" \
  --build-arg no_proxy="${no_proxy}" \
  --build-arg DEPENDENCY_MANAGER="%{DEPENDENCY_MANAGER_VERSION}" \
  --build-arg CPUPOOLER="%{CPUPOOLER_VERSION}" \
  --tag %{COMPONENT}:%{IMAGE_TAG} \
  %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/docker-build/%{COMPONENT}/

# create a save folder
mkdir -p %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/docker-save/

# save the cpu poooler container
docker save %{COMPONENT}:%{IMAGE_TAG} | xz -z -T2 > %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/docker-save/%{COMPONENT}:%{IMAGE_TAG}.tar

# remove docker image
docker rmi -f %{COMPONENT}:%{IMAGE_TAG}

%install
mkdir -p %{buildroot}/%{_caas_container_tar_path}/
rsync -av %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/docker-save/%{COMPONENT}:%{IMAGE_TAG}.tar %{buildroot}/%{_caas_container_tar_path}/

mkdir -p %{buildroot}%{PROCESS_STARTER_INSTALL_PATH}
rsync -av %{_builddir}/%{RPM_NAME}-%{RPM_MAJOR_VERSION}/results/process-starter %{buildroot}/%{PROCESS_STARTER_INSTALL_PATH}/

mkdir -p %{buildroot}/%{_playbooks_path}/
rsync -av ansible/playbooks/cpupooler.yaml %{buildroot}/%{_playbooks_path}/

mkdir -p %{buildroot}/%{_roles_path}/
rsync -av ansible/roles/cpupooler %{buildroot}/%{_roles_path}/

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
