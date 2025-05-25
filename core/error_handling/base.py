"""
기본 예외 처리 모듈.

이 모듈은 Antman 프로젝트의 모든 예외 클래스의 기본이 되는
AntmanBaseException 클래스를 정의합니다.
"""


class AntmanBaseException(Exception):
    """
    Antman 프레임워크의 모든 예외에 대한 기본 클래스.
    
    이 클래스는 모든 Antman 관련 예외의 상위 클래스입니다.
    표준 Exception을 상속받아 기본 예외 기능을 확장합니다.
    """
    
    def __init__(self, message="Antman 시스템 오류가 발생했습니다", code=None, *args, **kwargs):
        """
        AntmanBaseException 생성자.
        
        Args:
            message (str): 예외 메시지
            code (str, optional): 예외 코드
            *args: 추가 인자
            **kwargs: 추가 키워드 인자
        """
        self.message = message
        self.code = code
        self.extra_data = kwargs.get('extra_data', {})
        
        # 로깅 및 추적을 위한 추가 속성
        self.request = kwargs.get('request', None)
        self.user = kwargs.get('user', None)
        self.timestamp = kwargs.get('timestamp', None)
        
        super().__init__(message, *args)
    
    def __str__(self):
        """
        예외 객체의 문자열 표현.
        
        Returns:
            str: 예외 메시지
        """
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message
    
    def to_dict(self):
        """
        예외 정보를 사전 형태로 변환.
        
        API 응답이나 로깅에 사용됩니다.
        
        Returns:
            dict: 예외 정보를 담은 사전
        """
        result = {
            'error': True,
            'message': self.message,
        }
        
        if self.code:
            result['code'] = self.code
            
        if self.extra_data:
            result['details'] = self.extra_data
            
        return result
