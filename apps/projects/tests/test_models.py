"""
프로젝트 모델 테스트
"""
import pytest
from django.test import TestCase
from apps.projects.factories import ProjectFactory, ProjectUserFactory
from apps.users.factories import UserFactory

# 참고: 실제 Project 모델이 구현되면 import 문을 업데이트해야 합니다.
# from apps.projects.models import Project, ProjectUser

class ProjectModelTest(TestCase):
    """프로젝트 모델 테스트 클래스"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        # 아직 Project 모델이 구현되지 않았으므로 스킵
        self.skipTest("Project 모델이 아직 구현되지 않았습니다.")
        
        # 모델이 구현되면 아래와 같이 테스트 데이터를 설정
        # self.project = ProjectFactory.create(
        #     name='테스트 프로젝트',
        #     description='테스트 프로젝트 설명'
        # )
        # self.user = UserFactory.create()
        # self.project_user = ProjectUserFactory.create(
        #     project=self.project,
        #     user=self.user,
        #     role='admin'
        # )
    
    def test_project_creation(self):
        """프로젝트 생성 테스트"""
        # 아직 Project 모델이 구현되지 않았으므로 스킵
        self.skipTest("Project 모델이 아직 구현되지 않았습니다.")
        
        # 모델이 구현되면 아래와 같이 테스트
        # self.assertEqual(self.project.name, '테스트 프로젝트')
        # self.assertEqual(self.project.description, '테스트 프로젝트 설명')
        # self.assertIsNotNone(self.project.created_at)
        # self.assertIsNotNone(self.project.updated_at)
    
    def test_project_user_relation(self):
        """프로젝트-사용자 관계 테스트"""
        # 아직 Project 모델이 구현되지 않았으므로 스킵
        self.skipTest("Project 모델이 아직 구현되지 않았습니다.")
        
        # 모델이 구현되면 아래와 같이 테스트
        # self.assertEqual(self.project_user.project, self.project)
        # self.assertEqual(self.project_user.user, self.user)
        # self.assertEqual(self.project_user.role, 'admin')


@pytest.mark.django_db
class ProjectModelPytestTest:
    """pytest를 사용한 프로젝트 모델 테스트 클래스"""
    
    def test_project_factory(self, db):
        """ProjectFactory 테스트"""
        # 아직 Project 모델이 구현되지 않았으므로 스킵
        pytest.skip("Project 모델이 아직 구현되지 않았습니다.")
        
        # 모델이 구현되면 아래와 같이 테스트
        # project = ProjectFactory.create()
        # assert Project.objects.filter(id=project.id).exists()
    
    def test_project_user_factory(self, db):
        """ProjectUserFactory 테스트"""
        # 아직 ProjectUser 모델이 구현되지 않았으므로 스킵
        pytest.skip("ProjectUser 모델이 아직 구현되지 않았습니다.")
        
        # 모델이 구현되면 아래와 같이 테스트
        # project_user = ProjectUserFactory.create()
        # assert ProjectUser.objects.filter(id=project_user.id).exists()
