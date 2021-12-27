import math

def sign(x):
    if x == 0:
        return 0
    if x < 0:
        return -1
    return 1

def approx(a, b, variance):
    return a < b + variance and a > b - variance

# Animate with quadratic growth, then exponential decay
def quadratic_exponential(value, change_rate, target, acceleration, drag, delta_time):
    moving_twd = value - change_rate / math.log(drag)

    # Cap change_rate if it is too big
    if moving_twd > target + 0.001:
        change_rate = (value - target) * math.log(drag)
        moving_twd = value - change_rate / math.log(drag)
    
    # Accelerate if change_rate is too small
    if moving_twd < target - 0.001:
        change_rate += acceleration * delta_time
        moving_twd = value - change_rate / math.log(drag)
    
    # Slow down if that way you reach target precisely
    if approx(moving_twd, target, 0.001):
        change_rate *= pow(drag, delta_time)
    
    return change_rate

# animate with circular growth, then exponential decay
def circular_exponential(value, change_rate, target, acceleration, acceleration_modifier, drag, delta_time):
    moving_twd = value - change_rate / math.log(drag)

    # Cap change_rate if it is too big
    if moving_twd > target + 0.01:
        change_rate = (value - target) * math.log(drag)
        moving_twd = value - change_rate / math.log(drag)
    
    # Accelerate if change_rate is too small
    if moving_twd < target - 0.01:
        if math.atan(change_rate) + acceleration * delta_time < math.pi/2:
            change_rate = acceleration_modifier * math.tan(math.atan(change_rate / acceleration_modifier) + acceleration * delta_time)
        else:
            change_rate += change_rate - acceleration_modifier * math.tan(math.atan(change_rate / acceleration_modifier) - acceleration * delta_time)
        moving_twd = value - change_rate / math.log(drag)
    
    # Slow down if that way you reach target precisely
    if approx(moving_twd, target, 0.01):
        change_rate *= pow(drag, delta_time)
        change_rate = ((value + change_rate * delta_time) - target) * math.log(drag)
    
    return change_rate