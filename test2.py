import time
start_time = time.time()
counter = 0
while (counter != 126253):
    counter += 1
    print(counter)
print "My program took", time.time() - start_time, "to run."
