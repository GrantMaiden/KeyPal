import sqlite3
import os
from os.path import isfile, join

basepath = os.path.dirname(os.path.abspath(__file__))

connection = sqlite3.connect(basepath + "/sentences.db")
cur = connection.cursor()

#cur.execute('DROP TABLE sentences')
cur.execute('CREATE TABLE sentences (sentence varchar(255), words int, chars int, level int)')

with open(join(basepath, "sentences.txt"), "r") as f:
    #allchars = []
    for line in f:
        realLine = line.rstrip()
        numChars = len(realLine)
        #allchars.append(numChars)
        numWords = len(realLine.split())
        if realLine.count('"') % 2 == 1:
			continue;
			
        if numChars < 22:
            level = 0
        elif numChars < 30:
            level = 1
        elif numChars < 38:
            level = 2
        elif numChars < 46:
            level = 3
        elif numChars < 55:
            level = 4
        #elif numChars < 64:
        #    level = 5
        #elif numChars < 75:
        #    level = 6
        #else:
        #    level = 7
        else:
			continue;

        #print "{}\t{}\t{}\t{}".format(numChars, numWords, level, realLine)
        #print "INSERT INTO sentences VALUES ('{}', '{}', '{}', '{}')".format(realLine, numWords, numChars, level)
        data = (realLine, numWords, numChars, level)
        cur.execute('INSERT INTO sentences VALUES (?,?,?,?)', data)

    '''
    allchars.sort()
    length = len(allchars)
    numLevels = 8
    for i in range(numLevels-1):
        #print i
        cutoff = int(length * (i+1) / numLevels)
        #print cutoff
        print allchars[cutoff]


    cutoff1 = int(length * 1 / 5)
    cutoff2 = int(length * 2 / 5)
    cutoff3 = int(length * 3 / 5)
    cutoff4 = int(length * 4 / 5)
    print "{} {} {} {}".format(cutoff1, cutoff2, cutoff3, cutoff4)
    print "{} {} {} {}".format(allchars[cutoff1], allchars[cutoff2], allchars[cutoff3], allchars[cutoff4])
    '''

connection.commit()
connection.close()

