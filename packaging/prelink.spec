Name:           prelink
Version:        20111012
Release:        0
License:        GPL-2.0+
Summary:        An ELF Prelinking Utility
Url:            http://people.redhat.com/jakub/prelink/
Group:          System/Base
Source:         http://people.redhat.com/jakub/prelink/%{name}-%{version}.tar.bz2
Source2:        %{name}.conf
Patch0:         %{name}-make_it_cool.diff
Patch3:         %{name}-tests.diff
Patch4:         %{name}-make-dry-run-verbose.diff
Patch5:         fix-copydtneeded.patch
BuildRequires:  gcc-c++
BuildRequires:  glibc-devel-static
BuildRequires:  libelf0-devel
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
# It does not work at all on ia64, so let's listen upstream supported
# architectures
ExclusiveArch:  %{ix86} alpha sparc sparc64 s390 s390x x86_64 ppc ppc64

%description
The prelink program is a utility that modifies shared libraries and
executables in the ELF format so that far less relocations need to be
resolved at run time.  This decreases program start-up time.

Be aware that prelink can modify all libraries and executables on your
system. Applications which monitor changes in files or RPM itself
will no longer work.

%prep
%setup -q -n prelink
%patch0 -p0
%patch3 -p0
%patch4 -p0
%patch5 -p1

%build
# This package failed when testing with -Wl,-as-needed being default.
# So we disable it here, if you want to retest, just delete this comment and the line below.
export LD_AS_NEEDED=0
# Uninitialized memory in dynamic loader in ifunc3 test.
export -n MALLOC_PERTURB_
unset MALLOC_PERTURB_

CFLAGS="%{optflags}" \
./configure --prefix=/usr --mandir=%{_mandir} || cat config.log
make %{?_smp_mflags}

%check
make -C testsuite check-harder

%install
%make_install
mkdir -p %{buildroot}/etc
sed -e "s,LIBDIR,%{_lib}," %{SOURCE2} > %{buildroot}%{_sysconfdir}/prelink.conf
mkdir -p $FILLUP_DIR %{buildroot}/sbin/conf.d
install -m 0755 -d %{buildroot}%{_localstatedir}/lib/prelink
mkdir -p %{buildroot}%{_sysconfdir}/rpm
cat > %{buildroot}%{_sysconfdir}/rpm/macros.prelink <<EOF
# rpm-4.1 verifies prelinked libraries using a prelink undo helper.
#       Note: The 2nd token is used as argv[0] and "library" is a
#       placeholder that will be deleted and replaced with the appropriate
#       library file path.
%__prelink_undo_cmd     /usr/sbin/prelink prelink -y library
EOF


%docs_package

%files
%defattr(-,root,root)
%dir %{_localstatedir}/lib/prelink
%dir %{_sysconfdir}/rpm
%config(noreplace) %{_sysconfdir}/prelink.conf
%config %{_sysconfdir}/rpm/macros.prelink
%{_sbindir}/prelink
%{_bindir}/execstack

%changelog
