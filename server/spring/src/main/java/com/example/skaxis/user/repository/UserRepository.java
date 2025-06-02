package com.example.skaxis.user.repository;

import com.example.skaxis.user.model.User;
import org.springframework.stereotype.Repository;
import org.springframework.data.jpa.repository.JpaRepository;
import com.example.skaxis.user.Role;
import java.util.List;


@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    User findByUserName(String userName);
    List<User> findByUserType(Role userType);
}