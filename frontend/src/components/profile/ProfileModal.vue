<template>
  <Dialog
    v-model="showProfileDialog"
    :options="{
      title: 'Thông tin cá nhân',
      size: 'xl',
    }"
  >
    <template #body-content>
      <div class="text-base">
        <div class="flex flex-col gap-4">
          <div
            class="flex items-center border-b border-solid border-lightGray pb-4 gap-2"
          >
            <Avatar
              size="3xl"
              class="h-12 w-12"
              :label="studentInfo.student_name"
              :image="studentInfo.image || null"
            />
            <div class="flex flex-col ml-2 gap-1">
              <p class="text-lg font-semibold">
                {{ studentInfo.student_name }}
              </p>
              <p class="text-gray-600">{{ studentInfo.student_email_id }}</p>
            </div>
          </div>
          <div>
            <div class="flex gap-4">
              <div
                v-for="section in infoFormat"
                :key="section.section"
                class="flex-1 flex flex-col gap-4"
              >
                <div v-for="field in section.fields" :key="field.label">
                  <div
                    class="flex items-center"
                    v-if="field.label !== 'Address'"
                  >
                    <p class="w-1/2 text-sm text-gray-600">
                      {{ field.label }}:&nbsp;
                    </p>
                    <p class="w-1/2 text-gray-900">{{ field.value }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div
            class="flex items-center bg-gray-50 p-2 text-gray-600 text-sm rounded-md"
          >
            <FeatherIcon name="info" class="h-4 mr-2" />
            Trong trường hợp có bất kỳ chi tiết nào sai lệch, vui lòng liên hệ với quản trị viên trường.
          </div>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { Dialog, Avatar, FeatherIcon } from 'frappe-ui'
import { inject } from 'vue'
import { studentStore } from '@/stores/student'
const { getStudentInfo } = studentStore()

const showProfileDialog = inject('showProfileDialog')

const studentInfo = getStudentInfo().value

const infoFormat = [
  {
    section: 'section 1',
    fields: [
      {
        label: 'Số điện thoại',
        value: studentInfo.student_mobile_number,
      },
      {
        label: 'Ngày tham gia',
        value: studentInfo.joining_date,
      },
      {
        label: 'Ngày sinh',
        value: studentInfo.date_of_birth,
      },
      {
        label: 'Địa chỉ',
        value: [
          studentInfo?.address_line_1,
          studentInfo?.address_line_2,
          studentInfo?.city,
          studentInfo?.pincode,
          studentInfo?.state,
          studentInfo?.country,
        ]
          .map((item) => item?.trim())
          .filter(Boolean)
          .join(', '),
      },
    ],
  },
  {
    section: 'section 2',
    fields: [
      {
        label: 'Nhóm máu',
        value: studentInfo.blood_group,
      },
      {
        label: 'Giới tính',
        value: studentInfo.gender,
      },
      {
        label: 'Quốc tịch',
        value: studentInfo.nationality,
      },
    ],
  },
]
</script>
