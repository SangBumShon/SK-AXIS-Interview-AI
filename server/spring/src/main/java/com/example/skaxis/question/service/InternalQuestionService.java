package com.example.skaxis.question.service;

import com.example.skaxis.interview.model.Interview;
import com.example.skaxis.interview.model.Interviewee;
import com.example.skaxis.interview.model.InterviewInterviewee;
import com.example.skaxis.interview.repository.InterviewIntervieweeRepository;
import com.example.skaxis.question.model.Question;
import com.example.skaxis.question.repository.QuestionRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class InternalQuestionService {

    private final QuestionRepository questionRepository;
    private final InterviewIntervieweeRepository interviewIntervieweeRepository;

    @Autowired
    public InternalQuestionService(QuestionRepository questionRepository,
                                  InterviewIntervieweeRepository interviewIntervieweeRepository) {
        this.questionRepository = questionRepository;
        this.interviewIntervieweeRepository = interviewIntervieweeRepository;
    }

    /**
     * 여러 면접자 ID를 받아 각 면접자별로 질문 5개(공통 3 + 개별 2)를 조회
     * @param intervieweeIds 면접자 ID 목록
     * @return 면접자 ID별 질문 목록 Map
     */
    public Map<String, List<Question>> getQuestionsForMultipleInterviewees(List<Long> intervieweeIds) {
        Map<String, List<Question>> questionsPerInterviewee = new HashMap<>();
        
        for (Long intervieweeId : intervieweeIds) {
            // 면접자의 면접 세션 조회
            List<InterviewInterviewee> interviewInterviewees = interviewIntervieweeRepository.findByIntervieweeId(intervieweeId);
            
            if (interviewInterviewees.isEmpty()) {
                continue; // 면접 세션이 없으면 건너뜀
            }
            
            // 가장 최근 면접 세션 선택 (여러 면접이 있을 경우)
            InterviewInterviewee interviewInterviewee = interviewInterviewees.stream()
                    .sorted((a, b) -> b.getCreatedAt().compareTo(a.getCreatedAt()))
                    .findFirst()
                    .orElse(null);
            
            if (interviewInterviewee == null) {
                continue;
            }
            
            Long interviewId = interviewInterviewee.getInterviewId();
            
            // 공통 질문 3개 조회
            List<Question> commonQuestions = questionRepository.findByInterviewIdAndType(interviewId, "공통질문");
            if (commonQuestions.size() > 3) {
                commonQuestions = commonQuestions.subList(0, 3);
            }
            
            // 개별 질문 2개 조회
            List<Question> individualQuestions = questionRepository.findByInterviewIdAndType(interviewId, "개별질문");
            if (individualQuestions.size() > 2) {
                individualQuestions = individualQuestions.subList(0, 2);
            }
            
            // 질문 5개 합치기
            List<Question> allQuestions = new ArrayList<>();
            allQuestions.addAll(commonQuestions);
            allQuestions.addAll(individualQuestions);
            
            // 결과 맵에 추가
            questionsPerInterviewee.put(String.valueOf(intervieweeId), allQuestions);
        }
        
        return questionsPerInterviewee;
    }
}
