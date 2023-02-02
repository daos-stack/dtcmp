%global with_mpich 1
%if (0%{?rhel} >= 8)
%global with_openmpi 1
%global with_openmpi3 0
%else
%global with_openmpi 0
%global with_openmpi3 1
%endif

%if (0%{?suse_version} >= 1500)
%global module_load() if [ "%{1}" == "openmpi3" ]; then MODULEPATH=/usr/share/modules module load gnu-openmpi; else MODULEPATH=/usr/share/modules module load gnu-%{1}; fi
%else
%global module_load() module load mpi/%{1}-%{_arch}
%endif

%if %{with_mpich}
%global mpi_list mpich
%endif
%if %{with_openmpi}
%global mpi_list %{?mpi_list} openmpi
%endif
%if %{with_openmpi3}
%if 0%{?fedora}
# this would be nice to use but causes issues with linting
# since that is done on Fedora
#{error: openmpi3 doesn't exist on Fedora}
%endif
%global mpi_list %{?mpi_list} openmpi3
%endif

%if (0%{?suse_version} >= 1500)
%global mpi_libdir %{_libdir}/mpi/gcc
%global mpi_lib_ext lib64
%global mpi_includedir %{_libdir}/mpi/gcc
%global mpi_include_ext /include
%else
%global mpi_libdir %{_libdir}
%global mpi_lib_ext lib
%global mpi_includedir  %{_includedir}
%global mpi_include_ext -%{_arch}
%endif

Name:		dtcmp
Version:	1.1.4
Release:	1%{?dist}
Summary:	Datatype Compare Library for sorting and ranking distributed data using MPI
License:	BSD
URL:		https://github.com/LLNL/dtcmp
Source0:	https://github.com/LLNL/dtcmp/releases/download/v%version/dtcmp-%version.tar.gz
Patch1:		dtcmp-sover.patch
BuildRequires:	automake
%if (0%{?suse_version} >= 1500)
BuildRequires: lua-lmod
%else
BuildRequires: Lmod
%endif

%description
The Datatype Comparison (DTCMP) Library provides pre-defined and
user-defined comparison operations to compare the values of two items
which can be arbitrary MPI datatypes.

%if %{with_openmpi}
%package openmpi
Summary:	Datatype Compare Library for sorting and ranking distributed data using MPI
BuildRequires:	openmpi-devel
BuildRequires:	lwgrp-openmpi-devel

%description openmpi
The Datatype Comparison (DTCMP) Library provides pre-defined and
user-defined comparison operations to compare the values of two items
which can be arbitrary MPI datatypes.

%package openmpi-devel
Summary:	Development files for %{name}-openmpi
Requires: lwgrp-openmpi-devel
Requires:	%{name}-openmpi%{?_isa} = %version-%release

%description openmpi-devel
Development files for %{name}-openmpi.
%endif

%if %{with_openmpi3}
%package openmpi3
Summary:	Datatype Compare Library for sorting and ranking distributed data using MPI
BuildRequires:	openmpi3-devel
BuildRequires:	lwgrp-openmpi3-devel

%description openmpi3
The Datatype Comparison (DTCMP) Library provides pre-defined and
user-defined comparison operations to compare the values of two items
which can be arbitrary MPI datatypes.

%if (0%{?suse_version} >= 1500)
%package -n libdtcmp0-openmpi3
Summary:	Datatype Compare Library for sorting and ranking distributed data using MPI

%description -n libdtcmp0-openmpi3
Shared libraries for %{name}-openmpi3.
%endif

%package openmpi3-devel
Summary:	Development files for %{name}-openmpi3
Requires: lwgrp-openmpi3-devel
%if (0%{?suse_version} >= 1500)
Requires: libdtcmp0-openmpi3%{_isa} = %version-%release
%else
Requires:	%{name}-openmpi3%{?_isa} = %version-%release
%endif

%description openmpi3-devel
Development files for %{name}-openmpi3.
%endif

%if %{with_mpich}
%package mpich
Summary:	Datatype Compare Library for sorting and ranking distributed data using MPI
BuildRequires:	mpich-devel
BuildRequires:	lwgrp-mpich-devel

%description mpich
The Datatype Comparison (DTCMP) Library provides pre-defined and
user-defined comparison operations to compare the values of two items
which can be arbitrary MPI datatypes.

%if (0%{?suse_version} >= 1500)
%package -n libdtcmp0-mpich
Summary:	Datatype Compare Library for sorting and ranking distributed data using MPI

%description -n libdtcmp0-mpich
Shared libraries for %{name}-mpich.
%endif

%package mpich-devel
Summary:	Development files for %{name}-mpich
Requires: lwgrp-mpich-devel
%if (0%{?suse_version} >= 1500)
Requires: libdtcmp0-mpich%{_isa} = %version-%release
%else
Requires:	%{name}-mpich%{?_isa} = %version-%release
%endif

%description mpich-devel
Development files for %{name}-mpich.
%endif

%prep
%autosetup -p1
# sadly, even though the patch above patches configure also,
# make still wants to rebuild Makefile.in, saying it's older
# than Makefile.am, when it's not really
autoreconf

%build
%global _configure ../configure
export CC=mpicc
for mpi in %{?mpi_list}; do
  mkdir $mpi
  pushd $mpi
  %module_load $mpi
  %configure --includedir=%{mpi_includedir}/$mpi%{mpi_include_ext} --libdir=%{mpi_libdir}/$mpi/%{mpi_lib_ext} --disable-static --with-lwgrp
  %make_build
  module purge
  popd
done

%install
for mpi in %{?mpi_list}; do
  %module_load $mpi
  %make_install -C $mpi
  rm %{buildroot}/%{mpi_libdir}/$mpi/%{mpi_lib_ext}/*.la
  rm -r %{buildroot}%{_datadir}/dtcmp
  module purge
done

%if %{with_openmpi}
%files openmpi
%{mpi_libdir}/openmpi/%{mpi_lib_ext}/libdtcmp.so.*

%files openmpi-devel
%{mpi_includedir}/openmpi%{mpi_include_ext}/dtcmp.h
%{mpi_libdir}/openmpi/%{mpi_lib_ext}/libdtcmp.so
%{mpi_libdir}/openmpi/%{mpi_lib_ext}/pkgconfig/libdtcmp.pc
%endif

%if %{with_openmpi3}
%if (0%{?suse_version} >= 1500)
%files -n libdtcmp0-openmpi3
%else
%files openmpi3
%endif
%{mpi_libdir}/openmpi3/%{mpi_lib_ext}/libdtcmp.so.*

%files openmpi3-devel
%{mpi_includedir}/openmpi3%{mpi_include_ext}/dtcmp.h
%{mpi_libdir}/openmpi3/%{mpi_lib_ext}/libdtcmp.so
%{mpi_libdir}/openmpi3/%{mpi_lib_ext}/pkgconfig/libdtcmp.pc
%endif

%if %{with_mpich}
%if (0%{?suse_version} >= 1500)
%files -n libdtcmp0-mpich
%else
%files mpich
%endif
%{mpi_libdir}/mpich/%{mpi_lib_ext}/libdtcmp.so.*

%files mpich-devel
%{mpi_includedir}/mpich%{mpi_include_ext}/dtcmp.h
%{mpi_libdir}/mpich/%{mpi_lib_ext}/libdtcmp.so
%{mpi_libdir}/mpich/%{mpi_lib_ext}/pkgconfig/libdtcmp.pc
%endif

%changelog
* Wed Feb  1 2023 Brian J. Murrell <brian.murrell@intel.com> - 1.1.4-1
- New upstream release

* Mon May 17 2021 Brian J. Murrell <brian.murrell@intel.com> - 1.1.1-2
- Package for openmpi on EL8

* Thu Feb 04 2021 Dalton A. Bohning <daltonx.bohning@intel.com> - 1.1.1-1
- Update to version 1.1.1

* Mon Sep 28 2020 Brian J. Murrell <brian.murrell@intel.com> - 1.0.3-1.2
- Add patch to fix lwgrp discovery
- Package for multiple MPI stacks and multiple distros

* Tue Sep 22 2020 John E. Malmberg <john.e.malmberg@intel.com> - 1.0.3-1.1
- Change to use openmpi3

* Wed Sep 20 2017 Dave Love <loveshack@fedoraproject.org> - 1.0.3-1
- Initial packaging
