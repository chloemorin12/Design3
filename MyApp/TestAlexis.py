from testChloe import inverse_transfer_function

a, b, c = inverse_transfer_function(19.26677379649072,  0.05307996738598514, 0.8342156871242603)
print(a,b,c)
T = 60
T2 = 25
T3 = 25

# Fctn_de_transfert 2e ordre
P_t = a*T + b*T2 + c*T3

print(P_t)