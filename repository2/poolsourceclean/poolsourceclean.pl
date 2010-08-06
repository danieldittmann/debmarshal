#!/usr/bin/perl -w
#
# poolsourceclean.pl {directory} {dist}
#
# Scan pool and dist directories and snapshots.
# Delete any source that is not in a dist.
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
use FileHandle;
use File::Path qw(make_path remove_tree);
use strict;

#
# Return a list of files of all the Sources files
#
sub sources_files($);
sub sources_files($) {
  my ($dir) = @_;
  my (@sources);
  my $dh = new DirHandle $dir;
  while (my $de = $dh->read) {
    next if ($de eq '.' || $de eq '..');
    my $path = "$dir/$de";
    if (-d $path) {
      push @sources, sources_files($path);
    } elsif (-f $path) {
      if ($de eq 'Sources') {
	push(@sources,$path);
      }
    }
  }
  @sources;
}

#
# Parse an open filehandle that is a Sources file for the complete
# list of source files that are indexed in a repository.
#
sub parse_sources($$) {
  my ($fh,$sources) = @_;
  my ($directory);
  while (my $line = $fh->getline) {
    if ($line =~ /^Directory: (\S+)\s*$/) {
      $directory = $1;
    } elsif ($line =~ /^ [0-9a-f]+ \d+ (\S+)\s*$/) {
      $sources->{"$directory/$1"}++;
    } elsif ($line =~ /^$/) {
      $directory = undef;
    }
  }
}


sub purge_source_pool($$$$);
sub purge_source_pool($$$$) {
  my ($dir,$path,$sources,$unlink) = @_;
  my $dh = new DirHandle $dir;
  while (my $de = $dh->read) {
    my $fullpath = "$dir/$de";
    next if $de eq '.' || $de eq '..';
    if (-d $fullpath) {
      purge_source_pool("$dir/$de","$path/$de",$sources,$unlink);
    } elsif (-f $fullpath) {
      if ($de =~ /\.(dsc|tar\.gz|diff\.gz)$/) {
	if (!defined $sources->{"$path/$de"}) {
	  &{$unlink}($fullpath);
	}
      }
    }
  }
}

sub poolsourceclean($) {
  my ($repository) = @_;
  my (%sources);

  if (! -d $repository) {
    return ["$repository/ does not exist", 2];
  }
  if (! -d "$repository/dists") {
    return ["$repository/dists/ does not exist", 2];
  }
  if (! -d "$repository/pool") {
    return ["$repository/pool/ does not exist",2];
  }

  my (@sources) = sources_files("$repository/dists");
  foreach my $source (@sources) {
    my $sourcefh = new FileHandle $source;
    parse_sources($sourcefh,\%sources);
  }

  purge_source_pool("$repository/pool", "pool", \%sources, sub {unlink @_;} );

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

  

  my ($rcmsg,$rc) = @{poolsourceclean($inputdir)};

  print STDERR $rcmsg if defined $rcmsg;
  $rc;
}

if (!caller()) {
  main();
} else {
  return 1;
}


__END__

=head1 NAME

debmarshal_pooldebclean - remove unused .deb pool files from a repository


=head1 SYNOPSIS

debmarshal_pooldebclean {repository directory}

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

B<debmarshal_poolsourceclean> will delete all the unused source in a repository
pool, including debmarshal snapshot and regular Debian repositories.

=cut
