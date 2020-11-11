

for i in range(10):
    for j in range(10):
        del var
        if j == 8:
            var = 42
        try:
            print(i,j,var)
        except:
            pass
