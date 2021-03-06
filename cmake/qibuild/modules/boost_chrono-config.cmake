## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
include("${_ROOT_DIR}/boostutils.cmake")
boost_flib("chrono")
set(_deps)
list(APPEND _deps BOOST_SYSTEM)
qi_persistent_set(BOOST_CHRONO_DEPENDS ${_deps})
