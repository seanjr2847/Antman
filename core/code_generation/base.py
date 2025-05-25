"""
코드 생성 기본 모듈.

이 모듈은 Antman 프로젝트의 코드 생성 도구를 위한 기본 클래스를 제공합니다.
다양한 코드 생성기가 이 기본 클래스를 상속받아 구현됩니다.
"""

import os
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseGenerator(ABC):
    """
    모든 코드 생성기의 기본 클래스.
    
    이 추상 클래스는 코드 생성을 위한 공통 인터페이스와 유틸리티 메서드를 제공합니다.
    모든 특정 생성기 클래스(예: 모델, 뷰, 시리얼라이저)는 이 클래스를 상속받아 구현합니다.
    """
    
    def __init__(self, config=None):
        """
        BaseGenerator 생성자.
        
        Args:
            config (dict, optional): 생성기 구성 옵션을 포함하는 사전
        """
        self.config = config or {}
        self._validate_config()
        self.output_dir = self.config.get('output_dir', '')
        self.indent = self.config.get('indent', 4)
        self.encoding = self.config.get('encoding', 'utf-8')
        
        # 로깅 설정
        self.verbose = self.config.get('verbose', False)
        
    def _validate_config(self):
        """
        구성 옵션의 유효성을 검사합니다.
        
        각 하위 클래스는 이 메서드를 재정의하여 구체적인 검증을 구현할 수 있습니다.
        
        Raises:
            ValueError: 구성이 유효하지 않은 경우
        """
        # 기본 검증 로직
        if not isinstance(self.config, dict):
            raise ValueError("구성은 사전 형태여야 합니다")
            
        # 출력 디렉토리가 지정된 경우 해당 디렉토리가 존재하는지 확인
        output_dir = self.config.get('output_dir')
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"출력 디렉토리 생성됨: {output_dir}")
    
    @abstractmethod
    def generate(self):
        """
        코드를 생성합니다.
        
        이 메서드는 모든 하위 클래스에서 구현해야 합니다.
        생성된 코드를 문자열로 반환합니다.
        
        Returns:
            str: 생성된 코드
        """
        pass
    
    def save(self, content, filename=None):
        """
        생성된 코드를 파일로 저장합니다.
        
        Args:
            content (str): 저장할 코드 내용
            filename (str, optional): 저장할 파일 이름
                                     지정되지 않은 경우 구성에서 가져옵니다.
        
        Returns:
            str: 저장된 파일의 전체 경로
        """
        if not filename:
            filename = self.config.get('filename')
            if not filename:
                raise ValueError("파일 이름이 지정되지 않았습니다")
        
        # 출력 디렉토리가 있는 경우 경로 결합
        if self.output_dir:
            filepath = os.path.join(self.output_dir, filename)
        else:
            filepath = filename
            
        # 디렉토리가 존재하는지 확인
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            
        # 파일 저장
        with open(filepath, 'w', encoding=self.encoding) as f:
            f.write(content)
            
        if self.verbose:
            logger.info(f"파일이 저장됨: {filepath}")
            
        return filepath
    
    def generate_and_save(self, filename=None):
        """
        코드를 생성하고 저장하는 편의 메서드.
        
        Args:
            filename (str, optional): 저장할 파일 이름
        
        Returns:
            tuple: (생성된 코드 내용, 저장된 파일 경로)
        """
        content = self.generate()
        filepath = self.save(content, filename)
        return content, filepath
