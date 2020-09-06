import datetime
from math import ceil
from typing import Optional
from bill import Bill
from call import Call


# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


class Contract:
    """ A contract for a phone line

    This is an abstract class. Only subclasses should be instantiated.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.datetime
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Creates a new Contract with the <start> date, starts as inactive
        """
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advances to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Stores the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        """ Adds the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Returns the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return self.bill.get_cost()


class TermContract(Contract):
    """ People pay a deposit for this contract, if they make it to the end
    of the contract, then they get back the deposit, if it is not met, then
    the deposit is taken.
    """
    start: datetime.datetime
    end: datetime.datetime
    bill: Optional[Bill]
    term_minutes: int
    saved_month: datetime.date

    def __init__(self, start: datetime.date, end: datetime.date) -> None:
        self.end = end
        self.start = start
        self.saved_month = 0
        self.term_minutes = 0

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        self.bill = bill
        self.bill.set_rates("TERM", TERM_MINS_COST)
        self.term_minutes = 100
        self.bill.add_fixed_cost(TERM_MONTHLY_FEE)
        if (month, year) == (self.start.month, self.start.year):

            self.bill.add_fixed_cost(TERM_DEPOSIT)
        self.saved_month = (month, year)

    def bill_call(self, call: Call) -> None:

        if self.term_minutes > 0:
            self.bill.free_min += (ceil(call.duration / 60.0))
            self.term_minutes -= (ceil(call.duration / 60.0))
            if self.term_minutes < 0:
                self.bill.add_billed_minutes((self.term_minutes*-1))

        elif self.term_minutes == 0:
            self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:

        if self.saved_month > (self.end.month, self.end.year):
            self.start = None
            self.end = None
            self.bill.add_fixed_cost(-300)
            self.bill.get_cost()

        elif self.saved_month < (self.end.month, self.end.year):
            self.start = None
            self.end = None
            self.bill.get_cost()


class MTMContract(Contract):
    """"People start the contract at any time and they can cancel it anytime
    without a cancelling fee, they pay higher rates for calls however
    because there is no commitment"""
    start: datetime.datetime
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        self.bill = bill
        self.bill.set_rates("MTM", MTM_MINS_COST)
        self.bill.add_fixed_cost(MTM_MONTHLY_FEE)


class PrepaidContract(Contract):
    """People pay a balance which is their credit for the contract and they
    and they can fill it up whenever they want, there is no cancelling fee
    but their credit gets forfeited if they do."""
    start: datetime.datetime
    bill: Optional[Bill]
    balance: int

    def __init__(self, start: datetime.date, balance: int) -> None:
        self.start = start
        self.balance = balance

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        self.bill = bill
        self.bill.set_rates("PREPAID", PREPAID_MINS_COST)
        self.bill.add_fixed_cost(self.balance * -1)
        if self.balance > -10:
            self.balance -= 25

    def bill_call(self, call: Call) -> None:
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        self.start = None
        if self.balance > 0:
            self.bill.add_fixed_cost(self.balance)
            return self.bill.get_cost()

        else:
            return 0.0


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call', 'math'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
