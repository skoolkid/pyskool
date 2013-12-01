%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

Name:           pyskool
Version:        1.1
Release:        1%{?dist}
Summary:        Remake of Skool Daze and Back to Skool in Python and Pygame

License:        GPLv3+
URL:            http://pyskool.ca/
Source0:        http://pyskool.ca/downloads/%{name}/%{name}-%{version}.tar.xz

BuildArch:      noarch
BuildRequires:  python-devel
Requires:       pygame

%description
Pyskool is a re-implementation of the classic ZX Spectrum games, Skool Daze
and Back to Skool, in Python and Pygame. Pyskool aims to make the games easy
to customise by editing plain-text configuration files or - for more advanced
customisation - writing some Python code. In addition to Skool Daze and Back
to Skool, Pyskool includes three new 'mods': Skool Daze Take Too, Ezad Looks,
and Back to Skool Daze.

%prep
%setup -q

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
# --prefix=... is needed on openSUSE, but not Fedora
%{__python} setup.py install -O1 --prefix=%{_prefix} --skip-build --root $RPM_BUILD_ROOT
install -d %{buildroot}%{_mandir}/man6
cp -p man/man6/*.6 %{buildroot}%{_mandir}/man6
install -d %{buildroot}%{_datadir}/%{name}
cp -a images.ini pyskool.ini icon.png ini images sounds %{buildroot}%{_datadir}/%{name}

%files
%doc COPYING docs/*
%{_bindir}/*
%{_mandir}/man6/*
%{_datadir}/%{name}/*
%{python_sitelib}/*

%changelog
* Sun Dec  1 2013 Richard Dymond <rjdymond@gmail.com> 1.1-1
- Updated to 1.1

* Fri Dec  7 2012 Richard Dymond <rjdymond@gmail.com> 1.0.1-1
- Updated to 1.0.1

* Mon Dec  3 2012 Richard Dymond <rjdymond@gmail.com> 1.0-1
- Initial RPM release
