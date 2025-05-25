"""
프로젝트 앱을 위한 Factory 클래스 모음
"""
import factory
from faker import Faker
from django.utils import timezone
from apps.users.factories import UserFactory

fake = Faker('ko_KR')  # 한국어 로케일 사용

class ProjectFactory(factory.django.DjangoModelFactory):
    """
    프로젝트 모델을 위한 팩토리 클래스
    
    참고: 실제 Project 모델이 구현되면 이 팩토리를 업데이트해야 합니다.
    """
    
    class Meta:
        model = 'projects.Project'  # 아직 모델이 없으므로 문자열로 지정
    
    name = factory.LazyFunction(lambda: fake.company() + ' 프로젝트')
    description = factory.LazyFunction(fake.paragraph)
    git_repository_url = factory.LazyFunction(lambda: f'https://gitlab.example.com/{fake.word()}/{fake.word()}.git')
    database_connection_string = factory.LazyFunction(lambda: f'postgresql://{fake.user_name()}:{fake.password()}@db:5432/{fake.word()}')
    web_id = factory.LazyFunction(fake.user_name)
    web_password = factory.LazyFunction(fake.password)
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)
    
class ProjectUserFactory(factory.django.DjangoModelFactory):
    """
    프로젝트-사용자 매핑 모델을 위한 팩토리 클래스
    
    참고: 실제 ProjectUser 모델이 구현되면 이 팩토리를 업데이트해야 합니다.
    """
    
    class Meta:
        model = 'projects.ProjectUser'  # 아직 모델이 없으므로 문자열로 지정
    
    project = factory.SubFactory(ProjectFactory)
    user = factory.SubFactory(UserFactory)
    role = factory.LazyFunction(lambda: fake.random_element(elements=('admin', 'member', 'viewer')))
    created_at = factory.LazyFunction(timezone.now)
