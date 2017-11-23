# Copyright 2015-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3
#
# The term "product" means a real product (e.g LibreOffice 4.0) or anything
# that should be developed as a whole: it may have one or more modules
# (compontents). Another example at this commit: the DEWI itself, it can be
# described as product which have one module.
#
# The terms used by DEWI are similar to Eclipse and IntelliJ Idea, check it:
# https://www.jetbrains.com/idea/help/intellij-idea-vs-eclipse-terminology.html
#
# The term "workspace" is from Eclipse, it may have one or more projects and additional
# files, including a "data" defining product lists and modules and everyithing.
# The term "project" and "module" is the same as in IntelliJ Idea: each project has its
# own source, build and install directories, and modules may share the install directory.
#
# Each module has its own "builder" (e.g. autotools), what is used for bootstrapping,
# running tests, and so on. This is "Module SDK" at IntelliJ Idea because that software
# supports only Java (by default).
#
# Each module describes its dependencies - which can be either system packages on Ubuntu,
# Debian, or anything else, or another module.
#
# The current package (dewi.workspace) describes these.
