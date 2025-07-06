# journaling

- today is 1404/04/15 I've started to code this project again, I'm working on the first functions of `accounts` application.
- one hour have been passed, and I've debugged the first two functions. and now I should do these tests on them:
    1- creating a simple user with firstname, lastname, and all credentials [x]
    2- recreating a user with a duplicated username but different email [x]
    3- recreating a user with a duplicated email but different username [x]
    4- uploading a avatar image [x]


- So we want to prevent users to create accounts with repeated email and username. it means that email and usernames should be unique.so we must catch this at the first view which user tries to create an account. also catching it at the second view will increase the safety.

- I just solved the above problem.

- I faced another problem, which is that some times, the emailed OTP is invalid, there must be a problem somewhere, so I'll go to catch it now.