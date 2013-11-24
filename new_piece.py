import os
import sys

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "Usage: %s <new piece name>" % sys.argv[0]
    sys.exit(1)

  path = "pieces/%s.txt" % sys.argv[1]

  if os.path.isfile(path):
    print "%s already exists.  Exiting." % path
    sys.exit(1)

  # Open the file.
  open(path, "a")

  print "Done!  You have a new empty piece created."
