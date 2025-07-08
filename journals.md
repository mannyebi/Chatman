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

- I remove avatar uploading at the signup section, because it makes the flow complicated and it's not neccssary at all, we will add it later on upadting profile .

- now I should try to find, why sometimes a wrong otp sends to user's email ? where this happens ? It looks like a hard thing to debug, because a lot of things are envloved.

- it acts so wiered, I can not catch it, it works some times and it doesn't work some time, I'll just let it go for now.

- so I just realized that I don't need any login view, and I can generate login jwt tokens using `api/token/` endpoint.

- now I should work on `forgot password` functionality. it should be sth which is related to email. for example a link or just an otp sends to an email. I think a link with short time expiriation is more user friendly. I'll generate a UID for each user that asks for refreshin password. that UID should be expired after 5 minutes. a post request with `new password` and `confirm new password` should send in less than 5 minutes. and then user's password will refresh and it would send in response. I will create a model for UIDs contains User, UID and expiration time.

- so I wrote one of its views, which creats UID, and email it user.

- now I should validate its UID, by checking its expiration time, and UID content validation. if it was valid, I'll set new password for the user.