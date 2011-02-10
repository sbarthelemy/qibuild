## Copyright (C) 2011 Aldebaran Robotics

clean(ICONV)
fpath(ICONV iconv.h)

#only windows need iconv, on other plateform it's provided by the libc
if(WIN32)
  flib(ICONV iconv)
  export_lib(ICONV)
else()
  export_header(ICONV)
endif()

