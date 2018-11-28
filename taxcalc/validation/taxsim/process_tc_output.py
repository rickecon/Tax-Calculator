"""
Translates tc --dump output file into Internet-TAXSIM 9.3 output file.
"""
# CODING-STYLE CHECKS:
# pycodestyle process_tc_output.py
# pylint --disable=locally-disabled process_tc_output.py

import argparse
import os
import sys
import pandas as pd


def main():
    """
    High-level logic.
    """
    # parse command-line arguments:
    usage_str = 'python process_tc_output.py INPUT OUTPUT [--help]'
    parser = argparse.ArgumentParser(
        prog='',
        usage=usage_str,
        description=('Translates tc --dump output file into a TAXSIM22 '
                     '(Internet-TAXSIM 9.3) output file containing '
                     '28 variables.  The INPUT file contains the '
                     'output generated by running tc with the --dump option. '
                     'Any pre-existing OUTPUT file contents will be '
                     'overwritten.  For details on Internet-TAXSIM '
                     'version 9.3 OUTPUT format, go to '
                     'http://users.nber.org/~taxsim/taxsim-calc9/'))
    parser.add_argument('INPUT', nargs='?', default='',
                        help=('INPUT is name of file that contains '
                              'tc --dump output.'))
    parser.add_argument('OUTPUT', nargs='?', default='',
                        help=('OUTPUT is name of file that will contain '
                              'TAXSIM22 28-variable output.'))
    args = parser.parse_args()
    sname = 'process_tc_output.py'
    # check INPUT filename
    if args.INPUT == '':
        sys.stderr.write('ERROR: must specify INPUT file name\n')
        sys.stderr.write('USAGE: python {} --help\n'.format(sname))
        return 1
    if not os.path.isfile(args.INPUT):
        emsg = 'INPUT file named {} does not exist'.format(args.INPUT)
        sys.stderr.write('ERROR: {}\n'.format(emsg))
        return 1
    # check OUTPUT filename
    if args.OUTPUT == '':
        sys.stderr.write('ERROR: must specify OUTPUT file name\n')
        sys.stderr.write('USAGE: python {} --help\n'.format(sname))
        return 1
    if os.path.isfile(args.OUTPUT):
        os.remove(args.OUTPUT)
    # read INPUT file into a pandas DataFrame
    tcvar = pd.read_csv(args.INPUT)
    # write OUTPUT file using the pandas DataFrame
    write_taxsim_formatted_output(args.OUTPUT, tcvar)
    # return no-error exit code
    return 0
# end of main function code


def write_taxsim_formatted_output(filename, tcvar):
    """
    Write contents of tcvar pandas DataFrame to filename using
    Internet-TAXSIM 9.3 output format containing 28 variables.
    """
    assert isinstance(tcvar, pd.DataFrame)
    with open(filename, 'w') as output_file:
        for idx in range(0, len(tcvar.index)):
            odict4idx = extract_output(tcvar.xs(idx))
            outline = construct_output_line(odict4idx)
            output_file.write(outline)


def extract_output(out):
    """
    Extracts output for one filing unit in out and
    returns extracted output as a dictionary.

    Parameters
    ----------
    out: pandas DataFrame row containing tc --dump output for one filing unit

    Returns
    -------
    ovar: dictionary of output variables indexed from 1 to 28

    Notes
    -----
    The value of each output variable is stored in the ovar dictionary,
    which is indexed as Internet-TAXSIM output variables are (where the
    index begins with one).
    """
    ovar = {}
    ovar[1] = int(out['RECID'])  # id for tax filing unit
    ovar[2] = int(out['FLPDYR'])  # year taxes are calculated
    ovar[3] = 0  # state code is always zero
    ovar[4] = out['iitax']  # federal income tax liability
    ovar[5] = 0.0  # no state income tax calculation
    ovar[6] = out['payrolltax']  # ee+er for OASDI+HI
    ovar[7] = 0.0  # marginal federal income tax rate as percent
    ovar[8] = 0.0  # no state income tax calculation
    ovar[9] = 0.0  # marginal payroll tax rate as percent
    ovar[10] = out['c00100']  # federal AGI
    ovar[11] = out['e02300']  # UI benefits in AGI
    ovar[12] = out['c02500']  # OASDI benefits in AGI
    ovar[13] = 0.0  # always set zero-bracket amount to zero
    pre_phase_out_pe = out['pre_c04600']
    post_phase_out_pe = out['c04600']
    phased_out_pe = pre_phase_out_pe - post_phase_out_pe
    ovar[14] = post_phase_out_pe  # post-phase-out personal exemption
    ovar[15] = phased_out_pe  # personal exemption that is phased out
    # ovar[16] can be positive for non-itemizer:
    ovar[16] = out['c21040']  # phased out itemized deduction
    # ovar[17] is zero for non-itemizer:
    ovar[17] = out['c04470']  # post-phase-out item deduction
    ovar[18] = out['c04800']  # federal regular taxable income
    # ovar[19] is regular tax on taxable income
    ovar[19] = out['taxbc']
    ovar[20] = 0.0  # always set exemption surtax to zero
    ovar[21] = 0.0  # always set general tax credit to zero
    ovar[22] = out['c07220']  # child tax credit (adjusted)
    ovar[23] = out['c11070']  # extra refunded child tax credit
    ovar[24] = out['c07180']  # child care credit
    ovar[25] = out['eitc']  # federal EITC
    ovar[26] = out['c62100']  # federal AMT taxable income
    amt_liability = out['c09600']  # federal AMT liability
    ovar[27] = amt_liability
    # ovar[28] is federal income tax before credits; the Tax-Calculator
    # out['c05800'] is this concept but includes AMT liability
    # while Internet-TAXSIM ovar[28] explicitly excludes AMT liability, so
    # we have the following:
    ovar[28] = out['c05800'] - amt_liability
    return ovar


OVAR_FMT = {1: '{:d}.',  # add decimal point as in Internet-TAXSIM output
            2: ' {:d}',
            3: ' {:d}',
            4: ' {:.2f}',
            5: ' {:.2f}',
            6: ' {:.2f}',
            7: ' {:.2f}',
            8: ' {:.2f}',
            9: ' {:.2f}',
            10: ' {:.2f}',
            11: ' {:.2f}',
            12: ' {:.2f}',
            13: ' {:.2f}',
            14: ' {:.2f}',
            15: ' {:.2f}',
            16: ' {:.2f}',
            17: ' {:.2f}',
            18: ' {:.2f}',
            19: ' {:.2f}',
            20: ' {:.2f}',
            21: ' {:.2f}',
            22: ' {:.2f}',
            23: ' {:.2f}',
            24: ' {:.2f}',
            25: ' {:.2f}',
            26: ' {:.2f}',
            27: ' {:.2f}',
            28: ' {:.2f}'}


def construct_output_line(odict):
    """
    Construct an output line from a single-filing-unit odict dictionary.

    Parameters
    ----------
    odict: dictionary of output variables indexed from 1 to len(odict).

    Returns
    -------
    output_line: string

    """
    outline = ''
    for vnum in range(1, len(odict) + 1):
        outline += OVAR_FMT[vnum].format(odict[vnum])
    outline += '\n'
    return outline


if __name__ == '__main__':
    sys.exit(main())
