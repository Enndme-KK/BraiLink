<template>
	<view class="appointment-page">
		<!-- 自定义顶部导航 -->
		<view class="custom-header">
			<view class="header-bg"></view>
			<view class="header-content safe-area-top">
				<view class="header-top">
					<view class="header-back" @click="goBack">
						<text class="back-icon">←</text>
					</view>
					<view class="header-title-wrapper">
						<text class="header-title">预约挂号</text>
						<text class="header-subtitle">Appointment</text>
					</view>
					<view class="header-placeholder"></view>
				</view>
			</view>
		</view>
		
		<!-- 页面内容 -->
		<scroll-view class="page-content" scroll-y>
			<!-- 医生信息卡片 -->
			<view class="doctor-card" v-if="doctorInfo">
				<view class="doctor-header">
					<view class="doctor-avatar">
						<text class="avatar-text">{{ doctorInfo.name ? doctorInfo.name[0] : '医' }}</text>
					</view>
					<view class="doctor-info">
						<text class="doctor-name">{{ doctorInfo.name }}</text>
						<text class="doctor-title">{{ doctorInfo.title || '医生' }}</text>
					</view>
				</view>
				<view class="doctor-details">
					<view class="detail-item">
						<text class="detail-label">🏥 医院:</text>
						<text class="detail-value">{{ doctorInfo.hospital || '未填写' }}</text>
					</view>
					<view class="detail-item">
						<text class="detail-label">🏢 科室:</text>
						<text class="detail-value">{{ doctorInfo.department || '未填写' }}</text>
					</view>
					<view class="detail-item">
						<text class="detail-label">🎓 专科:</text>
						<text class="detail-value">{{ getSpecialtyText(doctorInfo.specialty) || '未填写' }}</text>
					</view>
				</view>
			</view>
			
			<!-- 挂号表单 -->
			<view class="form-section">
				<view class="section-title">挂号信息</view>
				
				<!-- 挂号类型 -->
				<view class="form-item">
					<text class="form-label">挂号类型 <text class="required">*</text></text>
					<picker mode="selector" :range="appointmentTypes" :range-key="'label'" @change="onAppointmentTypeChange" :value="appointmentTypeIndex">
						<view class="picker-view">
							<text :class="formData.appointmentType ? 'picker-text' : 'picker-placeholder'">
								{{ formData.appointmentType || '请选择挂号类型' }}
							</text>
							<text class="picker-arrow">›</text>
						</view>
					</picker>
				</view>
				
				<!-- 就诊日期 -->
				<view class="form-item">
					<text class="form-label">就诊日期 <text class="required">*</text></text>
					<picker mode="date" :value="formData.visitDate" @change="onDateChange" :start="minDate">
						<view class="picker-view">
							<text :class="formData.visitDate ? 'picker-text' : 'picker-placeholder'">
								{{ formData.visitDate || '请选择就诊日期' }}
							</text>
							<text class="picker-arrow">›</text>
						</view>
					</picker>
				</view>
				
				<!-- 就诊时间 -->
				<view class="form-item">
					<text class="form-label">就诊时间 <text class="required">*</text></text>
					<picker mode="selector" :range="timeSlots" @change="onTimeChange" :value="timeIndex">
						<view class="picker-view">
							<text :class="formData.visitTime ? 'picker-text' : 'picker-placeholder'">
								{{ formData.visitTime || '请选择就诊时间' }}
							</text>
							<text class="picker-arrow">›</text>
						</view>
					</picker>
				</view>
				
				<!-- 科室 -->
				<view class="form-item">
					<text class="form-label">就诊科室</text>
					<input 
						class="form-input" 
						v-model="formData.department" 
						placeholder="请输入就诊科室（可选）"
						placeholder-style="color: #999999"
					/>
				</view>
				
				<!-- 主诉 -->
				<view class="form-item">
					<text class="form-label">主诉</text>
					<textarea 
						class="form-textarea" 
						v-model="formData.symptoms" 
						placeholder="请描述您的主要症状（可选）"
						placeholder-style="color: #999999"
						:maxlength="500"
					/>
					<text class="char-count">{{ formData.symptoms.length }}/500</text>
				</view>
				
				<!-- 病史 -->
				<view class="form-item">
					<text class="form-label">病史</text>
					<textarea 
						class="form-textarea" 
						v-model="formData.medicalHistory" 
						placeholder="请描述您的病史（可选）"
						placeholder-style="color: #999999"
						:maxlength="500"
					/>
					<text class="char-count">{{ formData.medicalHistory.length }}/500</text>
				</view>
			</view>
			
			<!-- 提交按钮 -->
			<view class="submit-section">
				<button class="submit-btn" :class="{ 'disabled': !canSubmit }" @click="submitAppointment" :disabled="!canSubmit || isSubmitting">
					<text v-if="!isSubmitting">确认挂号</text>
					<text v-else>提交中...</text>
				</button>
			</view>
		</scroll-view>
	</view>
</template>

<script>
import { appointmentAPI, doctorAPI } from '@/utils/request.js'

export default {
	name: 'Appointment',
	data() {
		return {
			doctorId: null,
			doctorName: '',
			doctorInfo: null,
			appointmentTypes: [
				{ value: 'outpatient', label: '普通门诊' },
				{ value: 'expert', label: '专家门诊' },
				{ value: 'emergency', label: '急诊' },
				{ value: 'followup', label: '复诊' }
			],
			appointmentTypeIndex: 0,
			timeSlots: [
				'08:00-09:00',
				'09:00-10:00',
				'10:00-11:00',
				'11:00-12:00',
				'14:00-15:00',
				'15:00-16:00',
				'16:00-17:00',
				'17:00-18:00'
			],
			timeIndex: 0,
			formData: {
				appointmentType: '',
				visitDate: '',
				visitTime: '',
				department: '',
				symptoms: '',
				medicalHistory: ''
			},
			isSubmitting: false,
			minDate: ''
		}
	},
	computed: {
		canSubmit() {
			return this.formData.appointmentType && 
			       this.formData.visitDate && 
			       this.formData.visitTime
		}
	},
	async onLoad(options) {
		// 检查登录状态
		const authModule = await import('@/utils/auth.js')
		if (!authModule.requireAuth()) {
			return
		}
		
		// 验证用户类型
		const userType = authModule.getCurrentUserType()
		if (userType !== 'patient') {
			uni.showToast({
				title: '此页面仅限患者访问',
				icon: 'none'
			})
			setTimeout(() => {
				uni.navigateBack()
			}, 1500)
			return
		}
		
		// 获取参数
		this.doctorId = options.doctorId
		this.doctorName = decodeURIComponent(options.doctorName || '')
		
		// 设置最小日期为今天
		const today = new Date()
		this.minDate = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
		
		// 加载医生信息
		await this.loadDoctorInfo()
	},
	methods: {
		// 返回
		goBack() {
			uni.navigateBack()
		},
		
		// 加载医生信息
		async loadDoctorInfo() {
			try {
				console.log('开始加载医生信息，doctorId:', this.doctorId, 'doctorName:', this.doctorName)
				
				const doctors = await doctorAPI.getDoctors()
				const doctorsList = Array.isArray(doctors) ? doctors : (doctors.results || [])
				console.log('获取到的医生列表:', doctorsList)
				
				if (this.doctorId) {
					// 先通过ID查找
					this.doctorInfo = doctorsList.find(d => d.id == this.doctorId || d.id === parseInt(this.doctorId))
					console.log('通过ID查找医生:', this.doctorInfo)
				}
				
				if (!this.doctorInfo && this.doctorName) {
					// 如果找不到，使用名称匹配
					this.doctorInfo = doctorsList.find(d => d.name === this.doctorName)
					console.log('通过名称查找医生:', this.doctorInfo)
				}
				
				if (!this.doctorInfo && doctorsList.length > 0) {
					// 如果还是找不到，使用第一个医生（降级处理）
					console.warn('未找到指定医生，使用第一个医生')
					this.doctorInfo = doctorsList[0]
				}
				
				if (this.doctorInfo) {
					// 默认设置科室
					if (!this.formData.department && this.doctorInfo.department) {
						this.formData.department = this.doctorInfo.department
					}
					console.log('医生信息加载成功:', this.doctorInfo.name)
				} else {
					console.error('未找到医生信息')
					uni.showToast({
						title: '未找到医生信息',
						icon: 'none'
					})
				}
			} catch (error) {
				console.error('加载医生信息失败:', error)
				uni.showToast({
					title: '加载医生信息失败: ' + (error.message || '未知错误'),
					icon: 'none',
					duration: 3000
				})
			}
		},
		
		// 获取专科文本
		getSpecialtyText(specialty) {
			const specialtyMap = {
				'neurology': '神经科',
				'radiology': '放射科',
				'oncology': '肿瘤科',
				'neurosurgery': '神经外科',
				'general': '全科'
			}
			return specialtyMap[specialty] || specialty || '未填写'
		},
		
		// 挂号类型改变
		onAppointmentTypeChange(e) {
			this.appointmentTypeIndex = e.detail.value
			this.formData.appointmentType = this.appointmentTypes[e.detail.value].label
		},
		
		// 日期改变
		onDateChange(e) {
			this.formData.visitDate = e.detail.value
		},
		
		// 时间改变
		onTimeChange(e) {
			this.timeIndex = e.detail.value
			this.formData.visitTime = this.timeSlots[e.detail.value]
		},
		
		// 提交挂号
		async submitAppointment() {
			if (!this.canSubmit || this.isSubmitting) {
				return
			}
			
			// 验证表单
			if (!this.formData.appointmentType) {
				uni.showToast({
					title: '请选择挂号类型',
					icon: 'none'
				})
				return
			}
			
			if (!this.formData.visitDate) {
				uni.showToast({
					title: '请选择就诊日期',
					icon: 'none'
				})
				return
			}
			
			if (!this.formData.visitTime) {
				uni.showToast({
					title: '请选择就诊时间',
					icon: 'none'
				})
				return
			}
			
			// 确认提交
			uni.showModal({
				title: '确认挂号',
				content: `确定要挂${this.doctorInfo?.name || '该医生'}的号吗？\n挂号类型：${this.formData.appointmentType}\n就诊日期：${this.formData.visitDate}\n就诊时间：${this.formData.visitTime}`,
				success: async (res) => {
					if (res.confirm) {
						await this.doSubmit()
					}
				}
			})
		},
		
		// 执行提交
		async doSubmit() {
			this.isSubmitting = true
			
			try {
				uni.showLoading({
					title: '挂号中...',
					mask: true
				})
				
				const selectedType = this.appointmentTypes[this.appointmentTypeIndex] || this.appointmentTypes[0]
				const visitStartTime = this.formData.visitTime.split('-')[0]
				const appointmentData = {
					doctor_id: this.doctorId ? parseInt(this.doctorId) : null,
					appointment_type: selectedType.value,
					visit_date: `${this.formData.visitDate}T${visitStartTime}:00`,
					department: this.formData.department || this.doctorInfo?.department || '',
					symptoms: this.formData.symptoms || '',
					medical_history: this.formData.medicalHistory || ''
				}
				
				const response = await appointmentAPI.createAppointment(appointmentData)
				
				uni.hideLoading()
				
				uni.showToast({
					title: '挂号申请已提交',
					icon: 'success',
					duration: 2000
				})
				
				// 延迟返回，让用户看到成功提示
				setTimeout(() => {
					uni.navigateBack()
				}, 1500)
				
			} catch (error) {
				uni.hideLoading()
				console.error('挂号失败:', error)
				uni.showToast({
					title: error.message || '挂号失败，请重试',
					icon: 'none',
					duration: 2000
				})
			} finally {
				this.isSubmitting = false
			}
		}
	}
}
</script>

<style scoped>
.appointment-page { min-height: 100vh; background: var(--ds-bg); display: flex; flex-direction: column; font-family: var(--ds-font); }

.custom-header { position: sticky; top: 0; z-index: 100; }
.header-bg { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(244,246,251,0.85); backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px); border-bottom: 1px solid var(--ds-hairline); }
.header-content { position: relative; padding: 52px 16px 12px; }
.header-top { display: flex; align-items: center; justify-content: space-between; }
.header-back { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 12px; transition: background 0.18s; }
.header-back:active { background: var(--ds-brand-ghost); }
.back-icon { font-size: 28px; color: var(--ds-brand); font-weight: 300; line-height: 1; margin-top: -3px; }
.header-title-wrapper { flex: 1; text-align: center; }
.header-title { font-size: 17px; font-weight: 700; color: var(--ds-ink-1); display: block; }
.header-subtitle { font-size: 10px; font-weight: 600; color: var(--ds-ink-4); display: block; margin-top: 2px; letter-spacing: 1px; font-family: var(--ds-font-mono); }
.header-placeholder { width: 36px; }

.page-content { flex: 1; padding: 18px 20px; }

.doctor-card { background: var(--ds-surface); border-radius: var(--ds-r-md); padding: 16px; margin-bottom: 14px; border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); animation: ds-rise 0.5s var(--ds-ease) both; animation-delay: 0.05s; }
.doctor-header { display: flex; align-items: center; margin-bottom: 14px; padding-bottom: 14px; border-bottom: 1px solid var(--ds-hairline); }
.doctor-avatar { width: 54px; height: 54px; border-radius: 16px; background: var(--ds-grad-brand); display: flex; align-items: center; justify-content: center; margin-right: 14px;  }
.avatar-text { font-size: 22px; font-weight: 800; color: #fff; }
.doctor-info { flex: 1; display: flex; flex-direction: column; }
.doctor-name { font-size: 17px; font-weight: 800; color: var(--ds-ink-1); margin-bottom: 4px; }
.doctor-title { font-size: 12px; color: var(--ds-ink-3); }

.doctor-details { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.detail-item { display: flex; flex-direction: column; gap: 4px; padding: 10px 12px; background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); }
.detail-item:nth-child(3) { grid-column: 1 / -1; }
.detail-label { font-size: 10px; font-weight: 700; color: var(--ds-ink-4); letter-spacing: 0.8px; }
.detail-value { font-size: 13px; color: var(--ds-ink-1); font-weight: 600; }

.form-section { background: var(--ds-surface); border-radius: var(--ds-r-md); padding: 18px; margin-bottom: 14px; border: 1px solid var(--ds-hairline); box-shadow: var(--ds-shadow-sm); animation: ds-rise 0.5s var(--ds-ease) both; animation-delay: 0.12s; }
.section-title { font-size: 16px; font-weight: 800; color: var(--ds-ink-1); margin-bottom: 16px; padding-bottom: 10px; border-bottom: 1px solid var(--ds-hairline); display: block; }

.form-item { margin-bottom: 16px; }
.form-item:last-child { margin-bottom: 0; }
.form-label { font-size: 13px; color: var(--ds-ink-2); margin-bottom: 8px; display: block; font-weight: 600; }
.required { color: var(--ds-danger); }

.picker-view { display: flex; align-items: center; justify-content: space-between; padding: 12px 14px; background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); border: 1px solid var(--ds-hairline); }
.picker-text { font-size: 14px; color: var(--ds-ink-1); }
.picker-placeholder { font-size: 14px; color: var(--ds-ink-4); }
.picker-arrow { font-size: 18px; color: var(--ds-ink-4); }

.form-input { width: 100%; padding: 12px 14px; background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); border: 1px solid var(--ds-hairline); font-size: 14px; color: var(--ds-ink-1); box-sizing: border-box; }
.form-textarea { width: 100%; min-height: 90px; padding: 12px 14px; background: var(--ds-bg-sunken); border-radius: var(--ds-r-sm); border: 1px solid var(--ds-hairline); font-size: 14px; color: var(--ds-ink-1); box-sizing: border-box; line-height: 1.55; }
.char-count { font-size: 11px; color: var(--ds-ink-4); text-align: right; margin-top: 5px; display: block; font-family: var(--ds-font-mono); letter-spacing: 0.3px; }

.submit-section { padding: 6px 0 30px; animation: ds-rise 0.5s var(--ds-ease) both; animation-delay: 0.19s; }
.submit-btn { width: 100%; height: 50px; background: var(--ds-grad-brand); color: #fff; border-radius: var(--ds-r-sm); font-size: 16px; font-weight: 600; border: none; box-shadow: var(--ds-shadow-brand); letter-spacing: 0.5px; transition: transform 0.18s; }
.submit-btn:active { transform: scale(0.97); }
.submit-btn.disabled { background: var(--ds-bg-sunken); color: var(--ds-ink-4); box-shadow: none; }
.submit-btn::after { border: none; }

@keyframes ds-rise { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
</style>

