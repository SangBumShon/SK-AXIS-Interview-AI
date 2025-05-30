package com.example.skaxis.user.repository;

import com.example.skaxis.user.model.User;
import org.springframework.stereotype.Repository;
import org.springframework.data.jpa.repository.JpaRepository;

@Repository
public interface UserRepository extends JpaRepository<User, String> {
    User findByUserName(String userName);
}