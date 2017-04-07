In this directory are scripts to download and set up all of the supporting
libraries that will be benchmarked against.

If you would like to add a new library for benchmarking:

 * Add a <library>_install.sh script that builds the library and installs it to
   this directory (i.e. ./bin, ./lib, etc.).
 * Add the package name and URL to package-urls.txt.
 * Add the install script to install_all.sh

If you would like to update the version of a library used for benchmarking:

 * Update the corresponding URL in package-urls.txt.
