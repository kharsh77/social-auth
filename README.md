# Social Auth

A social login webapp for login via Github , linkedin and Twitter.


## Notes

- User can be created after authentication from social login providers
- User can also be created using phone number and password
- For user created using social auth, password is empty string. Which can be resetted later.
- Db used: sqLite


phonenumber supported values;
- '+919876543210'
- '9876543210'


Django admin credentials:
- username= 'admin'
- password= 'password'


Apis
=======
```````

* CreateUser
``````````````
	POST /user

	{
		"name": "haw",
		"email": "haw@gmail.com",
		"phoneNumber": "9876543210",
		"password": "qwerty"        // Optional: When user to be created using only phonenumber. 'authSource' field should not be there in request.
		"authSource": "github",		// Optional: Possible values- github/linkedin/twitter. 'authSourceData' field mandatory
		"authSourceData":"data1"    // Optional	
	}

* GetUser
````````````
	GET /user/<user_id>

* ListUsers
````````````
	GET /user/all

* SearchUsers (Search user based on phone number)
``````````````````````````````````````````````````
	GET /user/<query_string>

* ResetPassword
````````````````
	PUT /user/setpassword/<user_id>

	{
		"oldPassword": "qwerty", // Should be empty string if user created using social auth for the first time
		"newPassword": "asdfgj"
	}

* Login
````````
	GET /login

	{
		"phoneNumber": "9876543210",
		"password": "qwerty"
	}

* Logout
`````````
	GET /logout

	{
		"userId": "9"
	}


