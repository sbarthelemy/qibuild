## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

find_package(PkgConfig)
pkg_check_modules(DBUS-1 dbus-1)
export_lib_pkgconfig(DBUS-1)
