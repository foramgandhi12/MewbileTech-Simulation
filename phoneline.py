from typing import List, Dict, Tuple, Optional, Union
from call import Call
from callhistory import CallHistory
from bill import Bill
from contract import Contract


class PhoneLine:
    """ MewbileTech customer's phone line.

    === Public Attributes ===
    number:
         phone number
    contract:
         current contract for this phone, represented by a Contract instance
    bills:
         dictionary containing all the bills for this phoneline
         each key is a (month, year) tuple and the corresponding value is
         the Bill object for that month+year date.
    callhistory:
         call history for this phone line, represented as a CallHistory object

    === Representation Invariants ===
    - the <bills> dictionary contains as keys only those month+year combinations
    for dates that are encountered at least in one call from the input dataset.
    """
    number: str
    contract: Contract
    bills: Dict[Tuple[int, int], Bill]
    callhistory: CallHistory

    def __init__(self, number: str, contract: Contract) -> None:
        """ Creates a new PhoneLine with <number> and <contract>.
        """
        self.number = number
        self.contract = contract
        self.callhistory = CallHistory()
        self.bills = {}

    def new_month(self, month: int, year: int) -> None:
        """ Advances to a new month (specified by <month> and <year>) in the
        contract corresponding to this phone line.
        If the new month+year does not already exist in the <bills> attribute,
        creates a new bill.
        """
        if (month, year) not in self.bills:
            self.bills[(month, year)] = Bill()
            self.contract.new_month(month, year, self.bills[(month, year)])

    def make_call(self, call: Call) -> None:
        """ Adds the <call> to this phone line's callhistory, and bills it
        according to the contract for this phone line.
        If there is no bill for the current monthly billing cycle, then a new
        month must be <started> by advancing to the right month from <call>.
        """

        if call.get_bill_date() not in self.bills:
            self.new_month(call.time.month, call.time.year)
        self.callhistory.register_outgoing_call(call)
        self.contract.bill_call(call)

    def receive_call(self, call: Call) -> None:
        """ Adds the <call> to this phone line's callhistory.
        Incoming calls are not billed under any contract.
        However, if there is no bill for the current monthly billing cycle,
        then a new month must be <started> by advancing to the right month from
        <call>.
        """
        if call.get_bill_date() not in self.bills:
            self.new_month(call.time.month, call.time.year)
        self.callhistory.register_incoming_call(call)

    def cancel_line(self) -> float:
        """ Cancels this line's contract and returns the outstanding bill amount
        """
        return self.contract.cancel_contract()

    def get_number(self) -> str:
        """ Returns the phone number for this line
        """
        return self.number

    def get_call_history(self) -> CallHistory:
        """ Returns the CallHistory for this line
        """
        return self.callhistory

    def get_monthly_history(self, month: int = None, year: int = None) -> \
            Tuple[List[Call], List[Call]]:
        """ Returns all calls this line has made during the <month> month of the
        <year> year, formatted as a Tuple containing two lists, in this order:
        outgoing calls, incoming calls

        If month and year are both None, then return all calls from the
        callhistory of this phone line.

        Precondition:
        - <month> and <year> are either both specified, or are both missing/None
        - if <month> and <year> are specified (non-None), they are both valid
        monthly cycles according to the input dataset
        """
        return self.callhistory.get_monthly_history(month, year)

    def get_bill(self, month: int, year: int) \
            -> Optional[Dict[str, Union[float, int]]]:
        """ Returns a bill summary for the <month>+<year> billing cycle, as a
        dictionary.
        This dictionary will include the following string keys:
        "number" - indicates the phone number
        "type" - indicates the contract type
        "fixed" - fixed cost for that month
        "free_mins" - number of free minutes used in this monthly cycle
        "billed_mins" - number of billed minutes used in this monthly cycle
        "min_rate" - billing rate per minute
        "total" - total cost for this monthly bill
        The values corresponding to each key represent the respective amounts.
        If no bill exists for this month+year, return None.
        """
        if (month, year) not in self.bills:
            return None

        bill_summary = self.bills[(month, year)].get_summary()
        bill_summary['number'] = self.number
        return bill_summary


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing',
            'call', 'callhistory', 'bill', 'contract'
        ],
        'generated-members': 'pygame.*'
    })
