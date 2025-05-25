from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    커스텀 사용자 모델
    
    Django의 AbstractUser를 상속하여 확장한 사용자 모델입니다.
    현재는 기본 필드만 사용하지만, 필요에 따라 필드를 추가할 수 있습니다.
    """
    
    class Meta:
        verbose_name = _('사용자')
        verbose_name_plural = _('사용자들')
        
    def __str__(self):
        return self.username
