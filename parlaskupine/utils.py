from .views import howMatchingThem
from operator import itemgetter
def cus():
	a = howMatchingThem(None, 5, "deviation")
	c=[{"ratio":a[0][g]["ratio"], "name": a[0][g]["name"]} for g in a[0] if "ratio" in a[0][g].keys()]
	from operator import itemgetter
	c = sorted(c, key=itemgetter('ratio'))
	return c