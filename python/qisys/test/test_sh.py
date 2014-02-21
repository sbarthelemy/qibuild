## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import stat
import sys
import pytest

import qisys.sh
from qisrc.test.conftest import TestGit

def test_install_ro(tmpdir):
    tmp = tmpdir.strpath
    src = os.path.join(tmp, "src")
    os.mkdir(src)
    ro = os.path.join(src, "ro")
    with open(ro, "w") as fp:
        fp.write("ro\n")
    # 200:
    os.chmod(ro, stat.S_IRUSR)
    dest = os.path.join(tmp, "dest")
    qisys.sh.install(src, dest)

def test_install_on_self(tmpdir):
    a_file = tmpdir.join("a")
    a_file.write("")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        qisys.sh.install(a_file.strpath, tmpdir.strpath)
    assert "are the same file" in e.value.message
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        qisys.sh.install(tmpdir.strpath, tmpdir.strpath)
    assert "are the same directory" in e.value.message


def test_filter_hidden(tmpdir):
    src = tmpdir.ensure("src", dir=True)
    src.join("a_file").ensure(file=True)
    src.join(".hidden").ensure(file=True)
    dest = tmpdir.join("dest")
    def non_hidden(src):
        return not src.startswith(".")
    qisys.sh.install(src.strpath, dest.strpath, filter_fun=non_hidden)
    assert dest.join("a_file").check(file=True)
    assert not dest.join(".hidden").check(file=True)

def test_is_path_inside():
   assert qisys.sh.is_path_inside(os.path.join("foo", "bar"), "foo")
   assert qisys.sh.is_path_inside(os.path.join("foo", "bar"),
                                  os.path.join("foo", "bar"))
   assert qisys.sh.is_path_inside("foo", os.path.join("foo", "bar")) is False
   assert qisys.sh.is_path_inside(os.path.join("lib", "libfoobar"),
                                  os.path.join("lib", "libfoo")) is False
   assert qisys.sh.is_path_inside(os.path.join("gui", "bar", "libfoo"),
                                  "lib") is False

def test_copy_git_src(tmpdir):
    src = tmpdir.mkdir("src")
    dest = tmpdir.mkdir("dest")
    foo_src = src.mkdir("foo")
    foo_git = TestGit(foo_src.strpath)
    foo_git.initialize()
    foo_git.commit_file("a.txt", "a\n")
    foo_git.commit_file("b.txt", "a\n")
    foo_src.ensure("c.txt", file=True)
    qisys.sh.copy_git_src(foo_src.strpath, dest.strpath)
    assert dest.join("a.txt").check(file=True)
    assert not dest.join("c.txt").check(file=True)

def test_is_runtime():
    assert qisys.sh.is_runtime("lib/libfoo.a") is False
    assert qisys.sh.is_runtime("include/foo.h") is False
    assert qisys.sh.is_runtime("lib/python2.7/Makefile") is True
    assert qisys.sh.is_runtime("lib/python2.7/config/pyconfig.h") is True
    assert qisys.sh.is_runtime("include/python2.7/pyconfig.h") is True
    if sys.platform == "darwin":
        assert qisys.sh.is_runtime("lib/libfoo.dylib") is True
