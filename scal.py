#!/usr/bin/env python3

import datetime
import sys
import argparse # Import the argparse module for command-line argument parsing

# ANSI escape codes for text formatting
# These codes are used for coloring and background in the terminal.
# They might not work on all terminals, but are standard for most modern ones.
BLACK = '\033[30m' # ANSI escape code for black foreground color
WHITE_BACKGROUND = '\033[107m' # ANSI escape code for white background
RESET = '\033[0m'

# --- Shamsi Calendar Conversion Logic ---
# This section contains the core logic for converting between Gregorian and Shamsi dates.
# It is based on standard algorithms for the Jalali calendar.

def is_shamsi_leap_year(shamsi_year):
    """
    Determines if a given Shamsi year is a leap year.
    Reference: https://en.wikipedia.org/wiki/Iranian_calendars#Leap_years
    """
    rem = (shamsi_year + 2346) % 33
    return rem == 1 or rem == 5 or rem == 9 or rem == 13 or rem == 17 or rem == 21 or rem == 26 or rem == 30


def shamsi_to_gregorian(shamsi_year, shamsi_month, shamsi_day):
    """
    Converts a Shamsi date to a Gregorian date.
    Returns a tuple (gregorian_year, gregorian_month, gregorian_day).
    """
    g_days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    j_days_in_month = [0, 31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]

    if is_shamsi_leap_year(shamsi_year):
        j_days_in_month[12] = 30

    jy = shamsi_year
    jm = shamsi_month
    jd = shamsi_day

    days_passed_shamsi = sum(j_days_in_month[1:jm]) + jd

    gy = jy + 621

    if is_shamsi_leap_year(jy - 1):
        g_day_of_year_new_year = 80
    else:
        g_day_of_year_new_year = 79

    total_days_gregorian = g_day_of_year_new_year + days_passed_shamsi

    if total_days_gregorian > 365 + (1 if (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0) else 0):
        total_days_gregorian -= (365 + (1 if (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0) else 0))
        gy += 1

    gm = 1
    gd = 0
    while total_days_gregorian > 0:
        days_in_current_g_month = g_days_in_month[gm]
        if gm == 2 and ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)):
            days_in_current_g_month = 29

        if total_days_gregorian <= days_in_current_g_month:
            gd = total_days_gregorian
            break
        else:
            total_days_gregorian -= days_in_current_g_month
            gm += 1

    return gy, gm, gd


def gregorian_to_shamsi(gregorian_year, gregorian_month, gregorian_day):
    """
    Converts a Gregorian date to a Shamsi date.
    Returns a tuple (shamsi_year, shamsi_month, shamsi_day).
    """
    g_days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    j_days_in_month = [0, 31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]

    gy = gregorian_year
    gm = gregorian_month
    gd = gregorian_day

    days_passed_gregorian = sum(g_days_in_month[1:gm]) + gd
    if gm > 2 and ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)):
        days_passed_gregorian += 1

    jy = gy - 621
    if days_passed_gregorian < 80:
        jy -= 1

    if is_shamsi_leap_year(jy - 1):
        g_day_of_year_new_year = 80
    else:
        g_day_of_year_new_year = 79

    days_passed_shamsi = days_passed_gregorian - g_day_of_year_new_year
    if days_passed_shamsi < 1:
        if is_shamsi_leap_year(jy):
            days_passed_shamsi += 366
        else:
            days_passed_shamsi += 365

    jm = 1
    jd = 0
    while days_passed_shamsi > 0:
        days_in_current_j_month = j_days_in_month[jm]
        if jm == 12 and is_shamsi_leap_year(jy):
            days_in_current_j_month = 30

        if days_passed_shamsi <= days_in_current_j_month:
            jd = days_passed_shamsi
            break
        else:
            days_passed_shamsi -= days_in_current_j_month
            jm += 1

    return jy, jm, jd


def get_shamsi_month_name(month_number):
    """Returns the Shamsi month name for a given month number (1-12)."""
    shamsi_month_names = [
        "", "Farvardin", "Ordibehesht", "Khordad", "Tir", "Mordad", "Shahrivar",
        "Mehr", "Aban", "Azar", "Dey", "Bahman", "Esfand"
    ]
    return shamsi_month_names[month_number]


def get_days_in_shamsi_month(shamsi_year, shamsi_month):
    """Returns the number of days in a given Shamsi month."""
    if 1 <= shamsi_month <= 6:
        return 31
    elif 7 <= shamsi_month <= 11:
        return 30
    elif shamsi_month == 12:
        return 30 if is_shamsi_leap_year(shamsi_year) else 29
    else:
        raise ValueError("Invalid Shamsi month number.")

# --- Calendar Display Logic ---

def print_shamsi_calendar(year, month, current_shamsi_day=None):
    """
    Prints the Shamsi calendar for the given year and month.
    Optionally highlights the current_shamsi_day if provided and within the displayed month.
    """
    month_name = get_shamsi_month_name(month)

    print(f"\n      {month_name} {year}")
    print(" Sa Su Mo Tu We Th Fr")

    g_year_first_day, g_month_first_day, g_day_first_day = shamsi_to_gregorian(year, month, 1)
    
    first_day_of_month = datetime.date(g_year_first_day, g_month_first_day, g_day_first_day)

    # Calculate leading spaces for the first day of the month
    # Python's weekday(): Monday=0, Sunday=6.
    # We want: Saturday=0, Sunday=1, Monday=2, Tuesday=3, Wednesday=4, Thursday=5, Friday=6
    leading_spaces = (first_day_of_month.weekday() + 2) % 7

    print("   " * leading_spaces, end="")

    current_day_in_loop = 1
    num_days_in_month = get_days_in_shamsi_month(year, month)

    while current_day_in_loop <= num_days_in_month:
        day_num_str = str(current_day_in_loop)
        
        padding_needed = 3 - len(day_num_str)

        if current_shamsi_day is not None and current_day_in_loop == current_shamsi_day:
            print(" " * padding_needed + BLACK + WHITE_BACKGROUND + day_num_str + RESET, end="")
        else:
            print(f"{current_day_in_loop:3}", end="")
        
        # Move to the next line after Friday (6th day of the week, if Saturday is 0)
        # This means, if (leading_spaces + current_day_in_loop) is a multiple of 7, it's the end of the line.
        if (leading_spaces + current_day_in_loop) % 7 == 0:
            print()
        
        current_day_in_loop += 1
    
    # Print a final newline if the last day didn't end on a Friday
    if (leading_spaces + num_days_in_month) % 7 != 0:
        print()
    print() # Extra newline for spacing


# --- Main Execution ---

if __name__ == "__main__":
    current_g_date = datetime.date.today()
    current_shamsi_year, current_shamsi_month, current_shamsi_day = gregorian_to_shamsi(
        current_g_date.year, current_g_date.month, current_g_date.day
    )

    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Display Shamsi calendar or convert dates.",
        formatter_class=argparse.RawTextHelpFormatter # For better formatting of help message
    )

    # Mutually exclusive group for conversion options
    conversion_group = parser.add_mutually_exclusive_group()
    conversion_group.add_argument(
        "-g", "--gregorian",
        help="Convert a Gregorian date (YYYY-MM-DD) to Shamsi.",
        metavar="DATE"
    )
    conversion_group.add_argument(
        "-s", "--shamsi",
        help="Convert a Shamsi date (YYYY-MM-DD) to Gregorian.",
        metavar="DATE"
    )

    # Positional arguments for calendar display
    parser.add_argument(
        "month",
        nargs="?", # 0 or 1 argument
        type=int,
        help="Shamsi month (1-12). If only year is provided, displays all months of that year."
    )
    parser.add_argument(
        "year",
        nargs="?", # 0 or 1 argument
        type=int,
        help="Shamsi year."
    )

    args = parser.parse_args()

    # Handle conversion requests
    if args.gregorian:
        try:
            g_year, g_month, g_day = map(int, args.gregorian.split('-'))
            if not (1 <= g_month <= 12 and 1 <= g_day <= 31): # Basic validation
                raise ValueError("Invalid month or day in Gregorian date.")
            shamsi_y, shamsi_m, shamsi_d = gregorian_to_shamsi(g_year, g_month, g_day)
            print(f"Gregorian {args.gregorian} is Shamsi {shamsi_y}-{shamsi_m:02d}-{shamsi_d:02d}")
        except ValueError as e:
            print(f"Error: Invalid Gregorian date format or value. Please use YYYY-MM-DD. ({e})")
        sys.exit(0)

    if args.shamsi:
        try:
            s_year, s_month, s_day = map(int, args.shamsi.split('-'))
            if not (1 <= s_month <= 12 and 1 <= s_day <= 31): # Basic validation
                raise ValueError("Invalid month or day in Shamsi date.")
            gregorian_y, gregorian_m, gregorian_d = shamsi_to_gregorian(s_year, s_month, s_day)
            print(f"Shamsi {args.shamsi} is Gregorian {gregorian_y}-{gregorian_m:02d}-{gregorian_d:02d}")
        except ValueError as e:
            print(f"Error: Invalid Shamsi date format or value. Please use YYYY-MM-DD. ({e})")
        sys.exit(0)

    # Handle calendar display requests (original functionality)
    if args.month is not None and args.year is not None:
        try:
            if not (1 <= args.month <= 12):
                raise ValueError("Month must be between 1 and 12.")
            
            day_to_highlight = None
            if args.year == current_shamsi_year and args.month == current_shamsi_month:
                day_to_highlight = current_shamsi_day
            
            print_shamsi_calendar(args.year, args.month, day_to_highlight)
            sys.exit(0)
        except ValueError as e:
            print(f"Error: {e}")
            print("Usage: scal [month] [year]")
            print("       scal [year]")
            print("       scal (for current month)")
            sys.exit(1)
    elif args.month is not None and args.year is None: # Only year provided (as the 'month' argument)
        try:
            target_year = args.month # The first positional argument is interpreted as the year
            for m in range(1, 13):
                if target_year == current_shamsi_year and m == current_shamsi_month:
                    print_shamsi_calendar(target_year, m, current_shamsi_day)
                else:
                    print_shamsi_calendar(target_year, m)
            sys.exit(0)
        except ValueError: # Should ideally not happen if type=int is used, but good for robustness
            print("Usage: scal [month] [year]")
            print("       scal [year]")
            print("       scal (for current month)")
            sys.exit(1)
    elif args.month is None and args.year is None:
        # No arguments, show current month and highlight current day
        print_shamsi_calendar(current_shamsi_year, current_shamsi_month, current_shamsi_day)
        sys.exit(0)
    else:
        # This case should ideally be caught by argparse itself, but as a fallback
        parser.print_help()
        sys.exit(1)

