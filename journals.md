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
  - [x] add `participents` field to `ChatRoom` model in `chat` app, and implement its related functionality. in both `connect` and `receieve_json` check if user a participant.
  - [x] add rate limit to sending messages.
  - [ ] learn and then implement about sending files, musics, images and so on.
  - [ ] work on `group chat` functionality and its related rules.

- it seems like I should get the file byte from client (front end should recieve the main file, convert it to bytes, and the send it to backend), then convert that bytes content into a file with its true extension. then save that file in an appropriate directory inside `media` folder.

- I just created its model, now I should handle media configurations.

- I did it.

- So now I should start recieving the json from websocket and make the consumer ready to accept it.

- as I see, I need to add some error handling to project.

- WHHHHAT A HARD TASK, I finally found a way to add the upload file/files feature, and implent a part of it. this is the flow : Files should be upload on the server by and http endpoing, and after that, the pk of the uploaded file will return. then the frontend send it to backend, backend will recieve it and set that file/files in `Message` obj. I know it looks confusing, but its interesting.

- tomorrow tasks : 
  - [x] add `file.message` handler
  - [x] add `Upload_File` http endpoint

- I successfuly added upload file endpoint, and completed the `file.message` handler.

- I am so happy that my chat functionality is almost complete 😍.
- Now users should be able to send money through chat to each other 🔥. I really believe that this functionality is really cool.
- also I should add `typing` handler, so if someone started typing, everyone in the chatroom can realize.
- the other important thing is `creating group` functionality. this feature has even more features in it also. each group should has some settings also, like profile picture, bio, others can chat or not (if not, it would be a channel).
- so tomorrow tasks will be :
  - [ ] add `typing` handler.
  - [ ] add `money transfering` functionality in chat.
  - [ ] start learning a frontend technology.