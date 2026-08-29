import math

input=[0.2, 0.7, 0.4]
weights=[0.5, -0.2, 0.8]
bias=[0.1,0.2,0.11]

cal=[0, 0, 0]

for i in range(len(input)):
    for j in range(len(weights)):
        cal[i]+=input[i]*weights[j]
    cal[i]=math.tanh(cal[i]+bias[i])


print(cal)
