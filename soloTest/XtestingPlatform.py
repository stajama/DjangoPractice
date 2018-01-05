def calculateFahrenheit(tempString):
    '''Returns the string input in Kelvin as a string in Fahrenheit.)'''
    temp = float(tempString)
    print(temp)
    return str(round((temp * (9 / 5)) - 459.67, 2))

def calculateFahrenheit2(tempString):
    '''Returns the string input in Kelvin as a string in Fahrenheit.)'''
    temp = float(tempString)
    print(temp)
    return str(round((temp * (9.0 / 5.0)) - 459.67, 2))

print(calculateFahrenheit(272.27), calculateFahrenheit2(272.27))
