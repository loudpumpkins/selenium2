from config import *

# external
import pymysql
import random

# internal


class Ad:

	#my ads details
	category_id = None
	description = None
	price = None
	product_id = None
	images = []

	#kijiji details
	ad_description = None
	ad_title = None
	ad_type = None

	#support
	development_flag = False

	#MySQL
	connection = None
	cursor = None

	#SQLite

	'''
	insert rest of inputs
	'''
	def __init__(self):

		self.cursor = pymysql.connect(host=HOST['host'], user=HOST['user'], passwd=HOST['password'], db=HOST['db']).cursor()
		self.product_id = self.get_random_product_id()
		raw_product = self.get_raw_product_data()
		self.category_id = raw_product['category_id']
		self.description = raw_product['description']
		self.price = raw_product['price']
		self.images = self.get_product_images()

		# self.connection.commit()
		self.connection.close()

	def get_raw_product_data(self):
		""" get all the required product details to post """
		self.cursor.execute("SELECT p.model, p.quantity, p.price, pd.description, pc.category_id FROM oc_product p LEFT JOIN oc_product_description pd ON (p.product_id = pd.product_id) LEFT JOIN oc_product_to_store p2s ON (p.product_id = p2s.product_id) LEFT JOIN oc_product_to_category pc ON (p.product_id = pc.product_id) WHERE p.product_id = '" + self.product_id + "' AND pd.language_id = '1' AND p2s.store_id = '0' LIMIT 1;")
		my_product = self.cursor.fetchall()
		data = {
			'model' :       str(my_product[0][0]),
			'quantity' :    str(my_product[0][1]),
			'price' :       str(my_product[0][2]),
			'description' : str(my_product[0][3]),
			'category_id' : str(my_product[0][4]),
		}
		return data

	def get_random_product_id(self):
		""" get a random product ID from all products """
		self.cursor.execute("SELECT product_id FROM oc_product")
		products = self.cursor.fetchall()
		return str(products[random.randint(0, (len(products) - 1))][0])

	def get_product_images(self):
		self.cursor.execute("SELECT image FROM oc_product_image WHERE product_id='"+ self.product_id +"'")
		images = self.cursor.fetchall()
		data = []
		for image in images:
			data.append(image[0])
		return data