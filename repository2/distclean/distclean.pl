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
use DirHandle;
use File::Path qw(make_path remove_tree);

sub distclean($$$) {
  my ($repository,$dist,$options) = @_;

  if (! -d $repository) {
    return ["$repository/ does not exist", 2];
  }
  if (! -d "$repository/dists") {
    return ["$repository/dists/ does not exist", 2];
  }
  if (! -d "$repository/dists/$dist") {
    return ["$repository/dists/$dist/ does not exist",2];
  }

  my $d = new DirHandle "$repository/dists/$dist";
  if (! defined $d) {
    return ["Could not open $repository/dists/$dist/", 2];
  }

  my $direntry;
  my (%directory,%symlink);
  while (defined($direntry = $d->read)) {
    if (-l "$repository/dists/$dist/$direntry") {
      my $link = readlink "$repository/dists/$dist/$direntry";
      $symlink{$link}++;
    } elsif (-d "$repository/dists/$dist/$direntry" && $direntry =~ /^\d+$/) {
      $directory{$direntry}++;
    }
  }

  foreach my $snapshot (keys %directory) {
    if (! defined $symlink{$snapshot}) {
      remove_tree("$repository/dists/$dist/$snapshot");
    }
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

  if (@ARGV != 2) {
    pod2usage("$0: Repository directory and dist required.\n");
  }

  my ($inputdir,$dist) = @ARGV;

  my ($rcmsg,$rc) = @{distclean($inputdir, $dist, \%options)};
  print STDERR $rcmsg;
  $rc;
}

if (!caller()) {
  main();
} else {
  return 1;
}


__END__

=head1 NAME

debmarshal_distclean - Remove unused debmarshal snapshots from a repository
                       distribution

=head1 SYNOPSIS

debmarshal_distclean {repository directory} {dist}

 Options:
   -help            brief help message
   -man             full documentation

=head1 OPTIONS

=over 8

=item B<-help>

Print a brief help message and exits.

=item B<-man>

Prints the manual page and exits.

=back

=head1 DESCRIPTION

B<debmarshal_distclean> will delete all the numbered distributions in
{repository-dir}/dists/{dist}/, deleting any that have no symlinks to
them.  This is used to clean up unused snapshots in a repository
mirror.  If you have large enough diskspace, you don't have to, and may not want to, clean up ever.

=cut
