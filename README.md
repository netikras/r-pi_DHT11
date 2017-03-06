# r-pi_DHT11
DHT11 sensor readings with python

This is a variation of some DHT11 util found on the web. The one I found did everything by the book:
1. fetch data from sensor
2. validate checksum

In step 1 util used sleep(xx) between polling each bit which resulted in lots of bits either missing or repeated and checksums almost never were correct.

In this variation I actively poll 1000 bits from the sensor w/o any timeouts. Of course lots of bits do repeat. I divide the array into blocks of ones (HIs) and calculate average length of those blocks. Each block longer than avg will represent HI and every one shorter than avg -- LO. Like that:

    11111111111100000011111100000000001111111111111110000000111110000011111100000011111111111111111

        1               0                    1                0          0               1
becomes

101001

And then I do the rest.


PROS:

* >90% of polls return correct data

CONS:

* the faster CPU the more memory will be required for buffer (default -- 1000)
