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
- Update profile is a page that user can change this things : firstname, lastname, bio, avatar, (username, later).
- So I just add update account functionality, what else I should add in Accounts app ? signup, reset password, update account are done. probabbly thats enough for now, I'll just go to the other app, which is `Wallet`. and if another thing was required, I'll just add it to accoutns app.
- Users should be able to store credit on this platform, they should also be able to transmit money to eachother. donate links should be available also.
- I'll just start with creating The app.
- now I'll create its first model which is `wallet` it has these fields : 1-User 2-Balance 3-udpated_at
- I made the wallet, and an implementation for creating `wallet` record at the same time that the `user` record creats.
- I found a bug in `UpadteAccountView` which I wasn't even using the validated data by serializer, this also fixed.
- I added `Deposit` and `Transaction` but a little bit dirty. tomorrow will be cleanup day, try to cleanup the whole codes that you wrote.
- I add a handler on serializers.py inside `accounts` app to delete expired tokens when user asks for confirm reset password. this is not enough, and I should use celery or cron later.
- I refactored `DepositView` and `TransferView` .
- so what else should be in `wallet` application ? probably payment with crypto ? to deposit their wallet. also creating Donate links are required. Donate links are kind of the same thing as transfer. it just have a sender and reciever and a expiration time. so we may create separate model and view for it, but we also use the transfer view too.
- the `Donate link` functionality is available now. users can go an create their own donate link. on the UI, it will be a modal which shows the reciever and the price which user choose to pay.
- now Its time to start the `Chat` app. just dive deep into it.
- so I just finished the whole chat functionality. I've grasped a greate understanding of websocket and its requirements.
- I also learned about middlewares. I wrote one, it was a very fun experience. 
- now I just need to add some endpoints, the one that Im sure is required for now is `creating-room-for-chat` .
- after that I need to add a lot of features to the chat functionality, like sending files, images, musics, creating groups and so on.
- also the `group` functionality requires some other features like admin, owner, different access levels.
- the normal one-to-one chat is also required some other features, like blocking. 
- I guess that `ChatRoom` model in the `chat` app requires to add one more field called `participents` . so just the ones that are a part of the group can join to its channel layer and recieve its messages (even if they are authenticated.)
- base on all, these might be my new tasks for few days :
  - [ ] add `participents` field to `ChatRoom` model in `chat` app, and implement its related functionality .
  - [ ] learn and then implement about sending files, musics, images and so on.
  - [ ] work on `group chat` functionality and its related rules.