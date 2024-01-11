Name:		fuse3
Version:	3.10.2
Release:	6%{?dist}
Summary:	File System in Userspace (FUSE) v3 utilities
License:	GPL+
URL:		http://fuse.sf.net
Source0:	https://github.com/libfuse/libfuse/archive/fuse-%{version}.tar.gz
Source1:	fuse.conf
Patch0:		fuse3-gcc11.patch
Patch1:		fuse-3.10.4-fix-test-failure.patch
Patch2:		fuse-3.11.0-Modify-structures-in-libfuse-to-handle-flags-beyond-.patch
Patch3:		fuse-3.13.0-Initial-patch-provided-by-Miklos-Szeredi-mszeredi-re.patch
Patch4:		fuse-3.13.0-adding-comments-and-capability-discovery-enum-for-fl.patch
Patch5:		rhel-only-bz2188182-libfuse-add-feature-flag-for-expire-only.patch

BuildRequires:	which
%if ! 0%{?el6}
Conflicts:	filesystem < 3
%endif
BuildRequires:	libselinux-devel
BuildRequires:	meson, ninja-build, gcc, gcc-c++
%if ! 0%{?el6} && ! 0%{?el7}
BuildRequires:	systemd-udev
%endif
%if 0%{?el6}
BuildRequires:	udev, kernel-devel
%else
Requires:	%{_sysconfdir}/fuse.conf
%endif

Requires:	%{name}-libs = %{version}-%{release}
# fuse-common 3.4.2-3 had the fuse & fuse3 man pages in it
Conflicts:	fuse-common < 3.4.2-4

%description
With FUSE it is possible to implement a fully functional filesystem in a
userspace program. This package contains the FUSE v3 userspace tools to
mount a FUSE filesystem.

%package libs
Summary:	File System in Userspace (FUSE) v3 libraries
License:	LGPLv2+
%if ! 0%{?el6}
Conflicts:	filesystem < 3
%endif

%description libs
Devel With FUSE it is possible to implement a fully functional filesystem in a
userspace program. This package contains the FUSE v3 libraries.

%package devel
Summary:	File System in Userspace (FUSE) v3 devel files
Requires:	%{name}-libs = %{version}-%{release}
Requires:	pkgconfig
License:	LGPLv2+
%if ! 0%{?el6}
Conflicts:	filesystem < 3
%endif

%description devel
With FUSE it is possible to implement a fully functional filesystem in a
userspace program. This package contains development files (headers,
pgk-config) to develop FUSE v3 based applications/filesystems.

%if ! 0%{?el6} && ! 0%{?el7}
%package -n fuse-common
Summary:	Common files for File System in Userspace (FUSE) v2 and v3
License:	GPL+

%description -n fuse-common
Common files for FUSE v2 and FUSE v3.
%endif

%prep
%setup -n libfuse-fuse-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

%build
export LC_ALL=en_US.UTF-8
%if ! 0%{?_vpath_srcdir:1}
%global _vpath_srcdir .
%endif
%if ! 0%{?_vpath_builddir:1}
%global _vpath_builddir build
%endif
%if 0%{?el6}
%if ! 0%{?__global_ldflags:1}
%global __global_ldflags ""
%endif
%meson -D udevrulesdir=/etc/udev/rules.d
%else
%meson
%endif

(cd %{_vpath_builddir}
%if 0%{?el6}
meson configure -D c_args=-I"`ls -d /usr/src/kernels/*/include|head -1`"
%endif
%if 0%{?el6} || 0%{?el7}
meson configure -D examples=false
%endif
# don't have root for installation
meson configure -D useroot=false
ninja-build reconfigure
)
%meson_build

%install
export MESON_INSTALL_DESTDIR_PREFIX=%{buildroot}/usr %meson_install
find %{buildroot} .
find %{buildroot} -type f -name "*.la" -exec rm -f {} ';'
# change from 4755 to 0755 to allow stripping -- fixed later in files
chmod 0755 %{buildroot}/%{_bindir}/fusermount3

# Get rid of static libs
rm -f %{buildroot}/%{_libdir}/*.a
# No need to create init-script
rm -f %{buildroot}%{_sysconfdir}/init.d/fuse3

%if 0%{?el6} || 0%{?el7}
# This is in the fuse package on el7 and there's no default on el6
rm -f %{buildroot}%{_sysconfdir}/fuse.conf
%else
# Install config-file
install -p -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}
%endif

# Delete pointless udev rules, which do not belong in /usr/lib (brc#748204)
rm -f %{buildroot}/usr/lib/udev/rules.d/99-fuse3.rules

%if 0%{?el6} || 0%{?el7}
%post -p /sbin/ldconfig libs
%postun -p /sbin/ldconfig libs
%else
%ldconfig_scriptlets libs
%endif

%{!?_licensedir:%global license %%doc}

%files
%license LICENSE GPL2.txt
%doc AUTHORS ChangeLog.rst README.md
%{_sbindir}/mount.fuse3
%attr(4755,root,root) %{_bindir}/fusermount3
%{_mandir}/man1/*
%{_mandir}/man8/*
%if 0%{?el6}
%{_sysconfdir}/udev/rules.d/*
%endif

%files libs
%license LGPL2.txt
%{_libdir}/libfuse3.so.*

%files devel
%{_libdir}/libfuse3.so
%{_libdir}/pkgconfig/fuse3.pc
%{_includedir}/fuse3/

%if ! 0%{?el6} && ! 0%{?el7}
%files -n fuse-common
%config(noreplace) %{_sysconfdir}/fuse.conf
%endif

%changelog
* Thu Jul 13 2023 Pavel Reichl <preichl@redhat.com> - 3.10.2-6
- Fix feature_notify_inode_expire_only related(rhbz#2188182)

* Wed Feb 16 2022 Pavel Reichl <preichl@redhat.com> - 3.10.2-5
- Fix test failure
- Fix missing dependency

* Tue Feb 15 2022 Pavel Reichl <preichl@redhat.com> - 3.10.2-4
- Add gating.yaml file

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 3.10.2-3
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Thu Apr 15 2021 Mohan Boddu <mboddu@redhat.com> - 3.10.2-2
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Fri Feb  5 2021 Tom Callaway <spot@fedoraproject.org> - 3.10.2-1
- update to 3.10.2

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 3.10.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Dec  7 2020 Tom Callaway <spot@fedoraproject.org> - 3.10.1-1
- update to 3.10.1

* Wed Oct 14 2020 Jeff Law <law@redhat.com> - 3.10.0-2
- Add missing #include for gcc-11

* Mon Oct 12 2020 Tom Callaway <spot@fedoraproject.org> - 3.10.0-1
- update to 3.10.0
- enable lto

* Mon Aug 10 2020 Tom Callaway <spot@fedoraproject.org> - 3.9.4-1
- update to 3.9.4

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 3.9.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jul  1 2020 Jeff Law <law@redhat.com> - 3.9.2-2
- Disable LTO

* Thu Jun 18 2020 Tom Callaway <spot@fedoraproject.org> - 3.9.2-1
- update to 3.9.2

* Thu Mar 19 2020 Tom Callaway <spot@fedoraproject.org> - 3.9.1-1
- update to 3.9.1

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 3.9.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Mon Dec 16 2019 Tom Callaway <spot@fedoraproject.org> - 3.9.0-1
- update to 3.9.0

* Mon Nov  4 2019 Tom Callaway <spot@fedoraproject.org> - 3.8.0-1
- update to 3.8.0

* Fri Sep 27 2019 Tom Callaway <spot@fedoraproject.org> - 3.7.0-1
- update to 3.7.0

* Sun Sep  1 2019 Peter Lemenkov <lemenkov@gmail.com> - 3.6.2-1
- Update to 3.6.2

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 3.6.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed Jul 03 2019 Dave Dykstra <dwd@fedoraproject.org> - 3.6.1-3
- Update to the final version of pr #421

* Wed Jul 03 2019 Dave Dykstra <dwd@fedoraproject.org> - 3.6.1-2
- Update to newer version of pr #421
- Disable building examples on el7

* Thu Jun 13 2019 Tom Callaway <spot@fedoraproject.org> - 3.6.1-1
- Update to 3.6.1

* Fri May 24 2019 Dave Dykstra <dwd@fedoraproject.org> - 3.5.0-1
- Upgrade to upstream 3.5.0

* Sat May 04 2019 Dave Dykstra <dwd@fedoraproject.org> - 3.4.2-7
- Fix building on el6

* Wed May 01 2019 Dave Dykstra <dwd@fedoraproject.org> - 3.4.2-6
- Need Conflicts: fuse-common < 3.4.2-4, because <= 3.4.2-3 isn't quite
  enough.

* Wed May 01 2019 Dave Dykstra <dwd@fedoraproject.org> - 3.4.2-5
- Update the Conflicts: fuse-common <= version to 3.4.2-3

* Wed May 01 2019 Dave Dykstra <dwd@fedoraproject.org> - 3.4.2-4
- Bump release number in order to larger than a rebuild of fuse package
  done before separation pull request was merged.

* Mon Apr 08 2019 Dave Dykstra <dwd@fedoraproject.org> - 3.4.2-3
- Separate out from fuse package
