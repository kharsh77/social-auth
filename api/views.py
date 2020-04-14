import json, os, hashlib, binascii, re
from api.models import User
from django.core import serializers
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.sessions.models import Session



@require_http_methods(["POST"])
def createUser(request):
	parsedReq = parseRequestBody(request)

	name = getReqParam(parsedReq, 'name')
	email = getReqParam(parsedReq,'email')
	phoneNumber = getReqParam(parsedReq,'phoneNumber')
	password = getReqParam(parsedReq,'password')
	authSource = getReqParam(parsedReq,'authSource')
	authSourceData = getReqParam(parsedReq,'authSourceData')

	# Validating request params
	isError = (False, None)

	isError = validate(name, 'name')
	isError = validate(email, 'email') if not isError[0] else isError
	isError = validate(phoneNumber, 'phoneNumber') if not isError[0] else isError 

	if isError[0]:
		return JsonResponse({"message": isError[1]}, status=400)

	# Handling request when user is created from a social auth
	if authSource:
		error = validateAuthsource(authSource, authSourceData)
		if error[0]:
			return JsonResponse({"message": error[1]}, status=400)

	#  when user is created without using social auth i,e using a phone number
	elif authSource is None and password:
		isError = validate(password, 'password')
		if isError[0]:
			return JsonResponse({"message": isError[1]}, status=400)

	else :
		return JsonResponse({"message": "Insufficient credentials to create user"}, status=400)



	userMeta = {}
	user = None

	try:
		user = User.objects.get(phone_number=phoneNumber)
	except User.DoesNotExist:
		user = None

	if user:
		userMeta = json.loads(user.meta)

		if authSource:
			if authSource in userMeta:
				return JsonResponse({"message": "User already exists with {} account".format(authSource)}, status=400)
			else:
				userMeta[authSource] = authSourceData
				password = user.password

		if authSource is None and password:
			return JsonResponse({"message": "User already exists with this phone number: {}".format(phoneNumber)}, status=400)

		User.objects.filter(id=user.id).update(meta=json.dumps(userMeta), password=password)

	else:

		if authSource:
			userMeta[authSource] = authSourceData
			password = ""

		elif authSource is None and password:
			password = getPasswordHash(password)


		user = User(name=name, email=email, phone_number=phoneNumber,meta=json.dumps(userMeta),password=password)
		user.save()
		

	return JsonResponse({"userId": user.id}, status=200)



@require_http_methods(["GET"])
def listUsers(request):
	data = list(User.objects.values("id", "name", "email", "phone_number"))
	return JsonResponse({'users': data})


@require_http_methods(["GET"])
def getUsers(request, user_id):
	
	validate(user_id, "id")

	resp = None
	status = 200
	try:
		user = User.objects.get(id=user_id)
		resp = {
			"id": user.id,
			"name": user.name,
			"email": user.email,
			"phoneNumber": user.phone_number
		}
	except User.DoesNotExist:
		status= 400
		resp = {
			"error": True,
			"message":"The user doesn't exist"
		}

	return JsonResponse(resp,status=status)


@require_http_methods(["PUT"])
def setPassword(request, user_id):

	parsedReq = parseRequestBody(request)

	old_pwd = getReqParam(parsedReq, 'oldPassword')
	new_pwd = getReqParam(parsedReq, "newPassword")

	validate(user_id, id)
	validate(new_pwd, "password")

	try:
		user = User.objects.get(id=user_id)
		
		if user.password != "" and not matchPasword(user.password, old_pwd):
				return JsonResponse({"message": "Old password is not correct"}, status=400)

		hashedPwd = getPasswordHash(new_pwd)

		User.objects.filter(id=user.id).update(password=hashedPwd)


	except User.DoesNotExist:
		return JsonResponse({"message": "User not found"}, status=400)

	return JsonResponse({"message": "Password reset success"}, status = 200)


@require_http_methods(["GET"])
def searchUsers(request, key):
	validate(key, "search_key")

	users = list(User.objects.filter(phone_number__contains=key).values("id", "name", "email", "phone_number"))
	return JsonResponse({"users": users})


@require_http_methods(["POST"])
def login(request):
	parsedReq = parseRequestBody(request)

	phone_number = getReqParam(parsedReq, 'phoneNumber')
	password = getReqParam(parsedReq, "password")

	m = User.objects.get(phone_number=phone_number)
	if matchPasword(m.password, password):
		request.session['user_id'] = str(m.id)
		return HttpResponse("You're logged in.")
	else:
		return HttpResponse("Your username and password didn't match.")


@require_http_methods(["POST"])
def logout(request):
	parsedReq = parseRequestBody(request)

	user_id = getReqParam(parsedReq, 'userId')

	for s in Session.objects.all():
		if s.get_decoded().get('user_id') == user_id:
			s.delete()

	return HttpResponse("You're logged out.")



# Helper Functions
def getReqParam(obj, key):
	return obj[key] if key in obj else None

def parseRequestBody(request):
	body_unicode = request.body.decode('utf-8')
	return json.loads(body_unicode)


# ref: https://stackoverflow.com/questions/16135069/python-validation-mobile-number
# ref: https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
def validate(toValidateObj, toValidate):
	if toValidateObj is None:
		return (True, "{0} cannot be null".format(toValidate))

	if toValidate == 'name':
		if (len(toValidateObj)<3): return (True, "Name should be of atlest 3 characters")
	elif toValidate == 'email':
		regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
		if (not re.search(regex,toValidateObj)): return (True, "Email is invalid")
	elif toValidate == 'phoneNumber':
		regex = '^(?:\+?\d{2})?[7896]\d{9}$'
		if (not re.search(regex,toValidateObj)): return (True, "Phone number is invalid")
	elif toValidate == 'password':
		if (len(toValidateObj)<3): return (True, "Name should be of atlest 4 characters")
	return (False, None)


def validateAuthsource(authSource, authData):
	if authSource is None or authSource not in ["github","linkedin","twitter"]:
		return (True, "User can only be authenticated by github, linkedin or twitter")
	if authData is None:
		return (True, "authSourceData cannot be empty")

	return (False, None)


# ref: https://www.vitoshacademy.com/hashing-passwords-in-python/
def getPasswordHash(password):
	"""Hash a password for storing."""
	salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
	pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
								salt, 100000)
	pwdhash = binascii.hexlify(pwdhash)
	return (salt + pwdhash).decode('ascii')


def matchPasword(stored_password, provided_password):
	"""Verify a stored password against one provided by user"""
	salt = stored_password[:64]
	stored_password = stored_password[64:]
	pwdhash = hashlib.pbkdf2_hmac('sha512', 
								  provided_password.encode('utf-8'), 
								  salt.encode('ascii'), 
								  100000)
	pwdhash = binascii.hexlify(pwdhash).decode('ascii')
	return pwdhash == stored_password
