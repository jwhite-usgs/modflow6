# Get executables and build targets
# can compile mf6 direcetly using this command:
#  python -c "import test000_setup; test000_setup.test_build_modflow6()"

import os
import sys
import shutil
import pymake

from framework import running_on_CI

if running_on_CI():
    print('running on CI environment')
    os.environ['PYMAKE_DOUBLE'] = '1'

# paths to executables for  previous versions of MODFLOW
ebindir = os.path.abspath(
    os.path.join(os.path.expanduser('~'), '.local', 'bin'))
if not os.path.exists(ebindir):
    os.makedirs(ebindir)

# make sure exe extension is used on windows
eext = ''
soext = '.so'
if sys.platform.lower() == 'win32':
    eext = '.exe'
    soext = '.dll'

download_version = '3.0'
mfexe_pth = 'temp/mfexes'


def relpath_fallback(pth):
    try:
        # throws ValueError on Windows if pth is on a different drive
        return os.path.relpath(pth)
    except ValueError:
        return os.path.abspath(pth)


def create_dir(pth):
    # remove pth directory if it exists
    if os.path.exists(pth):
        print('removing... {}'.format(os.path.abspath(pth)))
        shutil.rmtree(pth)
    # create pth directory
    print('creating... {}'.format(os.path.abspath(pth)))
    os.makedirs(pth)

    msg = 'could not create... {}'.format(os.path.abspath(pth))
    assert os.path.exists(pth), msg

    return


def test_create_dirs():
    pths = [os.path.join('..', 'bin'),
            os.path.join('temp')]

    for pth in pths:
        create_dir(pth)

    return


def test_getmfexes():
    pymake.getmfexes(mfexe_pth)
    for target in os.listdir(mfexe_pth):
        srcpth = os.path.join(mfexe_pth, target)
        if os.path.isfile(srcpth):
            dstpth = os.path.join(ebindir, target)
            print('copying {} -> {}'.format(srcpth, dstpth))
            shutil.copy(srcpth, dstpth)
    return


def test_build_modflow6():
    # determine if app should be built
    for idx, arg in enumerate(sys.argv):
        if arg.lower() == '--nomf6':
            txt = 'Command line cancel of MODFLOW 6 build'
            print(txt)
            return

    # set source and target paths
    srcdir = os.path.join('..', 'src')
    target = os.path.join('..', 'bin', 'mf6')
    target += eext
    fc, cc = pymake.set_compiler('mf6')

    fflags = None
    if fc == 'gfortran':
        # some flags to check for errors in the code
        # add -Werror for compilation to terminate if errors are found
        fflags = ('-Wtabs -Wline-truncation -Wunused-label '
                  '-Wunused-variable -pedantic -std=f2008')

    pymake.main(srcdir, target, fc=fc, cc=cc, include_subdirs=True,
                fflags=fflags)

    msg = '{} does not exist.'.format(relpath_fallback(target))
    assert os.path.isfile(target), msg


def test_build_modflow6_so():
    # determine if app should be built
    for idx, arg in enumerate(sys.argv):
        if arg.lower() == '--nomf6':
            txt = 'Command line cancel of MODFLOW 6 build'
            print(txt)
            return

    # set source and target paths
    srcdir = os.path.join('..', 'srcbmi')
    comdir = os.path.join('..', 'src')
    excludefiles = [os.path.join(comdir, 'mf6.f90')]
    target = os.path.join('..', 'bin', 'libmf6')
    target += soext
    fc, cc = pymake.set_compiler('mf6')

    fflags = None
    if fc == 'gfortran':
        # some flags to check for errors in the code
        # add -Werror for compilation to terminate if errors are found
        fflags = ('-Wtabs -Wline-truncation -Wunused-label '
                  '-Wunused-variable -pedantic -std=f2008')

    pymake.main(srcdir, target, fc=fc, cc=cc, include_subdirs=True,
                fflags=fflags, srcdir2=comdir, excludefiles=excludefiles,
                sharedobject=True)

    msg = '{} does not exist.'.format(relpath_fallback(target))
    assert os.path.isfile(target), msg


def test_build_mf5to6():
    # determine if app should be built
    for idx, arg in enumerate(sys.argv):
        if arg.lower() == '--nomf5to6':
            txt = 'Command line cancel of MODFLOW 5 to 6 converter build'
            print(txt)
            return

    # set source and target paths
    srcdir = os.path.join('..', 'utils', 'mf5to6', 'src')
    target = os.path.join('..', 'bin', 'mf5to6')
    target += eext
    extrafiles = os.path.join('..', 'utils', 'mf5to6', 'pymake',
                              'extrafiles.txt')
    fc, cc = pymake.set_compiler('mf6')

    # build modflow 5 to 6 converter
    pymake.main(srcdir, target, fc=fc, cc=cc, include_subdirs=True,
                extrafiles=extrafiles)

    msg = '{} does not exist.'.format(relpath_fallback(target))
    assert os.path.isfile(target), msg


def test_build_zonebudget():
    # determine if app should be built
    for idx, arg in enumerate(sys.argv):
        if arg.lower() == '--nozonebudget':
            txt = 'Command line cancel of ZONEBUDGET for MODFLOW 6 build'
            print(txt)
            return

    # set source and target paths
    srcdir = os.path.join('..', 'utils', 'zonebudget', 'src')
    target = os.path.join('..', 'bin', 'zbud6')
    target += eext
    extrafiles = os.path.join('..', 'utils', 'zonebudget', 'pymake',
                              'extrafiles.txt')
    fc, cc = pymake.set_compiler('mf6')

    fflags = None
    if fc == 'gfortran':
        # some flags to check for errors in the code
        # add -Werror for compilation to terminate if errors are found
        fflags = ('-Wtabs -Wline-truncation -Wunused-label '
                  '-Wunused-variable -pedantic -std=f2008')

    pymake.main(srcdir, target, fc=fc, cc=cc, extrafiles=extrafiles,
                fflags=fflags)

    msg = '{} does not exist.'.format(relpath_fallback(target))
    assert os.path.isfile(target), msg


if __name__ == "__main__":
    test_create_dirs()
    test_getmfexes()
    test_build_modflow6()
    test_build_modflow6_so()
    test_build_mf5to6()
    test_build_zonebudget()
