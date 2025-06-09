export interface Room {
  id: string;
  name: string;
}

export interface TimeSlot {
  id: string;
  roomId: string;
  date: string;  // YYYY-MM-DD 형식의 날짜
  timeRange: string;
  interviewerIds: string[];
  candidateIds: string[];
}

export interface Person {
  id: string;
  name: string;
  role: 'interviewer' | 'candidate';
}

export const rooms: Room[] = [
  { id: 'room1', name: '면접실 1' },
  { id: 'room2', name: '면접실 2' },
  { id: 'room3', name: '면접실 3' }
];

export const timeSlots: TimeSlot[] = [
  {
    id: 'ts1',
    roomId: 'room1',
    date: '2025-06-04',
    timeRange: '09:00 - 10:00',
    interviewerIds: ['i1', 'i2', 'i3'],
    candidateIds: ['c1']
  },
  {
    id: 'ts2',
    roomId: 'room1',
    date: '2025-06-05',
    timeRange: '10:30 - 11:30',
    interviewerIds: ['i1', 'i2', 'i3'],
    candidateIds: ['c2', 'c3']
  },
  {
    id: 'ts3',
    roomId: 'room2',
    date: '2025-06-05',
    timeRange: '09:00 - 10:00',
    interviewerIds: ['i1', 'i2', 'i3'],
    candidateIds: ['c4']
  },
  {
    id: 'ts4',
    roomId: 'room2',
    date: '2025-06-05',
    timeRange: '10:30 - 11:30',
    interviewerIds: ['i1', 'i2', 'i3'],
    candidateIds: ['c5', 'c6']
  },
  {
    id: 'ts5',
    roomId: 'room1',
    date: '2025-06-05',
    timeRange: '09:00 - 10:00',
    interviewerIds: ['i1', 'i2', 'i3'],
    candidateIds: ['c7']
  },
  {
    id: 'ts6',
    roomId: 'room2',
    date: '2025-06-05',
    timeRange: '10:30 - 11:30',
    interviewerIds: ['i1', 'i2', 'i3'],
    candidateIds: ['c8', 'c9']
  },
  {
    id: 'ts7',
    roomId: 'room3',
    date: '2025-06-05',
    timeRange: '09:00 - 10:00',
    interviewerIds: ['i4', 'i5', 'i6'],
    candidateIds: ['c1', 'c2']
  },
  {
    id: 'ts8',
    roomId: 'room3',
    date: '2025-06-05',
    timeRange: '10:30 - 11:30',
    interviewerIds: ['i4', 'i5', 'i6'],
    candidateIds: ['c3', 'c4']
  },
  {
    id: 'ts9',
    roomId: 'room3',
    date: '2025-06-05',
    timeRange: '09:00 - 10:00',
    interviewerIds: ['i4', 'i5', 'i6'],
    candidateIds: ['c5', 'c6']
  },
  {
    id: 'ts10',
    roomId: 'room3',
    date: '2025-06-05',
    timeRange: '10:30 - 11:30',
    interviewerIds: ['i4', 'i5', 'i6'],
    candidateIds: ['c7', 'c8', 'c9']
  }
];

export const people: Person[] = [
  { id: 'i1', name: '김면접', role: 'interviewer' },
  { id: 'i2', name: '이평가', role: 'interviewer' },
  { id: 'i3', name: '박관리', role: 'interviewer' },
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

export const getPersonById = (id: string): Person | undefined => {
  return people.find(person => person.id === id);
}; 