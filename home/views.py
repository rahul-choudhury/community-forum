from unicodedata import category
from django.shortcuts import render, redirect
from home.models import Answers, Students, Teachers, Quentions
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime

from home.utils import *
from home.reaction import giveReaction

from django.core.files.storage import FileSystemStorage


def index(request):
    try:
        branch = request.GET.get("cat")
        if branch == None:
            allQuestions = Quentions.objects.all().order_by('dateTimeOfPost').reverse()
        else:
            allQuestions = Quentions.objects.filter(
                category=branch).all().order_by('dateTimeOfPost').reverse()
        sendDict = {}
        if len(allQuestions) == 0:
            sendDict["nothing"] = True
            return render(request, "index.html", sendDict)
        nameList = []
        voteList = []
        for item in allQuestions:
            if item.byStudent:
                user = Students.objects.filter(sID=item.uID).first()
            else:
                user = Teachers.objects.filter(tID=item.uID).first()
            voteList.append(item.likeCount-item.disLikeCount)
            nameList.append(user.name)
        sendDict = {
            "post": allQuestions,
            "postNameMix": zip(allQuestions, nameList, voteList),
        }
        return render(request, "index.html", sendDict)
    except:
        return render(request, "index.html")


def loginSignup(request):
    if request.session.get("log"):
        return redirect(index)
    return render(request, "loginSignup.html")


def signup(request):
    if request.method == "POST":
        userType = request.POST.get("acc-type")
        name = request.POST.get("name")
        password = request.POST.get("password")
        conPassword = request.POST.get("conPassword")
        branch = request.POST.get("branch")
        uId = request.POST.get("mail")
        regNumber = uId.split("@")[0]
        newUser = isNewUser(regNumber, True) if userType == "student" else isNewUser(
            uId, False)
        if not newUser:
            return alert(request, False, "You are already registered", "Login with your credentials", "/loginSignup")
        if password == conPassword:
            if userType == "student":
                newStudent = Students(
                    name=name, regNumber=regNumber, password=make_password(password+generateSalt(uId)), branch=branch, dateTimeOfJoin=datetime.now())
                newStudent.save()
                return alert(request, True, "Your account is created", "Now you can login", "/")
            newTeacher = Teachers(name=name, mailId=uId,
                                  password=make_password(password+generateSalt(uId)), branch="CSE", dateTimeOfJoin=datetime.now())
            newTeacher.save()
            return alert(request, True, "Your account is created", "Now you can login", "/")
        return alert(request, False, "Error", "Password not confirm password not matched.", "/")
    return redirect(index)


def userLogin(request, isStudent, uId, password):
    if isStudent:
        user = Students.objects.filter(regNumber=uId).first()
    else:
        user = Teachers.objects.filter(mailId=uId).first()
    if user is None:
        return alert(request, False, "Signup first", "Create an account to continue", "/")
    if check_password(password, user.password):
        request.session['log'] = True
        if isStudent:
            request.session['uId'] = str(user.sID)
        else:
            request.session['uId'] = str(user.tID)
        request.session['name'] = user.name
        request.session['isStudent'] = isStudent
        return redirect(index)
    return alert(request, False, "Password not matched", "", "/")


def login(request):
    if request.method == "POST":
        userType = request.POST.get("acc-type")
        password = request.POST.get("password")
        mail = request.POST.get("mail")
        isStudent = True if userType == "student" else False
        return userLogin(request, isStudent, mail, password+generateSalt(mail))
    return redirect(index)


def logout(request):
    del request.session['log']
    del request.session['uId']
    del request.session['name']
    del request.session['isStudent']
    return redirect(index)


def postQuestion(request):
    if request.session.get("log"):
        userID = request.session.get("uId")
        isStudent = request.session.get("isStudent")

        # check is user verified or not
        if not isUserVerified(request):
            return alert(request, False, "You are not verified", "Go to profile & verify your account", "/profile")

        type = "new"
        if request.method == "POST":
            title = request.POST.get("title")
            about = request.POST.get("about")
            type = request.POST.get("type")
            isImage = request.POST.get("isImage")
            branch = request.POST.get("branch")

            # handel new post
            if type == "new":
                new = Quentions(title=title, about=about, uID=userID,
                                byStudent=isStudent, dateTimeOfPost=datetime.now(), category=branch)
                new.save()
                if isImage == None:
                    return alert(request, True, "Post added", "You can also edit the post", f"/postView/{new.qID}")
                postImage = request.FILES['postImage']
                fs = FileSystemStorage()
                nameList = postImage.name.split(".")
                imageName = str(new.qID)+"."+nameList[len(nameList)-1]
                fs.save(f"static/postImages/{imageName}", postImage)
                return alert(request, True, "Post Added", "Post Saved with image", f"/postView/{new.qID}")
            else:
                # handel update part
                id = request.POST.get("id")
                postObject = Quentions.objects.filter(qID=id).first()
                if postObject.uID == request.session.get("uId"):
                    postObject.title = title
                    postObject.about = about
                    postObject.save()
                    return alert(request, True, "Post updated", "Wait for others response.", "/postImage")
                else:
                    return alert(request, False, "Sorry", "You are not allowed to edit this", "/")
        sendDict = {
            "type": type,
            "buttonName": "Post"
        }
        return render(request, "postQuestion.html", sendDict)
    return redirect(loginSignup)


def editPost(request, slug):
    postObject = Quentions.objects.filter(qID=slug).first()
    sendDict = {
        "type": "edit",
        "buttonName": "Update",
        "id": slug,
        "title": postObject.title,
        "about": postObject.about,
        "isEdit": True,
    }
    return render(request, "postQuestion.html", sendDict)


def postComment(request):
    if request.session.get("log"):

        # check is user verified or not
        if not isUserVerified(request):
            return alert(request, False, "You are not verified", "Go to profile & verify your account", "/profile")

        if request.method == "POST":
            about = request.POST.get("about")
            qID = request.POST.get("qID")
            isStudent = request.session.get("isStudent")
            uID = request.session.get("uId")
            newComment = Answers(
                uID=uID, qID=qID, byStudent=isStudent, ans=about, dateTimeOfPost=datetime.now())
            newComment.save()
            questionObject = Quentions.objects.filter(qID=qID).first()
            questionObject.comments += 1
            questionObject.save()
            return alert(request, True, "Added !", "", f"/postView/{qID}")
        return alert(request, False, "Not allowed", "Go to the post & try to comment", "/")
    return alert(request, False, "Sorry", "Login to comment", "/")


def profile(request):
    if request.session.get("log"):
        if request.session.get("isStudent"):
            user = Students.objects.filter(
                sID=request.session.get("uId")).first()
        else:
            user = Teachers.objects.filter(
                tID=request.session.get("uId")).first()

        # count post
        totalPost = Quentions.objects.filter(
            uID=request.session.get("uId")).all()
        totalComment = Answers.objects.filter(
            uID=request.session.get("uId")).all()
        userData = {
            "user": user,
            "post": totalPost,
            "postCount": len(totalPost),
            "commentCount": len(totalComment),
        }
        return render(request, "profile.html", userData)
    return redirect(index)


def postView(request, slug):
    post = Quentions.objects.filter(qID=slug).first()
    if post.byStudent:
        user = Students.objects.filter(sID=post.uID).first()
    else:
        user = Teachers.objects.filter(tID=post.uID).first()

    #  get comments & filter
    comments = Answers.objects.filter(qID=slug).all()
    commentUsers = []
    isCorrectAnswer = []
    for item in comments:
        if item.byStudent:
            cUser = Students.objects.filter(sID=item.uID).first()
        else:
            cUser = Teachers.objects.filter(tID=item.uID).first()
        commentUsers.append(cUser.name)
        isCorrectAnswer.append(str(post.correntAnswer) == str(item.aID))
    if request.session.get("log"):
        areYouOwner = post.uID == request.session.get("uId")
    else:
        areYouOwner = False

    # check for post image
    aboutImage = isPostImage(post.qID)
    sendDict = {
        "post": post,
        "name": user.name,
        "mixList": zip(comments, commentUsers, isCorrectAnswer),
        "slug": slug,
        "areYouOwner": areYouOwner,
        "isImage": aboutImage["isPic"],
        "fileName": aboutImage["fileName"],
        "vote": post.likeCount-post.disLikeCount,
    }
    return render(request, "postView.html", sendDict)


def addLike(request):
    if request.session.get("log"):

        # check is user verified or not
        if not isUserVerified(request):
            return alert(request, False, "You are not verified", "Go to profile & verify your account", "/profile")

        if request.method == "POST":
            contentId = request.POST.get("qID")
            userId = request.session.get('uId')
            isStudent = request.session.get('isStudent')
            status = giveReaction(isStudent, userId, True, contentId, True)
            return redirect(index)
    return redirect(index)


def addDisLike(request):
    if request.session.get("log"):

        # check is user verified or not
        if not isUserVerified(request):
            return alert(request, False, "You are not verified", "Go to profile & verify your account", "/profile")

        if request.method == "POST":
            contentId = request.POST.get("qID")
            userId = request.session.get('uId')
            isStudent = request.session.get('isStudent')
            status = giveReaction(isStudent, userId, True, contentId, False)
            return redirect(index)
    return redirect(index)


def deletePost(request, slug):
    allComments = Answers.objects.filter(qID=slug).all()
    allComments.delete()
    return deleteObject(request, slug, True)


def deleteComment(request, slug):
    return deleteObject(request, slug, False)


def deleteObject(request, slug, isPost):
    if isPost:
        post = Quentions.objects.filter(qID=slug).first()
    else:
        post = Answers.objects.filter(aID=slug).first()

    if request.session.get("log"):
        areYouOwner = post.uID == request.session.get("uId")
    else:
        areYouOwner = False

    if areYouOwner:
        post.delete()
        if not isPost:
            question = Quentions.objects.filter(qID=post.qID).first()
            question.comments -= 1
            question.save()
        return redirect(index)
    return alert(request, False, "Error!", "You are not allowed to delete this", "/")


def fixPost(request, slug):
    if request.session.get("log"):
        answer = Answers.objects.filter(aID=slug).first()
        question = Quentions.objects.filter(qID=answer.qID).first()
        if request.session.get("uId") == question.uID:
            question.isFixed = True
            question.correntAnswer = slug
            question.save()
            return alert(request, True, "This is fixed", "Now this post is marked as Fixed.", f"/postView/{question.qID}")
    return redirect(index)
