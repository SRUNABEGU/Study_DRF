from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson, Subscription
from users.models import User


class LessonTestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create(email='owner@test.com')
        self.other = User.objects.create(email='other@test.com')
        self.moder = User.objects.create(email='moder@test.com')
        self.moder.groups.add(Group.objects.create(name='moders'))

        self.course = Course.objects.create(title='Курс', owner=self.owner)
        self.lesson = Lesson.objects.create(
            title='Урок', course=self.course, owner=self.owner,
            video_url='https://youtube.com/abc',
        )
        self.client.force_authenticate(user=self.owner)

    def test_create_lesson(self):
        data = {'title': 'Новый', 'course': self.course.id,
                'video_url': 'https://youtube.com/xyz'}
        response = self.client.post(reverse('lms:lesson-create'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_create_lesson_bad_link(self):
        data = {'title': 'Плохой', 'course': self.course.id,
                'video_url': 'https://evil.com/video'}
        response = self.client.post(reverse('lms:lesson-create'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_lessons(self):
        response = self.client.get(reverse('lms:lesson-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 1)

    def test_retrieve_lesson(self):
        response = self.client.get(reverse('lms:lesson-detail', args=[self.lesson.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['title'], 'Урок')

    def test_update_lesson(self):
        response = self.client.patch(
            reverse('lms:lesson-update', args=[self.lesson.id]), {'title': 'Изменён'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Изменён')

    def test_delete_lesson(self):
        response = self.client.delete(reverse('lms:lesson-delete', args=[self.lesson.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())

    def test_anonymous_gets_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('lms:lesson-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_other_user_cannot_see_lesson(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.get(reverse('lms:lesson-detail', args=[self.lesson.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moder_can_update(self):
        self.client.force_authenticate(user=self.moder)
        response = self.client.patch(
            reverse('lms:lesson-update', args=[self.lesson.id]), {'title': 'Правка'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_moder_cannot_create(self):
        self.client.force_authenticate(user=self.moder)
        data = {'title': 'X', 'course': self.course.id}
        response = self.client.post(reverse('lms:lesson-create'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moder_cannot_delete(self):
        self.client.force_authenticate(user=self.moder)
        response = self.client.delete(reverse('lms:lesson-delete', args=[self.lesson.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='user@test.com')
        self.course = Course.objects.create(title='Курс', owner=self.user)
        self.client.force_authenticate(user=self.user)
        self.url = reverse('lms:subscribe')

    def test_subscribe(self):
        response = self.client.post(self.url, {'course_id': self.course.id})
        self.assertEqual(response.json()['message'], 'подписка добавлена')
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_unsubscribe(self):
        Subscription.objects.create(user=self.user, course=self.course)
        response = self.client.post(self.url, {'course_id': self.course.id})
        self.assertEqual(response.json()['message'], 'подписка удалена')
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_course_not_found(self):
        response = self.client.post(self.url, {'course_id': 999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_is_subscribed_flag(self):
        Subscription.objects.create(user=self.user, course=self.course)
        response = self.client.get(reverse('lms:courses-detail', args=[self.course.id]))
        self.assertTrue(response.json()['is_subscribed'])