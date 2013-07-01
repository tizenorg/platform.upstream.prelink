Name:           prelink
BuildRequires:  gcc-c++
BuildRequires:  glibc-devel-static
BuildRequires:  libelf0-devel
Summary:        An ELF Prelinking Utility
License:        GPL-2.0+
Group:          System/Base
Version:        20111012
Release:        0
Url:            http://people.redhat.com/jakub/prelink/
Source:         http://people.redhat.com/jakub/prelink/%name-%version.tar.bz2
Source2:        %name.conf
Source1001: 	prelink.manifest
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
cp %{SOURCE1001} .

%build
# This package failed when testing with -Wl,-as-needed being default.
# So we disable it here, if you want to retest, just delete this comment and the line below.
export LD_AS_NEEDED=0
# Uninitialized memory in dynamic loader in ifunc3 test.
export -n MALLOC_PERTURB_
unset MALLOC_PERTURB_

CFLAGS="$RPM_OPT_FLAGS" \
./configure --prefix=/usr --mandir=%{_mandir} || cat config.log
make %{?jobs:-j%jobs}

%check
make -C testsuite check-harder

%install
make install DESTDIR=$RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/etc
sed -e "s,LIBDIR,%_lib," %{SOURCE2} > $RPM_BUILD_ROOT/etc/prelink.conf
mkdir -p $FILLUP_DIR $RPM_BUILD_ROOT/sbin/conf.d
install -m 0755 -d $RPM_BUILD_ROOT/var/lib/prelink
mkdir -p $RPM_BUILD_ROOT/etc/rpm
cat > $RPM_BUILD_ROOT/etc/rpm/macros.prelink <<EOF
# rpm-4.1 verifies prelinked libraries using a prelink undo helper.
#       Note: The 2nd token is used as argv[0] and "library" is a
#       placeholder that will be deleted and replaced with the appropriate
#       library file path.
%__prelink_undo_cmd     /usr/sbin/prelink prelink -y library
EOF


%docs_package

%files
%manifest %{name}.manifest
%license COPYING
%defattr(-,root,root)
%dir /var/lib/prelink
%dir /etc/rpm
%config(noreplace) /etc/prelink.conf
%config /etc/rpm/macros.prelink
%_sbindir/prelink
%_bindir/execstack

%changelog
