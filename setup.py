#!/usr/bin/env python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2013 <Zane Swafford> <zane@zaneswafford.com>
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
### END LICENSE

###################### DO NOT TOUCH THIS (HEAD TO THE SECOND PART) ######################

import os
import sys

try:
    import DistUtilsExtra.auto
except ImportError:
    print >> sys.stderr, 'To build spindl you need https://launchpad.net/python-distutils-extra'
    sys.exit(1)
assert DistUtilsExtra.auto.__version__ >= '2.18', 'needs DistUtilsExtra.auto >= 2.18'

def update_config(libdir, values = {}):

    filename = os.path.join(libdir, 'spindl_lib/spindlconfig.py')
    oldvalues = {}
    try:
        fin = file(filename, 'r')
        fout = file(filename + '.new', 'w')

        for line in fin:
            fields = line.split(' = ') # Separate variable from value
            if fields[0] in values:
                oldvalues[fields[0]] = fields[1].strip()
                line = "%s = %s\n" % (fields[0], values[fields[0]])
            fout.write(line)

        fout.flush()
        fout.close()
        fin.close()
        os.rename(fout.name, fin.name)
    except (OSError, IOError), e:
        print ("ERROR: Can't find %s" % filename)
        sys.exit(1)
    return oldvalues


def move_desktop_file(root, target_data, prefix):
    # The desktop file is rightly installed into install_data.  But it should
    # always really be installed into prefix, because while we can install
    # normal data files anywhere we want, the desktop file needs to exist in
    # the main system to be found.  Only actually useful for /opt installs.

    old_desktop_path = os.path.normpath(root + target_data +
                                        '/share/applications')
    old_desktop_file = old_desktop_path + '/spindl.desktop'
    desktop_path = os.path.normpath(root + prefix + '/share/applications')
    desktop_file = desktop_path + '/spindl.desktop'

    if not os.path.exists(old_desktop_file):
        print ("ERROR: Can't find", old_desktop_file)
        sys.exit(1)
    elif target_data != prefix + '/':
        # This is an /opt install, so rename desktop file to use extras-
        desktop_file = desktop_path + '/extras-spindl.desktop'
        try:
            os.makedirs(desktop_path)
            os.rename(old_desktop_file, desktop_file)
            os.rmdir(old_desktop_path)
        except OSError as e:
            print ("ERROR: Can't rename", old_desktop_file, ":", e)
            sys.exit(1)

    return desktop_file

def update_desktop_file(filename, target_pkgdata, target_scripts):

    try:
        fin = file(filename, 'r')
        fout = file(filename + '.new', 'w')

        for line in fin:
            if 'Icon=' in line:
                line = "Icon=%s\n" % (target_pkgdata + 'media/spindl.svg')
            elif 'Exec=' in line:
                cmd = line.split("=")[1].split(None, 1)
                line = "Exec=%s" % (target_scripts + 'spindl')
                if len(cmd) > 1:
                    line += " %s" % cmd[1].strip()  # Add script arguments back
                line += "\n"
            fout.write(line)
        fout.flush()
        fout.close()
        fin.close()
        os.rename(fout.name, fin.name)
    except (OSError, IOError), e:
        print ("ERROR: Can't find %s" % filename)
        sys.exit(1)

def compile_schemas(root, target_data):
    if target_data == '/usr/':
        return  # /usr paths don't need this, they will be handled by dpkg
    schemadir = os.path.normpath(root + target_data + 'share/glib-2.0/schemas')
    if (os.path.isdir(schemadir) and
            os.path.isfile('/usr/bin/glib-compile-schemas')):
        os.system('/usr/bin/glib-compile-schemas "%s"' % schemadir)


class InstallAndUpdateDataDirectory(DistUtilsExtra.auto.install_auto):
    def run(self):
        DistUtilsExtra.auto.install_auto.run(self)

        target_data = '/' + os.path.relpath(self.install_data, self.root) + '/'
        target_pkgdata = target_data + 'share/spindl/'
        target_scripts = '/' + os.path.relpath(self.install_scripts, self.root) + '/'

        values = {'__spindl_data_directory__': "'%s'" % (target_pkgdata),
                  '__version__': "'%s'" % self.distribution.get_version()}
        update_config(self.install_lib, values)

        desktop_file = move_desktop_file(self.root, target_data, self.prefix)
        update_desktop_file(desktop_file, target_pkgdata, target_scripts)
        compile_schemas(self.root, target_data)

        
##################################################################################
###################### YOU SHOULD MODIFY ONLY WHAT IS BELOW ######################
##################################################################################

DistUtilsExtra.auto.setup(
    name='spindl',
    version='1.00',
    license='Apache-2.0',
    author='Zane Swafford',
    author_email='zane@zaneswafford.com',
    description='Track your time and get things done.',
    long_description='Spindl is a simple way to track how much time you spend throughout the day. See trends, analyse your time, and get things done with Spindl.',
    url='http://www.zaneswafford.com/spindl',
    cmdclass={'install': InstallAndUpdateDataDirectory}
    )

