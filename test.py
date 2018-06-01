#calculate shit
counter = 502
total = 0
while (counter != 0):
    total += counter
    counter -= 1
print(total)

same = 4
something = [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15]]
for i in range(same):
    for j in range(same):
        print(something[i][j])

templist = []
tempMatrix = 0
while (tempMatrix < 10):
    templist.append([])
    tempMatrix += 1
templist[2].append(0)
print(templist)
