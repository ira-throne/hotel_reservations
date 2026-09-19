from mrjob.job import MRJob
from mrjob.step import MRStep

class MRJReservations (MRJob):
    MONTH_MAP = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }

    def mapper(self, _, reservation):
        # extracting contents of the line into a list
        cells = reservation.split(',')
        day = 0
        month = 0
        year = 0
        stay_length = 0
        avg_price = 0
        cancelled = False
        # if in hotel-booking file
        if len(cells) == 13:
            # checks for cancellation
            if cells[1] == '0':
            # extracts data into variables
                day = int(cells[6])
                month = self.MONTH_MAP[cells[4]]
                year = int(cells[3])
                stay_length = int(cells[7]) + int(cells[8])
                avg_price = float(cells[11])
            else:
                # if cancelled, turns on the cancellation switch
                cancelled = True
        # if customer-reservations file
        elif len(cells) == 10:
            # checks for cancellation
            if cells[9] == 'Not_Canceled':
                # extracts data into variables
                day = int(cells[6])
                month = int(cells[5])
                year = int(cells[4])
                stay_length = int(cells[1]) + int(cells[2])
                avg_price = float(cells[8])
            else:
                # if cancelled, turns on the cancellation switch
                cancelled = True

        # checks the cancellation switch
        if not cancelled:
            while stay_length > 0:
                # checks for cases when the reservation rolls into the next month
                # determines the max number of days of the reservation for current month
                # if Jan, Mar, May, Jul, Aug, Oct or Dec
                if month in [1, 3, 5, 7, 8, 10, 12]:
                    max_days_plus_one = 32
                # if Apr, Jun, Sep or Nov
                elif month in [4, 6, 9, 11]:
                    max_days_plus_one = 31
                # if February non-leap year
                elif (month == 2) and ((year % 4) != 0):
                    max_days_plus_one = 29
                # if February leap year
                else:
                    max_days_plus_one = 30
        
                # if the reservation length rolls over to next month
                if (day + stay_length) >= max_days_plus_one:
                    # count how many days of the reservation are in current month
                    days_in_month = max_days_plus_one - day
                    total_price = days_in_month * avg_price
                    # update the stay length to not account for the month that we already printed
                    stay_length = stay_length - days_in_month
                    # print a separate entry for current month
                    form_date = str(month)+ '/' + str(year)
                    yield form_date, total_price
                
                    # reset the day, increment the month
                    day = 1
                    month += 1
                    # if the month was December, increment year, reset month to January
                    if month > 12:
                        month = 1
                        year += 1
                    
                else:
                    # default case: the whole reservation is in one month
                    total_price = avg_price * stay_length
                    stay_length = 0
                    form_date = str(month)+ '/' + str(year)
                    # yields date (month/year) as key, total for each reservation for that date as value
                    yield form_date, total_price

    # pre-combines entries with the same date
    # makes reducer more efficient
    def combiner(self, date, totals):
        yield date, sum(totals)

    # sums up totals for each date
    # doesn't yield a key, but yields value with the totals as the first column
    def sum_reducer(self, date, totals):
        yield None, (sum(totals), date)
    
    # takes input from the first reducer, sorts it in reverse order by total
    # yields date as key, total (rounded to two decimals) as value
    def sort_reducer(self, _, totals):
        for total, date in sorted(totals, reverse=True):
            yield date, round(total,2)
    
    def steps(self):
        return [
            MRStep(
            mapper=self.mapper,
            combiner=self.combiner,
            reducer=self.sum_reducer
            ),
            MRStep(
            reducer=self.sort_reducer
            )]


if __name__=='__main__':
    MRJReservations.run()