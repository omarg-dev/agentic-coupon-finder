import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.finder.collector import CouponFinder

finder = CouponFinder()
# finder.find_codes("amazon.sa") # test with a complex regional domain
# finder.find_codes("dominos.sa") # test with simple regional domain
finder.find_codes("maestropizza.com") # the simplest of them all (literally has a coupon field on homepage)