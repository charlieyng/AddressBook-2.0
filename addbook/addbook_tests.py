import addbook
import unittest
import json

class addbookTestCase(unittest.TestCase):

	def setUp(self):
		addbook.app.testing = True
		self.app = addbook.app.test_client()
		
	def test_getFail(self):
		rv = self.app.get('/contact/Pickle', follow_redirects = True)
		assert b'No contact with that name found' in rv.data

	def test_post(self):
		rv = self.app.post('/contact', data = "{ 'name' : 'Harley', 'phonenumber' : 228123812 }", follow_redirects = True)
		assert b'Contact Added' in rv.data

	def test_getSuccess(self):
		rv = self.app.get('/contact/Harley', follow_redirects = True)
		assert b'No contact with that name found' not in rv.data


	def test_postDuplicate(self):
		rv = self.app.post('/contact', data = "{ 'name' : 'Harley'}", follow_redirects = True)
		assert b'Error: Contact with that name already exists!' in rv.data

	def test_put(self):
		rv = self.app.put('/contact/Harley', data = "{ 'name' : 'Melon', 'phonenumber' : 884838844 }", follow_redirects = True)
		assert b'Contact Updated' in rv.data

	def test_delete(self):
		rv = self.app.delete('/contact/Melon', follow_redirects = True)
		assert b'Contact Deleted' in rv.data

	def test_list(self):
		rv = self.app.get('/contact?pageSize=6&page=0&query={"query": {"match_all": {}}}', follow_redirects = True)


if __name__ == '__main__':
	unittest.main()