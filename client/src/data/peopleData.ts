export interface Person {
  id: string;
  name: string;
  role: 'interviewer' | 'candidate';
}

export const people: Person[] = [
  // 면접관
  { id: 'i1', name: '김면접', role: 'interviewer' },
  { id: 'i2', name: '이면접', role: 'interviewer' },
  { id: 'i3', name: '박면접', role: 'interviewer' },
  { id: 'i4', name: '최면접', role: 'interviewer' },
  { id: 'i5', name: '정면접', role: 'interviewer' },
  { id: 'i6', name: '강면접', role: 'interviewer' },
  { id: 'i7', name: '윤면접', role: 'interviewer' },
  { id: 'i8', name: '한면접', role: 'interviewer' },
  { id: 'i9', name: '최면접', role: 'interviewer' },

  // 지원자
  { id: 'c1', name: '홍길동', role: 'candidate' },
  { id: 'c2', name: '김철수', role: 'candidate' },
  { id: 'c3', name: '이영희', role: 'candidate' },
  { id: 'c4', name: '박지성', role: 'candidate' },
  { id: 'c5', name: '최지원', role: 'candidate' },
  { id: 'c6', name: '최민수', role: 'candidate' },
  { id: 'c7', name: '정다은', role: 'candidate' },
  { id: 'c8', name: '김지원', role: 'candidate' },
  { id: 'c9', name: '이수진', role: 'candidate' }
];

export const getInterviewers = () => people.filter(p => p.role === 'interviewer');
export const getCandidates = () => people.filter(p => p.role === 'candidate');

export const getPersonById = (id: string) => people.find(p => p.id === id);
export const getPersonByName = (name: string) => people.find(p => p.name === name); 