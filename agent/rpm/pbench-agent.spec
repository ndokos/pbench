Name:           pbench-agent
Version:     0.60
%define gdist gc9e89f8f
Release:     1%{?gdist}%{!?gdist:}
Summary:        The pbench harness

License:        GPLv3+
URL:            http://perf1.perf.lab.eng.bos.redhat.com/atheurer/pbench
Source0:        pbench-agent-%{version}.tar.gz
Buildarch:      noarch


%if 0%{?rhel} == 6
%define turbostatpkg cpupowerutils
%else
%define turbostatpkg kernel-tools
%endif

%if 0%{?rhel} == 7
Requires:  scl-utils, rh-python36
%endif

%if 0%{?rhel} == 8 || 0%{?fedora} >= 29
Requires:  python3-pip
%endif

%if 0%{?fedora} == 0
# NOT fedora
%define perljsonxs pbench-perl-JSON-XS
%else
%define perljsonxs perl-JSON-XS
%endif


Requires:  bzip2, tar, xz, screen
Requires:  perl, perl-JSON, %{perljsonxs}, perl-Time-HiRes, perl-Data-UUID
Requires:  net-tools, numactl, perf, psmisc, bc, sos, %{turbostatpkg}
# The following are needed by UBI containers which are bare bones - most other
# systems will probably already have them installed.
Requires:  ansible hostname iproute procps-ng iputils openssh-server openssh-clients rsync

Obsoletes: pbench <= 0.34
Conflicts: pbench <= 0.34
# configtools is packaged with pbench-agent, so we specifically do NOT want the configtools
# RPM installed.
Conflicts: configtools

Patch0: stockpile-shebang.patch

%define installdir opt/pbench-agent

%description
The pbench harness

%prep

%setup
%patch0 -p1

%build

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/%{installdir}

cd ./agent
%{__make} install DESTDIR=%{?buildroot}/%{installdir} INSTALL="%{__install} -p"
%{__make} install-build-artifacts DESTDIR=%{?buildroot}/%{installdir} INSTALL="%{__install} -p"

# we don't need this
rm %{?buildroot}/%{installdir}/Makefile

%pre
# this RPM conflicts with a configtools RPM, but we may have a Pypi
# configtools installed: zap it.
%if 0%{?rhel} == 7
scl enable rh-python36 -- bash -c 'if pip3 show configtools > /dev/null 2>&1 ;then pip3 uninstall -y configtools ;fi'
%endif

%if 0%{?rhel} == 8 || 0%{?fedora} >= 29
if pip3 show configtools > /dev/null 2>&1 ;then pip3 uninstall -y configtools ;fi
%endif

%post
# link the pbench profile, so it'll automatically be sourced on login
ln -sf /%{installdir}/profile /etc/profile.d/pbench-agent.sh

%preun
# if uninstalling, rather than updating, delete the link
if [ $1 -eq 0 ] ;then
    rm -f /etc/profile.d/pbench-agent.sh
fi

%postun
# if uninstalling, rather than updating, remove /%{installdir}
if [ $1 -eq 0 ] ;then
    rm -rf /%{installdir}
fi

%posttrans

%files
%defattr(775,pbench,pbench,775)
/%{installdir}/config

/%{installdir}/lib
/%{installdir}/ansible
/%{installdir}/base

/%{installdir}/VERSION
/%{installdir}/SEQNO
/%{installdir}/SHA1
/%{installdir}/profile

%ghost %attr(0400,pbench,pbench) /%{installdir}/id_rsa
%ghost %attr(0664,pbench,pbench) /%{installdir}/config/pbench-agent.cfg

%defattr(775,pbench,pbench,775)
/%{installdir}/util-scripts
/%{installdir}/tool-scripts
/%{installdir}/bench-scripts

# stockpile
%defattr(775,pbench,pbench,775)
/%{installdir}/stockpile

