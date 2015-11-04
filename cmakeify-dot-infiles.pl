#!/usr/bin/perl
#
# Script for generating CMake *.h.in files for CODA.
#
# Usage: ./cmakeify-dot-infiles <infile> <outfile>
#
# (Typical example: ./cmakeify-dot-infiles config.h.in config.h.cmake.in)
#
# This script:
# + Changes #define lines to #cmakedefine lines
# + Is a modified version of the CLS perl code for cmakeifying brathll.
#

use strict;
use warnings;
use File::Basename;

sub CopyFile($$)
{
    local $_;
    my ($Source, $Dest)	= @_;
    my $Model;

    $Model	= substr($Source, -3, 3) eq '.in';

    open SRC, "<", $Source or die "Problem opening ".$Source.":  $!\n";
    open DST, ">", $Dest   or die "Problem creating $Dest: $!\n";
    if ($Model)
    {
        my $generatorfile = basename($0);
        my $sourcefile = basename($Source);
        print DST "/* Generated by $generatorfile from $sourcefile. */\n"
    }
    my $SourceBase	= basename($Source);
  SOURCE_LINE:
    while (<SRC>)
    {
        if ($Model)
        {
            if (($SourceBase eq "config.h.in") &&
                m@#endif /\* !defined\(CODA_CONFIG_H\) \*/@)
            {
                $_ = <<'EOF' . $_;

/* This is the relative path to CODA definitions for the IDL interface. */	
#cmakedefine CODA_DEFINITION_IDL ${CODA_DEFINITION_IDL}

/* This is the relative path to CODA definitions for the MATLAB interface. */	
#cmakedefine CODA_DEFINITION_MATLAB ${CODA_DEFINITION_MATLAB}

#ifdef WIN32
/* include windows specific headers */
#include <windows.h>
#include <io.h>
#include <direct.h>

/* include sys/stat.h because we are going to override stat */
#include <sys/stat.h>

/* we need to redefine ELEMENT_TYPE because it conflicts with io.h contents */
#define ELEMENT_TYPE ELEMENT_TYPE_RENAMED
#define XML_NS 1
#define XML_DTD 1
#define XML_LARGE_SIZE 1
#define XML_CONTEXT_BYTES 1024
#define XML_BUILDING_EXPAT 1

/* redefines for special string handling functions */
#define strcasecmp _stricmp
#define strncasecmp _strnicmp
#define snprintf _snprintf
#if defined(_MSC_VER) && _MSC_VER < 1500
#define vsnprintf _vsnprintf
#endif

/* redefines for file handling functions */
#define open(arg1,arg2) _open(arg1,arg2)
#define close(arg1) _close(arg1)
#define read(arg1,arg2,arg3) _read(arg1,arg2,arg3)
#define lseek(arg1,arg2,arg3) _lseeki64(arg1,arg2,arg3)
#define off_t __int64
#define stat _stati64
#define S_IFREG _S_IFREG

#define YYMALLOC malloc
#define YYFREE free

/* coda-idl defines */

#ifndef CODA_DEFINITION_IDL
#define CODA_DEFINITION_IDL "../definitions"
#endif

#ifdef IDL_V5_3
#define HAVE_IDL_SYSFUN_DEF2 1
#endif

#ifdef IDL_V5_4
#define HAVE_IDL_SYSFUN_DEF2 1
#define HAVE_IDL_SYSRTN_UNION 1
#endif

/* coda-matlab defines */

#ifndef CODA_DEFINITION_MATLAB
#define CODA_DEFINITION_MATLAB "../definitions"
#endif

#if defined(MATLAB_R11) || defined(MATLAB_R12)
#define mxCreateDoubleScalar replacement_mxCreateDoubleScalar
#else
#define HAVE_MXCREATEDOUBLESCALAR 1
#endif

#ifdef MATLAB_R11
#define mxCreateNumericMatrix replacement_mxCreateNumericMatrix
#else
#define HAVE_MXCREATENUMERICMATRIX 1
#endif
#endif

EOF
                next SOURCE_LINE;
            }


            if (m/^(\s*)(#undef)\s+(\w+)/)
            {
                $_	= "$1#cmakedefine $3 ".'$'."{$3}$'";

                # Move comment of end of line to preceding line
                s/^(.*)(\/\*.*\*\/)/$2\n$1$'/;
                
                if (m/define.*HAVE_ALLOCA_H/)
                {
                    $_	.= <<'EOF'

/* Automatically added by "cmakeify-dot-infiles" conversion script */
/* Needed for windows. */
#cmakedefine HAVE_MALLOC_H ${HAVE_MALLOC_H}
#ifdef HAVE_MALLOC_H
#include <malloc.h>
#endif

EOF
                }
            }
        }
    }
    continue
    {
        print DST	or die "Problem writing into $Dest: $!\n";
    }
    close SRC;
    close DST
    or die "Problem closing $Dest: $!\n";
}

# main:

$main::infile = undef;
$main::outfile = undef;

args_init(\@ARGV);


# args:
#   1) - ref to @ARGV
# return:
#   undef
# purpose:
#   parse command line.
# effect:
#   modifies @ARGV
sub args_init {

    my( $args ) = @_;

    @$args < 2
    && usage( "Too few args." );

    $main::outfile = pop( @$args );
    $main::infile = pop( @$args );

    (-f $main::infile)
    || usage( "$main::infile: Must be an existing file." );

    CopyFile($main::infile, $main::outfile);
}


sub usage {
    my( $msg ) = @_;
    print "
Usage: $0 <infile> <outfile>
";

    $msg && print "$msg\n\n";
    exit 1;
}
