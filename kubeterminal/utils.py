import math

def log_scale(numbers, log_type='natural'):
    """
    This function takes a list of numbers and returns a new list where numbers greater than 10 are scaled logarithmically and then 10 is added.
    Numbers less than or equal to 10 are returned unchanged.
    
    Parameters:
    numbers (list of float): A list of numbers to be scaled.
    log_type (str): The type of logarithm to use ('natural' for ln, 'log10' for base 10). Default is 'natural'.
    
    Returns:
    list of float: A new list with numbers scaled logarithmically if greater than 10 and 10 added to them, otherwise unchanged.
    """
    if log_type == 'natural':
        log_func = math.log
    elif log_type == 'log10':
        log_func = math.log10
    else:
        raise ValueError("Invalid log_type. Use 'natural' for ln or 'log10' for base 10 logarithm.")
    
    return [log_func(num) + 10 if num > 10 else num for num in numbers]
