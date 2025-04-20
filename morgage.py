
def calc_pmt(pv, r, n):
    pmt = (PV*r)/(((1/(1+r)**(n*12)))-1)

def schedule(pv, r, n, pmt):
    month = 1
    print("-"*36)
    print(f"{n/12} year mortgage for a ${pv} house.".center(36))
    print("Month".center(8), "Payment".center(8), "Principle Reduction")


PV = int(input("Enter the cost of the house: "))
interest = float(input("Enter the interest rate: "))
n = 12 * float(input("Enter the years of the mortgage: "))
print(f"There will be {n} payments to be made.")
pmtnec = input("Do you know the payment amount?")
if pmtnec.lower() == "no":
    pmt = calc_pmt(PV, interest, n)
else:
    pmt = input("Enter monthly payment amount: ")

