## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
include_directories(".")

add_library(bar
  bar/bar.hpp
  bar/bar.cpp)

install(TARGETS bar
  RUNTIME DESTINATION "lib"
  ARCHIVE DESTINATION "lib"
  LIBRARY DESTINATION "lib")

install(FILES bar/bar.h
  DESTINATION "include/bar")
