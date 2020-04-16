#!/usr/bin/env python
# -*- coding:utf-8 -*

import os, time


print("Test écriture lente, mais sans fermer le fichier")
filename = './hotfolder/test1.txt'
os.remove(filename)
with open(filename,"a") as file:
    for i in range(500):
        print(i)
        file.write(str(i))
        time.sleep(0.1)

print("Test écriture lente, en fermant le fichier")
filename = './hotfolder/test2.txt'
os.remove(filename)
for i in range(500):
    print(i)
    with open(filename,"a") as file:
        file.write(str(i))
    time.sleep(0.1)

print("Test écriture très lente, en fermant le fichier")
filename = './hotfolder/test3.txt'
os.remove(filename)
for i in range(50):
    print(i)
    with open(filename,"a") as file:
        file.write(str(i))
    time.sleep(1)
