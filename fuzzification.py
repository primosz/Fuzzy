from typing import List
import matplotlib.pyplot as plt
import numpy as np
import csv

rules = []


class Triangle:
    def __init__(self, name, start, peak, end, none=0):
        self.name = name
        self.a = start
        self.b = peak
        self.c = end

    def __str__(self):
        return ' ' + self.name + str(self.a) + str(self.b) + str(self.c)

    def __call__(self, x):
        if x < self.a or x > self.c:
            return {'set': self.name, 'value': 0}
        elif x == self.b:
            return {'set': self.name, 'value': 1}
        elif x < self.b:
            return {'set': self.name, 'value': (x - self.a) / (self.b - self.a)}
        elif x > self.b:
            return {'set': self.name, 'value': 1 - ((x - self.b) / (self.c - self.b))}


class Trapezoid:
    def __init__(self, name, start, peak_first, peak_second, end):
        self.name = name
        self.a = start
        self.b = peak_first
        self.c = peak_second
        self.d = end

    def __call__(self, x):
        if x < self.a or x > self.d:
            return {'set': self.name, 'value': 0}
        elif self.b <= x <= self.c:
            return {'set': self.name, 'value': 1}
        elif x < self.b:
            return {'set': self.name, 'value': (x - self.a) / (self.b - self.a)}
        elif x > self.c:
            return {'set': self.name, 'value': 1 - ((x - self.c) / (self.d - self.c))}


class Gaussian:
    def __init__(self, name, expected_value, sigma, none_1=0, none_2=0):
        self.name = name
        self.mu = expected_value
        self.sigma = sigma

    def __call__(self, x):
        return {'set': self.name, 'value': np.exp(-np.power(x - self.mu, 2.) / (2 * np.power(self.sigma, 2.)))}


# you can create rules by giving parameters:
# 1 - list of fuzze sets objects
# 2 - list of temperatures in rule
# 3 - what is target temperature (after 'AND')
# 4 - what is the actions (after 'THEN')
class Rule:
    def __init__(self, fuzzySets, currentTable, target, then):
        self.fuzzySets = fuzzySets
        self.currentTable = currentTable
        self.target = target
        self.then = then

    def __call__(self, currentTemp, targetTemp):
        currentTempsMemberships = []
        for fSet in self.currentTable:
            foundSet = next((x for x in self.fuzzySets if x.name == fSet), None)
            currentTempsMemberships.append(foundSet(currentTemp)['value'])

        foundSet = next((x for x in self.fuzzySets if x.name == self.target), None)
        targetMembership = foundSet(targetTemp)['value']

        result = min(max(currentTempsMemberships), targetMembership)
        return {'action': self.then, 'membership': result}

    def __str__(self):
        current_string = ' or '.join(self.currentTable)
        return f"If it's {current_string} and target is {self.target} then {self.then}."


def loadRules(filename, fuzzySets):
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            currentTempslist = list(row[0].split(";"))
            rules.append(Rule(fuzzySets, currentTempslist, row[1], row[2]))


def rulesAggregation(rules, outputFuzzySets):
    result = [0] * 200
    for set in outputFuzzySets:
        for i in range(200):
            if set(i)['value'] > 0:
                matches = [x['membership'] for x in rules if x['action'] == set.name and x['membership'] > 0]
                if len(matches) > 0:
                    tmp = set(i)['value']
                    if result[i] < min(max(matches), tmp):
                     result[i] = min(max(matches), tmp)
    return result


def calulcateCentroid(plot):
    n = len(plot)
    x = list(range(n))
    num = 0
    denum = 0
    for i in range(n):
        num += x[i] * plot[i]
        denum += plot[i]
    return num / denum


def drawFinalPlot(outputFuzzySets, aggregatedRules, point):

    print(f'Final result: {point}')
    plt.figure(figsize=(12,6))
    plt.ylim(0, 1)
    for x in outputFuzzySets:
        plt.plot(np.linspace(0, 200, 200), [x(i)['value'] for i in range(0, 200)], '--', label=x.name, linewidth='0.5')

    plt.fill_between(np.linspace(0, 200, 200), aggregatedRules)
    plt.plot(np.linspace(0, 200, 200), aggregatedRules, label="Output membership", fillstyle='full')
    plt.axvline(x=point, label=f'Centroid: {point}', color='black')

    plt.ylabel('memberships')
    plt.legend()
    plt.show()


def test_functions():
#fuzzy sets for input
    very_cold = Trapezoid("VERY COLD", -20, -20, 5, 10)
    cold = Triangle("COLD", 5, 10, 15)
    warm = Gaussian("WARM", 18, 3)
    hot = Gaussian("HOT", 22, 5)
    very_hot = Trapezoid("VERY HOT", 25, 30, 50, 50)
    classes = [very_cold, cold, warm, hot, very_hot]

#fuzzy sets for output
    cool = Triangle("COOL", 0, 50, 100)
    no_change = Triangle("NO CHANGE", 50, 100, 150)
    heat = Triangle("HEAT", 100, 150, 200)
    outputFuzzySets = [cool, no_change, heat]

    loadRules("rules.csv", classes)

    for x in rules:
        print(x)

    temp1 = 22
    temp2 = 22

    current = [x(temp1) for x in classes]
    target = [x(temp2) for x in classes]

    print(current)
    print(target)

    rule1 = Rule(classes, ["VERY COLD"], "VERY COLD", "NO CHANGE")
    #          IF temperature=(Cold OR Warm OR Hot OR Very_Hot) AND target=Very_Cold THEN	Cool
    rule2 = Rule(classes, ["COLD", "WARM", "HOT", "VERY HOT"], "VERY COLD", "COOL")
    rule3 = Rule(classes, ["VERY COLD"], "COLD", "HEAT")
    rule4 = Rule(classes, ["COLD"], "COLD", "NO CHANGE")
    rule5 = Rule(classes, ["WARM", "HOT", "VERY HOT"], "COLD", "COOL")
    rule6 = Rule(classes, ["COLD", "VERY COLD"], "WARM", "HEAT")
    rule7 = Rule(classes, ["WARM"], "WARM", "NO CHANGE")
    rule8 = Rule(classes, ["HOT", "VERY HOT"], "WARM", "COOL")
    rule9 = Rule(classes, ["VERY COLD", "COLD", "WARM"], "HOT", "HEAT")
    rule10 = Rule(classes, ["HOT"], "HOT", "NO CHANGE")
    rule11 = Rule(classes, ["VERY HOT"], "WARM", "COOL")
    rule12 = Rule(classes, ["VERY COLD", "COLD", "WARM", "HOT"], "VERY HOT", "HEAT")
    rule13 = Rule(classes, ["VERY HOT"], "VERY HOT", "NO CHANGE")

    print(rule1(temp1, temp2))
    print(rule2(temp1, temp2))
    print(rule3(temp1, temp2))
    print(rule4(temp1, temp2))
    print(rule5(temp1, temp2))
    print(rule6(temp1, temp2))
    print(rule7(temp1, temp2))
    print(rule8(temp1, temp2))
    print(rule9(temp1, temp2))
    print(rule10(temp1, temp2))
    print(rule11(temp1, temp2))
    print(rule12(temp1, temp2))
    print(rule13(temp1, temp2))
    evaluatedRules = [rule1(temp1, temp2), rule2(temp1, temp2), rule3(temp1, temp2), rule4(temp1, temp2), rule5(temp1, temp2), rule6(temp1, temp2),
                      rule7(temp1, temp2), rule8(temp1, temp2), rule9(temp1, temp2), rule10(temp1, temp2), rule11(temp1, temp2), rule12(temp1, temp2), rule13(temp1, temp2)]


    aggregatedRules = rulesAggregation(evaluatedRules, outputFuzzySets)
    centroid = calulcateCentroid(aggregatedRules)

    drawFinalPlot(outputFuzzySets, aggregatedRules, centroid)



test_functions()
