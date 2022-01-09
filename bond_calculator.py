'''

@project       : Queens College CSCI 365/765 Computational Finance
@Instructor    : Dr. Alex Pang

@Group Name    : Rocket
@Student Name  : Mohammed Chowdhury , Kyle Coleman , Tamzid Chowdhury

@Date          : Fall 2021

A Bond Calculator Class
'''

import math
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
from bisection_method import bisection

import enum
import calendar

from datetime import date

from bond import Bond, DayCount, PaymentFrequency

def get_actual360_daycount_frac(start, end):
    day_in_year = 360
    day_count = (end - start).days
    return(day_count / day_in_year)

def get_30360_daycount_frac(start, end):
    day_in_year = 360
    day_count = 360*(end.year - start.year) + 30*(end.month - start.month - 1) + \
                max(0, 30 - start.day) + min(30, end.day)
    return(day_count / day_in_year )


''' Mohammed
this method, and day-count in general, is a standard method for calculating the number of days between two dates.
actual days between the start date and end date in the numerator / actual days in that year
'''
def get_actualactual_daycount_frac(start, end):


    end_of_year = date(start.year, 12, 31)
    beginning_of_year = date( start.year, 1, 1)

    # TODO
    # result = ...
    # end TODO
    end_of_year = date(start.year, 12, 31)
    beginning_of_year = date(start.year, 1, 1)
    days_in_the_year = (end_of_year - beginning_of_year).days + 1

    num_days_btwn_strt_n_end = (end-start).days
    result = num_days_btwn_strt_n_end / days_in_the_year
    return(result)

class BondCalculator(object):
    '''
    Bond Calculator class for pricing a bond
    '''

    def __init__(self, pricing_date):
        self.pricing_date = pricing_date

    ''' Mohammed '''
    def calc_one_period_discount_factor(self, bond, yld):
        # calculate the future cashflow vectors
        # TODO: calculate the one period discount factor
        # hint: need to use if else statement for different payment frequency cases
        '''
        note: 
        discount factor is 1 / (1 x (1 + Discount Rate) ^ Period Number)
        since this is 1 period, we can exclude period number since 1/(1+yield) ^ 1 = 1/(1+yield)
        1 period df is 1/(1+yield) for annual
        period df is 1/(1+yield/2) for semi-annual
        '''
        if (bond.payment_freq == PaymentFrequency.ANNUAL):
            df = 1/(1+yld)
        elif(bond.payment_freq == PaymentFrequency.SEMIANNUAL):
            df = 1/(1+yld/2)
        elif(bond.payment_freq == PaymentFrequency.QUARTERLY):
            df = 1/(1+yld/4)
        elif(bond.payment_freq == PaymentFrequency.MONTHLY):
            df = 1/(1+yld/12)
        elif(bond.payment_freq == PaymentFrequency.CONTINUOUS):
            df = np.exp(yld* -1) # means e^-yield
        else:
            df = None

        return(df)

    ''' Kyle '''
    def calc_clean_price(self, bond, yld):
        '''
        Calculate bond price as of the pricing_date for a given yield
        bond price should be expressed in percentage eg 100 for a par (face value) bond
        '''

        one_period_factor = self.calc_one_period_discount_factor(bond, yld)
        # TODO: implement calculation here
        df = self.calc_one_period_discount_factor
        '''Clean Price (%) = ( Coupon * (1 - (1 + yield) ^ - periods) / yield + 1 / (1 + yield)^periods ) * 100'''
        if (bond.payment_freq == PaymentFrequency.ANNUAL):
            n = 1
        elif(bond.payment_freq == PaymentFrequency.SEMIANNUAL):
            n = 2
        elif(bond.payment_freq == PaymentFrequency.QUARTERLY):
            n = 4
        elif(bond.payment_freq == PaymentFrequency.MONTHLY):
            n = 12
        elif(bond.payment_freq == PaymentFrequency.CONTINUOUS):
            n = None #TODO
        else:
            n = None
        result = ( (bond.coupon/n) * (1-(1+yld/n)**(n*-bond.term)) / (yld/n) + 1/((1+yld/n)**(n*bond.term)) )* 100
        # end TODO:

        return(result)

    ''' Kyle '''
    def calc_accrual_interest(self, bond, settle_date):

        '''
        calculate the accrual interest on given a settle_date
        by calculating the previous payment date first and use the date count
        from previous payment date to the settle_date
        '''
        prev_pay_date = bond.get_previous_payment_date(settle_date)
        end_date = settle_date
        # TODO:

        if (bond.day_count == DayCount.DAYCOUNT_30360):
            frac = get_30360_daycount_frac(prev_pay_date, settle_date)
        elif (bond.day_count == DayCount.DAYCOUNT_ACTUAL_360):
            frac = get_actual360_daycount_frac(prev_pay_date, settle_date)
        else:
            frac = get_actualactual_daycount_frac(prev_pay_date,settle_date)

        result = frac * bond.coupon * bond.principal/100
        # end TODO
        return(result)

    ''' Kyle + Tamzid '''
    def calc_macaulay_duration(self, bond, yld):
        '''
        time to cashflow weighted by PV
        '''

        if (bond.payment_freq == PaymentFrequency.ANNUAL):
            n = 1
        elif(bond.payment_freq == PaymentFrequency.SEMIANNUAL):
            n = 2
        elif(bond.payment_freq == PaymentFrequency.QUARTERLY):
            n = 4
        elif(bond.payment_freq == PaymentFrequency.MONTHLY):
            n = 12
        elif(bond.payment_freq == PaymentFrequency.CONTINUOUS):
            n = None

        wavg = 0
        for j in range(1, bond.term*n + 1):
            if (j < bond.term*n):
                wavg += j/n * ((bond.coupon/n) * bond.principal) / ((1 + yld/n)**j )
            elif(j == bond.term*n):
                wavg += j/n * (bond.principal + ((bond.coupon/n) * bond.principal)) / ((1 + yld/n)**j)

        PVs = 0
        for i in range(1, bond.term +1):
            if (i < bond.term):
                PVs += ((yld/n) * self.calc_clean_price(bond, yld)) * (1 / (1 + yld/n)**i )
            elif(i == bond.term):
                PVs +=  (self.calc_clean_price(bond, yld) + (yld/n) * self.calc_clean_price(bond, yld)) / (1 + yld/n)**i 
        
        result = wavg/PVs

        # end TODO
        return(result)

    ''' Tamzid '''
    def calc_modified_duration(self, bond, yld):
        """
        calculate modified duration at a certain yield yld
        """
        D = self.calc_macaulay_duration(bond, yld)

        # TODO: implement details here

        if bond.payment_freq == PaymentFrequency.ANNUAL:
            period = 1
        elif bond.payment_freq == PaymentFrequency.SEMIANNUAL:
            period = 1/2
        elif bond.payment_freq == PaymentFrequency.QUARTERLY:
            period = 1/4
        elif bond.payment_freq == PaymentFrequency.MONTHLY:
            period = 1/12
        else:
            period = None

        result = D/(1+yld*period)
        # end TODO:
        return(result)

    def calc_yield(self, bond, bond_price):
        '''
        Calculate the yield to maturity on given a bond price using bisection method
        '''

        def match_price(yld):
            calculator = BondCalculator(self.pricing_date)
            px = calculator.calc_clean_price(bond, yld)
            return(px - bond_price)

        # TODO: implement details here
        def f(x):
            return match_price(x)
        yld = bisection(f, .00001, 1, 0.0001)
        # end TODO:
        result = yld[0]
        return(result)

    def calc_convexity(self, bond, yld):
        # calculate convexity of a bond at a certain yield yld

        bond_price = self.calc_clean_price(bond, yld)
        i = 1
        sum = 0
        for coupon in bond.coupon_payment:
            sum = i*(i+1) * coupon/1 * (1 + yld)** (i+2)

        result = 1 / (bond_price * (1 + yld) **2) * sum
        return( result)


##########################  some test cases ###################

def _example2():
    pricing_date = date(2021, 1, 1)
    issue_date = date(2021, 1, 1)
    engine = BondCalculator(pricing_date)

    # Example 2
    bond = Bond(issue_date, term=10, day_count = DayCount.DAYCOUNT_30360,
                 payment_freq = PaymentFrequency.ANNUAL, coupon = 0.05)

    yld = 0.06
    px_bond2 = engine.calc_clean_price(bond, yld)
    print("The clean price of bond 2 is: ", format(px_bond2, '.4f'))
    assert( abs(px_bond2 - 92.640) < 0.01)

'''
'''
def _example3():
    pricing_date = date(2021, 1, 1)
    issue_date = date(2021, 1, 1)
    engine = BondCalculator(pricing_date)


    bond = Bond(issue_date, term = 2, day_count =DayCount.DAYCOUNT_30360,
                 payment_freq = PaymentFrequency.SEMIANNUAL,
                 coupon = 0.08)

    yld = 0.06
    px_bond3 = engine.calc_clean_price(bond, yld)
    print("The clean price of bond 3 is: ", format(px_bond3, '.4f'))
    assert( abs(px_bond3 - 103.717) < 0.01)


def _example4():
    # unit tests
    pricing_date = date(2021, 1, 1)
    issue_date = date(2021, 1, 1)
    engine = BondCalculator(pricing_date)

    # Example 4 5Y bond with semi-annual 5% coupon priced at 103.72 should have a yield of 4.168%
    price = 103.72
    bond = Bond(issue_date, term=5, day_count = DayCount.DAYCOUNT_30360,
                payment_freq = PaymentFrequency.SEMIANNUAL, coupon = 0.05, principal = 100)


    yld = engine.calc_yield(bond, price)
    print("The yield of bond 4 is: ", yld)
    assert( abs(yld - 0.04168) < 0.01)

def _example5():
    # unit tests
    pricing_date = date(2021, 1, 1)
    issue_date = date(2021, 1, 1)
    engine = BondCalculator(pricing_date)

    yld = .04
    bond = Bond(issue_date, term=5, day_count = DayCount.DAYCOUNT_30360,
                payment_freq = PaymentFrequency.SEMIANNUAL, coupon = 0.05, principal = 100)


    mDuration = engine.calc_macaulay_duration(bond, yld)
    print("The Macaulay Duration of bond 5 is: ", format(mDuration, '.4f'))


def _test():
    # basic test cases
    _example2()
    _example3()
    _example4()
    _example5()




if __name__ == "__main__":
    _test()

'''ignore'''