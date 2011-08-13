# TODO
# - -Wl,-q broken for gcc 4.6 (gcc 4.5 is ok)
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine	with_dist_kernel
%endif
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif
%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		rel	0.6
%define		pname	martian
Summary:	martian / linmodem package
Name:		%{pname}%{_alt_kernel}
Version:	20100123
Release:	%{rel}
# Code uses proprietary component distributed under Agere Systems license.
# Other components are protected either by GPL or LGPL. See package for more info.
License:	Agere Systems license (see ASWMLICENSE), GPL/LGPL (the rest)
Group:		Base/Kernel
#Source0:	http://www.barrelsoutofbond.org/downloads/martian/%{name}-full-%{version}.tar.gz
Source0:	http://linmodems.technion.ac.il/packages/ltmodem/kernel-2.6/martian/martian-full-%{version}.tar.gz
# Source0-md5:	17205efb777bb48fdf6b76210cf5f8f6
Source1:	http://linmodems.technion.ac.il/packages/ltmodem/kernel-2.6/martian/ltmdmobj.o-8.31-gcc4.gz
# Source1-md5:	14df61d5307f6960ff9de42567db4db9
URL:		http://martian.barrelsoutofbond.org/
BuildRequires:	bash
Provides:	martian_dev = %{release}
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2}
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
# x86_64 kernel module likely builds too, but userspace is 32bit only due pre-provided binary .o
ExclusiveArch:	%{ix86}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Martian is software to serve the Agere Systems PCI WinModem under
LINUX. These are modems built on DSP 164x (Mars) series. Project's
major objective is to pull the proprietary core out of the kernel.

%package -n kernel%{_alt_kernel}-misc-martian
Summary:	Martian / Linmodem driver
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires:	uname(release) >= 2.6.12
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif

# may not be stripped, see modem/tweakrelocsdynamic.c
%define		_noautostrip	.*/martian_modem

%description -n kernel%{_alt_kernel}-misc-martian
Linux Lucent/Agere Systems PCI WinModem driver.

%prep
%setup -q -n martian-full-%{version}
%{__gzip} -dc %{SOURCE1} > modem/ltmdmobj.o
touch -r %{SOURCE1} modem/ltmdmobj.o

%{__sed} -i -e 's#gcc -#$(CC) -#g' modem/Makefile

%build
%if %{with userspace}
%{__make} -C modem martian_modem \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -Wall" \
	MLDFLAGS="%{rpmldflags} -Wl,-q -lpthread -lrt" \
	SHELL=/bin/bash
%endif

%if %{with kernel}
%build_kernel_modules -m %{pname}_dev -C kmodule
%endif

%install
rm -rf $RPM_BUILD_ROOT
%if %{with userspace}
install -d $RPM_BUILD_ROOT{%{_sbindir},/etc/rc.d/init.d}
# install startup sccript
install -p scripts/%{pname} $RPM_BUILD_ROOT/etc/rc.d/init.d
# install the martian modem
install -p modem/martian_modem $RPM_BUILD_ROOT%{_sbindir}
%endif

%if %{with kernel}
%install_kernel_modules -m kmodule/%{pname}_dev -d misc
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-misc-martian
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-misc-martian
%depmod %{_kernel_ver}

%if %{with kernel}
%files -n kernel%{_alt_kernel}-misc-martian
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.ko*
%endif

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README INSTALL ChangeLog Concept
%doc Cleaning.txt sample.txt
%doc modem/ASWMLICENSE
%attr(754,root,root) /etc/rc.d/init.d/martian
%attr(755,root,root) %{_sbindir}/martian_modem
%endif
