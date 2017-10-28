#!/usr/bin/env python

"""

Solution for static data.

"""


def floor_power_of_two(x):
    x = x | (x >> 1)
    x = x | (x >> 2)
    x = x | (x >> 4)
    x = x | (x >> 8)
    x = x | (x >> 16)
    x = x | (x >> 32)
    return x - (x >> 1)


def insertion_sort(a):
    i = 1
    while i < len(a):
        j = i
        while j > 0 and a[j - 1] > a[j]:
            a[j], a[j - 1] = a[j - 1], a[j]
            j = j - 1
        i = i + 1
    return a


def block_sort(a):
    power_of_two = floor_power_of_two(len(a))
    scale = len(a) / power_of_two

    for merge in range(0, power_of_two, 16):
        start = int(merge * scale)
        end = int(min(start + (scale * 16), len(a)))
        insertion_sort(a[start:end])

    length = 16

    while length < power_of_two:
        for merge in range(0, power_of_two, length * 2):
            start = merge * scale
            mid = (merge + length) * scale
            end = (merge + length * 2) * scale

            if array[end - 1] < array[start]:
                rotate(array, mid - start, range(start, end))
            elif array[mid - 1] > array[mid]:
                merge(array, range(start, mid), range(mid, end))
        length += length


if __name__ == '__main__':
    print("Solution - Static")
    array = [5, 6, 9, 5, 8, 2, 4]
    block_sort(array)
