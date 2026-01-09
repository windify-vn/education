import { createRouter, createWebHistory } from 'vue-router'
import { usersStore } from '@/stores/user'
import { sessionStore } from '@/stores/session'
import { studentStore } from '@/stores/student'

const routes = [
  { path: '/', redirect: '/profile' },
  {
    path: '/404',
    name: 'Không tìm thấy trang',
    component: () => import('@/pages/404.vue'),
  },
  {
    path: '/doctype-tester',
    name: 'Doctype Tester',
    component: () => import('@/pages/CrudTester.vue'),
  },
  {
    path: '/profile',
    name: 'Hồ sơ cá nhân',
    component: () => import('@/pages/Profile.vue'),
  },
  {
    path: '/program',
    name: 'Chương trình học',
    component: () => import('@/pages/ProgramAcademy.vue'),
  },
  {
    path: '/view',
    name: 'Xem tài liệu',
    component: () => import('@/pages/ViewDocument.vue'),
  },
  // {
  //   path: '/program/:programName',
  //   name: 'Chi tiết chương trình học',
  //   component: () => import('@/pages/ProgramAcademyDetail.vue'),
  // },
  {
    path: '/program/:programName/:courseName',
    name: 'Chi tiết khóa học',
    component: () => import('@/pages/ProgramAcademyCourseDetail.vue'),
  },
  {
    path: '/program/:programName/:courseName/:topicName',
    name: 'Chi tiết bài học',
    component: () => import('@/pages/ProgramAcademyTopicDetail.vue'),
  },
  {
    path: '/schedule',
    name: 'Lịch học',
    component: () => import('@/pages/Schedule.vue'),
  },
  {
    path: '/grades',
    name: 'Điểm Số',
    component: () => import('@/pages/Grades.vue'),
  },
  {
    path: '/fees',
    name: 'Học Phí',
    component: () => import('@/pages/Fees.vue'),
  },
  {
    path: '/attendance',
    name: 'Điểm Danh',
    component: () => import('@/pages/Attendance.vue'),
  },
  {
    path: '/achievements-ranking',
    name: 'Bảng thành tích',
    component: () => import('@/pages/AchievementsRanking.vue'),
  },
  {
    path: '/learning',
    name: 'Tài liệu học tập',
    component: () => import('@/pages/Learning.vue'),
  },
  {
    path: '/homework',
    name: 'Bài tập về nhà',
    component: () => import('@/pages/Homework.vue'),
  },
  {
    path: '/homework/:homeworkName',
    name: 'Chi tiết bài tập về nhà',
    component: () => import('@/pages/HomeworkDetail.vue'),
  },
  {
    path: '/assessment-results',
    name: 'Kết quả đánh giá',
    component: () => import('@/pages/AssessmentResult.vue'),
  },
  {
    path: '/assessment-result/:id',
    name: 'Chi tiết kết quả đánh giá',
    component: () => import('@/pages/AssessmentResultDetail.vue'),
  },
  {
    path: '/:catchAll(.*)',
    name: 'Không tìm thấy trang',
    component: () => import('@/pages/404.vue'),
  },
]

let router = createRouter({
  history: createWebHistory('/student-portal'),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const { isLoggedIn, user: sessionUser } = sessionStore()
  const { user } = usersStore()
  const { student, studentInfo } = studentStore()

  if (!isLoggedIn) {
    window.location.href = '/login'
    return
  }

  if (user.data.length === 0) {
    await user.reload()
  }

  await student.reload()

  // Kiểm tra nếu có user info nhưng không có student info
  if (
    user.data.length > 0 &&
    (!studentInfo || Object.keys(studentInfo).length === 0)
  ) {
    window.location.href = '/app/education'
    return
  }

  next()
})

export default router
