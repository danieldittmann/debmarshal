#!/usr/bin/perl -w
#
# distclean.pl {directory} {dist}
#
# Scan directory, deleting debian dists that do not have symlinks to them.
#
#
# Copyright 2010 Google Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Drake Diedrich <dld@google.com>

use Getopt::Long;
use Pod::Usage;


sub distclean($$$) {
  my ($repository,$dist,$options) = @_;

  if (! -d $repository) {
    return ["$repository/ does not exist", 2];
  }
  if (! -d "$repository/dists") {
    return ["$repository/dists/ does not exist", 2];
  }
  if (! -d "$repository/dists/$dist") {
    return ["$repository/dists/$dists does not exist",2];
  }

  [undef, 0];
}


# main()
#
# Parse options, print usage, and return with exit codes.
#
sub main {
  my %options;

  my $result = GetOptions(\%options,
             'help|?',
             'man')
    or pod2usage(2);

  pod2usage(1) if $options{'help'};
  pod2usage(-verbose => 2) if $options{'man'};

  if (@ARGV != 1) {
    pod2usage("$0: Repository directory required.\n");
  }

  my ($inputdir) = @ARGV;

  my ($rcmsg,$rc) = distclean($inputdir,"null", \%options);
  print STDERR $rcmsg;
  $rc;
}

if (!caller()) {
  main();
} else {
  return 1;
}
