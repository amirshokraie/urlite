from rest_framework.generics import (
    CreateAPIView, 
    UpdateAPIView, 
    RetrieveAPIView,
)
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    UserRegisterSerializer,
    UserRetrieveSerializer,
    PasswordChangeSerializer
)
from .models import User


class UserRegisterAPIView(CreateAPIView):
    serializer_class = UserRegisterSerializer
    

class UserRetrieveAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = UserRetrieveSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user


class PasswordChangeAPIView(UpdateAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = PasswordChangeSerializer
