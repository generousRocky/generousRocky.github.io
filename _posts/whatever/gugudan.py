# python
from time import sleep

"""
for i in range(1, 10):
    for j in range(1, 10):
        result = ("%s times %s is %s" % (i, j, i*j))
        print (result);


i = 1
while (i < 10):
    j = 1
    while(j < 10):
        result = str(i) + "X" + str(j) + "=" + str(i*j)
        print (result)
        j = j+1
    i = i + 1
"""

for i in range(1, 10):
    for j in range(1, 10):
        result = str(i) + "X" + str(j) + "=" + str(i*j)
        print (result)


def guguFunction():
    print("This is gugu function")
    for i in range(1, 10):
        for j in range(1, 10):
            result = str(i) + "X" + str(j) + "=" + str(i*j)
            print (result)

guguFunction()
guguFunction()
