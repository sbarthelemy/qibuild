##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010 Aldebaran Robotics
##

import os
import sys
import logging
import qibuild.sh
import qibuild.build
from   qibuild.toc.toc import Toc

LOGGER = logging.getLogger("qibuild.tocbuilder")

class TocBuilder(Toc):
    def __init__(self, work_tree, build_type, toolchain_name, build_config, cmake_flags):
        """
            work_tree      = a toc worktree
            build_type     = a build type, could be debug or release
            toolchain_name = by default the system toolchain is used
            cmake_flags    = optional additional cmake flags
            build_config   = optional a build configuration
        """
        Toc.__init__(self, work_tree)
        self.build_type        = build_type
        self.toolchain_name    = toolchain_name
        self.build_config      = build_config
        self.cmake_flags       = cmake_flags
        self.build_folder_name = None

        self._set_build_folder_name()

        if not self.build_config:
            self.build_config = self.configstore.get("general", "build", "config", default=None)

        for p in self.buildable_projects.values():
            self._update_project_build_config(p)

    def _update_project_build_config(self, project):
        """Set the build configurations of the dependencies
        of the projects.
        """
        project.build_config.update(self, project, self.build_folder_name)
        LOGGER.debug("[%s] build configuration\n%s", project.name, project.build_config)

    def _set_build_folder_name(self):
        """Get a reasonable build folder.
        The point is to be sure we don't have two incompatible build configurations
        using the same build dir.

        Return a string looking like
        build-linux-release
        build-cross-debug ...
        """
        res = ["build"]
        if self.toolchain_name:
            res.append(self.toolchain_name)
        if not sys.platform.startswith("win32") and self.build_type:
            # On windows, sharing the same build dir for debug and release is OK.
            # (and quite mandatory when using CMake + Visual studio)
            # On linux, it's not.
            res.append(tob.build_type)
        if self.build_config:
            res.append(self.build_config)
        self.build_folder_name = "-".join(res)

    def get_sdk_dirs(self, project):
        """ return a list of sdk, needed to build a project """
        dirs = list()

        projects = self.resolve_deps(project)
        projects.remove(project)

        for project in projects:
            if project in self.buildable_projects.keys():
                dirs.append(self.get_project(project).get_sdk_dir())
            else:
                LOGGER.warning("dependency not found: %s", project)
        return dirs





def get_qibuild_cmake_framework_path():
    """ return the path to the QiBuild Cmake framework """
    return os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "cmake"))

def bootstrap_project(project, dep_sdk_dirs):
    """Generate the find_deps.cmake for the given project
    """
    build_dir = project.build_config.build_directory

    to_write  = "#############################################\n"
    to_write += "#QIBUILD AUTOGENERATED FILE. DO NOT EDIT.\n"
    to_write += "#############################################\n"
    to_write += "\n"
    to_write += "#QIBUILD CMAKE FRAMEWORK PATH:\n"
    to_write += "set(CMAKE_MODULE_PATH \"%s\")\n" % get_qibuild_cmake_framework_path()
    to_write += "\n"
    to_write += "#DEPENDENCIES:\n"
    for dep_sdk_dir in dep_sdk_dirs:
        to_write += "list(APPEND CMAKE_PREFIX_PATH \"%s\")\n" % qibuild.sh.to_posix_path(dep_sdk_dir)

    output_path = os.path.join(build_dir, "dependencies.cmake")
    with open(output_path, "w") as output_file:
        output_file.write(to_write)

    LOGGER.debug("Wrote to %s:\n%s", output_path, to_write)


def configure_project(project, flags=None, toolchain_file=None, generator=None):
    """ Call cmake with correct options
    if toolchain_file is None a t001chain file is generated in the cmake binary directory.
    if toolchain_file is "", then CMAKE_TOOLCHAIN_FILE is not specified.
    """

    #TODO: guess generator

    if not os.path.exists(project.directory):
        raise ConfigureException("source dir: %s does not exist, aborting" % project.directory)

    if not os.path.exists(os.path.join(project.directory, "CMakeLists.txt")):
        LOGGER.info("Not calling cmake for %s", os.path.basename(project.directory))
        return

    # Set generator (mandatory on windows, because cmake does not
    # autodetect visual studio compilers very well)
    cmake_args = []
    if generator:
        cmake_args.extend(["-G", generator])

    # Make a copy so that we do not modify
    # the list used by the called
    if flags:
        cmake_flags = flags[:]
    else:
        cmake_flags = list()
    cmake_flags.extend(project.build_config.cmake_flags)

    if toolchain_file:
        cmake_flags.append("CMAKE_TOOLCHAIN_FILE=" + toolchain_file)

    cmake_args.extend(["-D" + x for x in cmake_flags])

    qibuild.build.cmake(project.directory, project.build_config.build_directory, cmake_args)


def make_project(project, build_type, num_jobs=1, nmake=False, target=None):
    """Build the project"""
    build_dir = project.build_config.build_directory
    LOGGER.debug("[%s]: building in %s", project.name, build_dir)
    if sys.platform.startswith("win32") and not nmake:
        sln_files = glob.glob(build_dir + "/*.sln")
        if len(sln_files) == 0:
            LOGGER.debug("Not calling msbuild for %s", os.path.basename(build_dir))
            return

        if len(sln_files) != 1:
            err_message = "Found several sln files: "
            err_message += ", ".join(sln_files)
            raise MakeException(err_message)
        sln_file = sln_files[0]
        qibuild.build.build_vc(sln_file, build_type=build_type, target=target)
    else:
        if not os.path.exists(os.path.join(build_dir, "Makefile")):
            LOGGER.debug("Not calling make for %s", os.path.basename(build_dir))
            return
        if sys.platform.startswith("win32"):
            qibuild.build.build_nmake(build_dir, target=target)
        else:
            qibuild.build.build_unix(build_dir, num_jobs=num_jobs, target=target)
