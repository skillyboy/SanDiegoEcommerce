from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from .models.user import User, FarmerProfile, BuyerProfile
from .models.models import Cooperative, Vehicle, LogisticsRequest, TrackingStatus, Notification, FarmerSubscription, CropCalendar, WeatherData, AgroAnalytics, SystemSettings
from .models.market import ProductCategory, Product, ProductImage, ProductReview, CropListing, Bid, Offer, Order, OrderItem, PriceTrend
from .models.finance import Wallet, WalletTransaction, Contract, SavingsAccount, SavingsTransaction, MobileMoneyProcessor, SMSGateway, LoanApplication, LoanRepayment, RepaymentSchedule, CropInsurance, InsuranceClaim
from .models.thrift import ThriftGroup, ThriftMembership, ThriftContribution, ThriftPayout, ThriftCycle, ThriftMeeting, ThriftAttendance, ThriftPenalty, ThriftLoan, ThriftLoanRepayment
from .models.chat import ChatRoom, ChatMessage

# Register models
for model in [
	User, FarmerProfile, BuyerProfile, Cooperative, Vehicle, LogisticsRequest,
	TrackingStatus, Notification, FarmerSubscription, CropCalendar, WeatherData,
	AgroAnalytics, SystemSettings, ProductCategory, Product, ProductImage,
	ProductReview, CropListing, Bid, Offer, Order, OrderItem, PriceTrend,
	Wallet, WalletTransaction, Contract, SavingsAccount, SavingsTransaction,
	LoanApplication, LoanRepayment, RepaymentSchedule, CropInsurance,
	InsuranceClaim, ThriftGroup, ThriftMembership, ThriftContribution,
	ThriftPayout, ThriftCycle, ThriftMeeting, ThriftAttendance, ThriftPenalty,
	ThriftLoan, ThriftLoanRepayment, ChatRoom, ChatMessage,
]:
	try:
		admin.site.register(model)
	except AlreadyRegistered:
		# Model was already registered (e.g., due to reloads); ignore to avoid noisy warnings
		pass