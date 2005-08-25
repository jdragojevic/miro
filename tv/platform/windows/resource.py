import os, sys
import re

def appRoot():
    if hasattr(sys, "frozen"):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(sys.argv[0])

# Note: some of these functions are probably not absolutely correct in
# the face of funny characters in the input paths. In particular,
# url() doesn't DTRT when the path contains spaces. But they should be
# sufficient for resolving resources, since we have control over the
# filenames.

# Find the full path to a resource data file. 'relative_path' is
# expected to be supplied in Unix format, with forward-slashes as
# separators. The output, though, uses the native platform separator.
def path(relative_path):
    parts = re.split(r'/', relative_path)
    parts[0:0] = [appRoot(), 'resources']
    return os.path.join(*parts)

# As path(), but return a file: URL instead.
def url(relative_path):
    parts = re.split(r'/', relative_path)
    parts[0:0] = [appRoot(), 'resources']
    return "file:///" + '/'.join(parts)
