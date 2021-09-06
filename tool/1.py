with open('CET6.txt', 'r', encoding='UTF-8') as f:
    destination = open(r"CET6-en.txt", 'wb+')
    lines = f.readlines()
    for line in lines:
        line = str(line)
        result = line.split(' ')
        result = result[0] + '\n'
        destination.write(result.encode())
    destination.close()
