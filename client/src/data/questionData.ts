export interface Question {
  id: string;
  content: string;
  type: 'common' | 'individual';
}

// 공통 질문 (모든 지원자에게 동일하게 적용)
export const commonQuestions: Question[] = [
  {
    id: 'cq1',
    content: '자신의 장점과 단점에 대해 설명해주세요.',
    type: 'common'
  },
  {
    id: 'cq2',
    content: '지원동기는 무엇인가요?',
    type: 'common'
  },
  {
    id: 'cq3',
    content: '향후 5년 후의 목표는 무엇인가요?',
    type: 'common'
  }
];

// 개별 질문 (지원자별로 다른 질문)
export const individualQuestions: Record<string, Question[]> = {
  'c1': [ // 홍길동
    {
      id: 'iq1-1',
      content: '프로젝트에서 리더십을 발휘한 경험이 있다면 말씀해주세요.',
      type: 'individual'
    },
    {
      id: 'iq1-2',
      content: '실패했던 경험과 그로부터 배운 점은 무엇인가요?',
      type: 'individual'
    }
  ],
  'c2': [ // 김철수
    {
      id: 'iq2-1',
      content: '팀 프로젝트에서 갈등을 해결한 경험이 있나요?',
      type: 'individual'
    },
    {
      id: 'iq2-2',
      content: '새로운 기술을 배울 때 어떤 방식으로 접근하시나요?',
      type: 'individual'
    }
  ],
  'c3': [ // 이영희
    {
      id: 'iq3-1',
      content: '업무 중 가장 큰 도전을 극복한 경험은 무엇인가요?',
      type: 'individual'
    },
    {
      id: 'iq3-2',
      content: '스트레스 상황에서 어떻게 대처하시나요?',
      type: 'individual'
    }
  ],
  'c4': [ // 박지성
    {
      id: 'iq4-1',
      content: '본인의 커리어 목표는 무엇인가요?',
      type: 'individual'
    },
    {
      id: 'iq4-2',
      content: '우리 회사에 대해 어떤 점을 알고 계신가요?',
      type: 'individual'
    }
  ],
  'c5': [ // 최지원
    {
      id: 'iq5-1',
      content: '본인의 강점을 업무에 어떻게 활용할 수 있을까요?',
      type: 'individual'
    },
    {
      id: 'iq5-2',
      content: '업무와 관련하여 가장 자신 있는 분야는 무엇인가요?',
      type: 'individual'
    }
  ],
  'c6': [ // 최민수
    {
      id: 'iq6-1',
      content: '팀워크가 중요한 이유는 무엇이라고 생각하시나요?',
      type: 'individual'
    },
    {
      id: 'iq6-2',
      content: '본인의 업무 스타일은 어떤 것인가요?',
      type: 'individual'
    }
  ],
  'c7': [ // 정다은
    {
      id: 'iq7-1',
      content: '업무 중 가장 중요하게 생각하는 가치는 무엇인가요?',
      type: 'individual'
    },
    {
      id: 'iq7-2',
      content: '본인의 약점을 보완하기 위해 어떤 노력을 하고 있나요?',
      type: 'individual'
    }
  ],
  'c8': [ // 김지원
    {
      id: 'iq8-1',
      content: '업무 중 가장 큰 성취감을 느낀 경험은 무엇인가요?',
      type: 'individual'
    },
    {
      id: 'iq8-2',
      content: '본인의 전문성을 키우기 위해 어떤 노력을 하고 있나요?',
      type: 'individual'
    }
  ],
  'c9': [ // 이수진
    {
      id: 'iq9-1',
      content: '업무 중 가장 어려웠던 결정은 무엇이었나요?',
      type: 'individual'
    },
    {
      id: 'iq9-2',
      content: '본인의 업무 방식이 팀에 어떤 기여를 할 수 있을까요?',
      type: 'individual'
    }
  ]
};

// 지원자별 전체 질문 목록을 가져오는 함수
export const getQuestionsForCandidate = (candidateId: number): Question[] => {
  if (candidateId === undefined || candidateId === null) {
    console.warn('candidateId가 undefined 또는 null입니다. 기본 질문만 반환합니다.');
    return [...commonQuestions];
  }
  const candidateQuestions = individualQuestions[candidateId.toString()] || [];
  return [...commonQuestions, ...candidateQuestions];
}; 