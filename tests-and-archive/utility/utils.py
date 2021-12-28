from typing import List


def move(list: List, amount: int = 1) -> List:
    if amount < 0:
        for i in range(amount, len(list)):
            list[i+amount] = list[i]
    else:
        for i in range(len(list)):
            list[len(list)-1-i+amount] = list[len(list)-1-i]