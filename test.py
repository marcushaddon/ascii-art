from ascii import reduce_flicker
from random import randint

frames = [[[randint(1,20) for _ in range(2)] for _ in range(2)] for _ in range(10)]

print "before de jittering"
for frame in frames:
    for row in frame:
        print row
    print

reduce_flicker(frames, 10)

print "after de jittering"
for frame in frames:
    for row in frame:
        print row
    print
