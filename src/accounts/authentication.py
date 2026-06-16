from rest_framework_simplejwt.authentication import JWTAuthentication

class JWTCookiesAuthentication(JWTAuthentication) :
    
	def authenticate(self, request):
		raw_token = request.COOKIES.get('access')
		if not raw_token :
			return None
		token = self.get_validated_token(raw_token)
		return self.get_user(token), token
	

    
