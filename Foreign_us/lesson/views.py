from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView

from lesson.models import LessonFile, Lesson, LanguageTag, LessonReply, LessonLike
from member.models import Member, MemberFile
from review.models import Review, ReviewFile, ReviewLike, ReviewReply
from django.core import serializers
import json


# Create your views here.
class LessonListView(View):
    def get(self, request):
        return render(request, 'lesson/list.html')


class LessonListAPI(APIView):
    def get(self, request, page, type):
        size = 7
        offset = (page - 1) * size
        limit = page * size
        all_posts = list(Lesson.objects.order_by('-id').all())

        if type == 'popular_post':
            all_posts = list(Lesson.objects.order_by('-post_view_count').all())

        posts = []
        for i in range(len(all_posts)):
            id = all_posts[i].id
            member_id = all_posts[i].member_id
            member_files = MemberFile.objects.filter(member_id=member_id, file_type="P")
            lesson_file = LessonFile.objects.filter(lesson_id=id)
            post = Lesson.objects.filter(id=id).annotate(post_file=lesson_file.values('image')[:1], member_file=member_files.values('image')[:1]).values('id', 'created_date', 'post_title', 'post_content', 'post_view_count', 'post_file', 'member__member_nickname', 'member_file')
            posts.append(post)

        posts = posts[offset:limit + 1]
        # posts = list(Lesson.objects.order_by('-id').all())[offset:limit + 1]
        hasNext = False

        if len(posts) > size:
            hasNext = True
            posts.pop(size)

        context = {
            # 'posts': LessonSerializer(posts, many=True).data,
            'posts': posts,
            'hasNext': hasNext
        }

        # return Response(posts)
        return Response(context)

    def post(self, request, page):
        datas = json.loads(request.body)
        # print(dict(datas).get("post_filter"))
        # print(datas)
        # print(datas['post_filters'])
        post_filters = datas['post_filters']
        # print(post_filters)
        # print(datas)
        # print(post_filters)
        # print(post_filters)
        all_posts_filter = []
        # all_posts_filter = Lesson.objects.filter(languagetag__language_type__in=post_filters).order_by('-id')
        # print(all_posts_filter)
        # print(list(set(all_posts_filter)))

        if post_filters:
            for i in list(Lesson.objects.filter(languagetag__language_type__in=post_filters).order_by('-id')):
                if i not in all_posts_filter:
                    all_posts_filter.append(i)

        # print(Lesson.objects.filter(languagetag__language_type__in=post_filters).order_by('-id'))
        # print(all_posts_filter)


        size = 7
        offset = (page - 1) * size
        limit = page * size
        # all_posts = list(Lesson.objects.order_by('-id').all())
        # # print(all_posts)
        #
        # if type == 'popular_post':
        #     all_posts = list(Lesson.objects.order_by('-post_view_count').all())

        posts = []
        for i in range(len(all_posts_filter)):
            id = all_posts_filter[i].id
            member_id = all_posts_filter[i].member_id
            member = Member.objects.filter(id=member_id)
            member_files = MemberFile.objects.filter(member_id=member_id, file_type="P")
            lesson_file = LessonFile.objects.filter(lesson_id=id)
            post = Lesson.objects.filter(id=id)

            # post = Lesson.objects.filter(id=id).annotate(post_file=lesson_file.values('image')[:1], member_file=member_files.values('image')[:1]).values('id', 'created_date', 'post_title', 'post_content', 'post_view_count', 'post_file', 'member__member_nickname', 'member_file')
            # serializers.serialize('json', i)
            # print(i)
            # print(post)
            # temp = serializers.serialize('json', post)
            # print(temp)
            posts.append([serializers.serialize('json', post), serializers.serialize('json', lesson_file), serializers.serialize('json', member_files), serializers.serialize('json', member)])


        posts = posts[offset:limit + 1]
        # posts = list(Lesson.objects.order_by('-id').all())[offset:limit + 1]
        hasNext = False

        if len(posts) > size:
            hasNext = True
            posts.pop(size)

        # serialized_data = {
        #     'id': data['id'],
        #     'created_date': data['created_date'],
        #     'post_title': data['post_title'],
        #     'post_content': data['post_content'],
        #     'post_view_count': data['post_view_count'],
        #     'post_file': data['post_file'],
        #     'member__member_nickname': data['member__member_nickname'],
        #     'member_file': data['member_file'],
        # }


        # queryset_json = serializers.serialize('json', posts)
        # queryset_json = []
        # # for i in posts:
        # #     queryset_json.append(serializers.serialize('json', i))
        # print(queryset_json)
        # print((queryset_json))

        context = {
            'posts': posts,
            'hasNext': hasNext
        }
        return JsonResponse(context, status=200)


class LessonDetailView(View):
    # def get(self, request):
    #     return render(request, 'lesson/detail.html')

    def get(self, request, post_id):
        post = Lesson.objects.get(id=post_id)
        post.post_view_count = post.post_view_count + 1
        post.save()

        # 게시글 작성자의 모든 게시글 출력
        # member_posts = Lesson.objects.filter(member_id=post.member_id).all()

        writer_profile = "member/profile_icon.png"
        if post.member.memberfile_set.filter(file_type='P'):
            writer_profile = post.member.memberfile_set.get(file_type='P')

        context = {
            'post': post,
            'post_files': list(post.lessonfile_set.all()),
            'writer': post.member,
            'writer_profile': writer_profile,
        }
        if 'member_email' in request.session:
            member = Member.objects.get(member_email=request.session['member_email'])
            context['member'] = member
            if member.memberfile_set.filter(file_type='P'):
                context['member_profile'] = member.memberfile_set.get(file_type='P')

        return render(request, 'lesson/detail.html', context)


class LessonWriteView(View):
    def get(self, request, post_id=None):
        # 멤버 정보
        member = Member.objects.get(member_email=request.session['member_email'])

        # 멤버 프로필 이미지 없으면 기본 이미지로
        member_profile_img = "member/profile_icon.png"

        # 멤버의 프로필 이미지가 있으면 해당 이미지로
        if member.memberfile_set.filter(file_type='P'):
            member_profile_img = member.memberfile_set.get(file_type="P").image

        # 수정할 게시글 아이디가 맞다면 해당 게시글 수정
        if Lesson.objects.filter(id=post_id):
            post = Lesson.objects.get(id=post_id)
            post_tags = LanguageTag.objects.filter(lesson_id=post_id)
            context = {
                'member_file': member_profile_img,
                'post_title': post.post_title,
                'post_content': post.post_content,
                'post_status': post.post_status,
                'member': member,
                'post_id': post_id,
                'post_tags': post_tags,
                'tag_delete': post_tags,
            }
        # 거짓이면 새로운 게시글 작성
        else:
            context = {
                'member_file': member_profile_img,
                'post_title': "",
                'post_content': "",
                'post_status': "",
                'member': "",
                'post_id': 0,
            }
        return render(request, 'lesson/write.html', context)

    def post(self, request, post_id):
        # 멤버 정보
        member = Member.objects.get(member_email=request.session['member_email'])

        # 작성 및 수정페이지에서 받아온 데이터 및 파일,태그
        datas = request.POST
        files = request.FILES

        # 받아온 태그가 있다면 해당 태그 값을 담고 없으면 None이다
        post_tags = dict(datas).get("post_tags")

        # lesson(게시글) 생성 및 업데이트 할때 넣을 데이터
        lesson_datas = {
            'post_title': datas['post_title'],
            'post_content': datas['post_content'],
            'post_status': datas['post_status'],
            'member': member,
        }

        # 수정할 게시글 아이디가 맞다면 해당 게시글 수정
        if Lesson.objects.filter(id=post_id):
            Lesson.objects.filter(id=post_id).update(**lesson_datas)
            lesson_post = Lesson.objects.get(id=post_id)
            # 파일 업로드 시 전에 있던 파일 삭제 후 새로 받은 파일로 생성
            if files:
                LessonFile.objects.filter(lesson_id=post_id).delete()
                for file in files.getlist('post_file'):
                    LessonFile.objects.create(image=file, lesson=lesson_post)
            # 태그가 있다면 생성
            if post_tags:
                for tag in post_tags:
                    LanguageTag.objects.update_or_create(language_type=tag, lesson=lesson_post)
            # 하나라도 없으면 해당 게시글의 태그 전체삭제
            else:
                LanguageTag.objects.filter(lesson_id=post_id).delete()


        # 수정할 게시글이 없다면 새로운 게시글 생성
        else:
            lesson_post = Lesson.objects.create(**lesson_datas)
            # 파일 생성
            if files:
                for file in files.getlist('post_file'):
                    LessonFile.objects.create(image=file, lesson=lesson_post)

            # 태그 생성
            if post_tags:
                for tag in post_tags:
                    LanguageTag.objects.create(language_type=tag, lesson=lesson_post)


        return redirect('lesson:list-init')


# 과외 홍보 댓글
class LessonReplyListAPI(APIView):
    def get(self, request, post_id, page=1):
        size = 5
        offset = (page - 1) * size
        limit = page * size

        all_replies = list(LessonReply.objects.filter(lesson_id=post_id).order_by("-id").all())
        total = len(all_replies)

        replies = []
        for i in range(len(all_replies)):
            id = all_replies[i].member.id
            reply_id = all_replies[i].id
            reply_writer_file = MemberFile.objects.filter(member_id=id, file_type="P")
            reply = LessonReply.objects.filter(id=reply_id).order_by("-id").annotate(member_nickname=F('member__member_nickname'), reply_writer_file=reply_writer_file.values('image')[:1]).values('id', 'reply_content', 'member_id', 'member_nickname', 'created_date', 'reply_writer_file')
            replies.append(reply)
        #
        # posts = posts[offset:limit + 1]



        # replies = list(LessonReply.objects.filter(notice_id=post_id).order_by("-id").annotate(member_nickname=F('member__member_nickname')).values('id', 'reply_content', 'member_nickname', 'created_date'))
        # total = len(replies)

        replies = replies[offset:limit + 1]
        hasNext = False

        if len(replies) > size:
            hasNext = True
            replies.pop(size)

        context = {
            # 'posts': LessonSerializer(posts, many=True).data,
            'replies': replies,
            'hasNext': hasNext,
            'total': total
        }
        return Response(context)
        # return Response(LessonReplySerializer(replies, many=True).data)

class LessonReplyWriteAPI(APIView):
    def post(self, request):
        datas = request.data
        datas = {
            'lesson': Lesson.objects.get(id=datas.get('post_id')),
            'member': Member.objects.get(member_email=request.session['member_email']),
            'reply_content': datas.get('reply_content')
        }
        LessonReply.objects.create(**datas)
        return Response('success')


class LessonReplyModifyAPI(APIView):
    def post(self, request):
        datas = request.data

        LessonReply.objects.filter(id=datas['id']).update(reply_content=datas['reply_content'])
        return Response('success')


class LessonReplyDeleteAPI(APIView):
    def get(self, request, id):
        LessonReply.objects.filter(id=id).delete()
        return Response('success')


class LessonLikeAddAPI(APIView):
    def post(self, request):
        datas = request.data
        datas = {
            'lesson': Lesson.objects.get(id=datas['id']),
            'member': Member.objects.get(member_email=request.session['member_email']),
        }
        LessonLike.objects.create(**datas)
        return Response('success')


class LessonLikeDeleteAPI(APIView):
    def post(self, request):
        datas = request.data
        member = Member.objects.get(member_email=request.session['member_email'])
        LessonLike.objects.filter(lesson_id=datas['id'], member=member).delete()
        return Response('success')


class LessonLikeCountAPI(APIView):
    def get(self, request, id):
        return Response(LessonLike.objects.filter(lesson_id=id).count())


class LessonLikeExistAPI(APIView):
    def get(self, request, id):
        # datas = request.data
        member = Member.objects.get(member_email=request.session['member_email'])
        check = LessonLike.objects.filter(lesson_id=id, member=member).exists()
        return Response(check)








class LessonReviewDetailView(View):
    def get(self, request, post_id):
        post = Review.objects.get(id=post_id)
        post.post_view_count = post.post_view_count + 1
        post.save()

        writer_profile = "member/profile_icon.png"
        if post.member.memberfile_set.filter(file_type='P'):
            writer_profile = post.member.memberfile_set.get(file_type='P')

        context = {
            'post': post,
            'post_files': list(post.reviewfile_set.all()),
            'writer': post.member,
            'writer_profile': writer_profile,
        }
        if 'member_email' in request.session:
            member = Member.objects.get(member_email=request.session['member_email'])
            context['member'] = member
            if member.memberfile_set.filter(file_type='P'):
                context['member_profile'] = member.memberfile_set.get(file_type='P')

        return render(request, 'lesson/review-detail.html', context)



class LessonReviewWriteView(View):
    def get(self, request, post_id=None):
        # 멤버 정보
        member = Member.objects.get(member_email=request.session['member_email'])

        # 멤버 프로필 이미지 없으면 기본 이미지로
        member_profile_img = "member/profile_icon.png"

        # 멤버의 프로필 이미지가 있으면 해당 이미지로
        if member.memberfile_set.filter(file_type='P'):
            member_profile_img = member.memberfile_set.get(file_type="P").image

        # 수정할 게시글 아이디가 맞다면 해당 게시글 수정
        if Review.objects.filter(id=post_id):
            post = Review.objects.get(id=post_id)
            context = {
                'member_file': member_profile_img,
                'post_title': post.post_title,
                'post_content': post.post_content,
                'post_status': post.post_status,
                'member': member,
                'reviewed_member': post.reviewed_member.member_nickname,
                'post_id': post_id,
            }
        # 거짓이면 새로운 게시글 작성
        else:
            context = {
                'member_file': member_profile_img,
                'post_title': "",
                'post_content': "",
                'post_status': "",
                'member': "",
                'reviewed_member': "",
                'post_id': 0,
            }
        return render(request, 'lesson/review-write.html', context)

    def post(self, request, post_id):
        # 멤버 정보
        member = Member.objects.get(member_email=request.session['member_email'])

        # 작성 및 수정페이지에서 받아온 데이터 및 파일,태그
        datas = request.POST
        files = request.FILES
        reviewed_member = Member.objects.get(member_nickname=datas['reviewed_member'])

        # lesson(게시글) 생성 및 업데이트 할때 넣을 데이터
        review_datas = {
            'post_title': datas['post_title'],
            'post_content': datas['post_content'],
            'post_status': datas['post_status'],
            'member': member,
            'reviewed_member': reviewed_member,
        }

        # 수정할 게시글 아이디가 맞다면 해당 게시글 수정
        if Review.objects.filter(id=post_id):
            Review.objects.filter(id=post_id).update(**review_datas)
            review_post = Review.objects.get(id=post_id)
            # 파일 업로드 시 전에 있던 파일 삭제 후 새로 받은 파일로 생성
            if files:
                ReviewFile.objects.filter(review_id=post_id).delete()
                for file in files.getlist('post_file'):
                    ReviewFile.objects.create(image=file, review=review_post)

        # 수정할 게시글이 없다면 새로운 게시글 생성
        else:
            review_post = Review.objects.create(**review_datas)
            # 파일 생성
            if files:
                for file in files.getlist('post_file'):
                    ReviewFile.objects.create(image=file, review=review_post)


        # return redirect('mypage:mylesson-review_init')
        return redirect(f'/profile/{reviewed_member.id}')


# 과외 후기 댓글
class ReviewReplyListAPI(APIView):
    def get(self, request, post_id, page=1):
        size = 5
        offset = (page - 1) * size
        limit = page * size

        all_replies = list(ReviewReply.objects.filter(review_id=post_id).order_by("-id").all())
        total = len(all_replies)

        replies = []
        for i in range(len(all_replies)):
            id = all_replies[i].member.id
            reply_id = all_replies[i].id
            reply_writer_file = MemberFile.objects.filter(member_id=id, file_type="P")
            reply = ReviewReply.objects.filter(id=reply_id).order_by("-id").annotate(member_nickname=F('member__member_nickname'), reply_writer_file=reply_writer_file.values('image')[:1]).values('id', 'reply_content', 'member_id', 'member_nickname', 'created_date', 'reply_writer_file')
            replies.append(reply)

        replies = replies[offset:limit + 1]
        hasNext = False

        if len(replies) > size:
            hasNext = True
            replies.pop(size)

        context = {
            # 'posts': LessonSerializer(posts, many=True).data,
            'replies': replies,
            'hasNext': hasNext,
            'total': total
        }
        return Response(context)
        # return Response(LessonReplySerializer(replies, many=True).data)

class ReviewReplyWriteAPI(APIView):
    def post(self, request):
        datas = request.data
        datas = {
            'review': Review.objects.get(id=datas.get('post_id')),
            'member': Member.objects.get(member_email=request.session['member_email']),
            'reply_content': datas.get('reply_content')
        }
        ReviewReply.objects.create(**datas)
        return Response('success')


class ReviewReplyModifyAPI(APIView):
    def post(self, request):
        datas = request.data

        ReviewReply.objects.filter(id=datas['id']).update(reply_content=datas['reply_content'])
        return Response('success')


class ReviewReplyDeleteAPI(APIView):
    def get(self, request, id):
        ReviewReply.objects.filter(id=id).delete()
        return Response('success')


class ReviewLikeAddAPI(APIView):
    def post(self, request):
        datas = request.data
        datas = {
            'review': Review.objects.get(id=datas['id']),
            'member': Member.objects.get(member_email=request.session['member_email']),
        }
        ReviewLike.objects.create(**datas)
        return Response('success')


class ReviewLikeDeleteAPI(APIView):
    def post(self, request):
        datas = request.data
        member = Member.objects.get(member_email=request.session['member_email'])
        ReviewLike.objects.filter(review_id=datas['id'], member=member).delete()
        return Response('success')


class ReviewLikeCountAPI(APIView):
    def get(self, request, id):
        return Response(ReviewLike.objects.filter(review_id=id).count())


class ReviewLikeExistAPI(APIView):
    def get(self, request, id):
        # datas = request.data
        member = Member.objects.get(member_email=request.session['member_email'])
        check = ReviewLike.objects.filter(review_id=id, member=member).exists()
        return Response(check)