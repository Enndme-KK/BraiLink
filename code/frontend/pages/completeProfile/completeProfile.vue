<template>
	<view class="page-container">
		<!-- 背景装饰 -->
		<view class="bg-decoration">
			<view class="circle circle-1"></view>
			<view class="circle circle-2"></view>
			<view class="circle circle-3"></view>
		</view>
		
		<!-- 顶部标题 -->
		<view class="header-section">
			<view class="back-btn" @click="goBack" hover-class="back-pressed">
				<text class="back-char">‹</text>
			</view>
			<view class="logo-container">
				<view class="logo-icon">
					<text class="icon">📋</text>
				</view>
				<text class="app-title">完善档案</text>
				<text class="app-subtitle">{{ userTypeText }}信息完善</text>
			</view>
		</view>
		
		<!-- 表单容器 -->
		<view class="form-container">
			<view class="form-card">
				<view class="card-gradient"></view>
				
				<!-- 医生档案表单 -->
				<view class="form-content" v-if="userType === 'doctor'">
					<!-- 姓名 -->
					<view class="input-group">
						<text class="field-label">姓名 <text class="label-required">*</text></text>
						<text class="field-hint">请填写您的真实姓名</text>
						<view class="input-wrapper">
							<text class="input-icon">👤</text>
							<input 
								class="input-field" 
								type="text" 
								placeholder="如：张三" 
								v-model="doctorForm.name"
								maxlength="50"
							/>
						</view>
					</view>
					
					<!-- 执业证号 -->
					<view class="input-group">
						<text class="field-label">执业证号 <text class="label-required">*</text></text>
						<text class="field-hint">请填写您的医师执业证书编号</text>
						<view class="input-wrapper">
							<text class="input-icon">📜</text>
							<input 
								class="input-field" 
								type="text" 
								placeholder="如：DOC001234" 
								v-model="doctorForm.license_number"
								maxlength="50"
							/>
						</view>
					
					<!-- 专科 -->
					<view class="input-group">
						<text class="field-label">专科 <text class="label-required">*</text></text>
						<text class="field-hint">请选择您的专科领域</text>
						<view class="input-wrapper">
							<text class="input-icon">🏥</text>
							<picker mode="selector" :range="specialtyOptions" :range-key="'label'" @change="onSpecialtyChange">
								<view class="picker-view">
									<text :class="doctorForm.specialty ? 'picker-text' : 'picker-placeholder'">
										{{ doctorForm.specialty ? getSpecialtyLabel(doctorForm.specialty) : '请选择专科（必填）' }}
									</text>
									<text class="picker-arrow">▼</text>
								</view>
							</picker>
						</view>
					</view>
					
					<!-- 医院 -->
					<view class="input-group">
						<text class="field-label">医院 <text class="label-required">*</text></text>
						<text class="field-hint">请填写您所在的医院名称</text>
						<view class="input-wrapper">
							<text class="input-icon">🏢</text>
							<input 
								class="input-field" 
								type="text" 
								placeholder="如：北京大学第一医院" 
								v-model="doctorForm.hospital"
								maxlength="200"
							/>
						</view>
					</view>
					
					<!-- 科室 -->
					<view class="input-group">
						<text class="field-label">科室 <text class="label-required">*</text></text>
						<text class="field-hint">请填写您所在的科室名称</text>
						<view class="input-wrapper">
							<text class="input-icon">🚪</text>
							<input 
								class="input-field" 
								type="text" 
								placeholder="如：神经外科、放射科" 
								v-model="doctorForm.department"
								maxlength="100"
							/>
						</view>
					</view>
					
					<!-- 职称 -->
					<view class="input-group">
						<text class="field-label">职称</text>
						<text class="field-hint">请填写您的职称</text>
						<view class="input-wrapper">
							<text class="input-icon">💼</text>
							<input 
								class="input-field" 
								type="text" 
								placeholder="如：主任医师、副主任医师、主治医师" 
								v-model="doctorForm.title"
								maxlength="50"
							/>
						</view>
					</view>
					
					<!-- 手机号 -->
					<view class="input-group">
						<text class="field-label">手机号</text>
						<text class="field-hint">请填写您的手机号码</text>
						<view class="input-wrapper">
							<text class="input-icon">📱</text>
							<input 
								class="input-field" 
								type="number" 
								placeholder="如：13812345678" 
								v-model="doctorForm.phone"
								maxlength="11"
							/>
						</view>
					</view>
					
					<!-- 个人简介 -->
					<view class="input-group">
						<text class="field-label">个人简介</text>
						<text class="field-hint">请填写您的专业特长及简介</text>
						<view class="input-wrapper textarea-wrapper">
							<text class="input-icon">📝</text>
							<textarea 
								class="textarea-field" 
								placeholder="如：擅长脑肿瘤诊断与手术治疗"
								v-model="doctorForm.bio"
								maxlength="500"
							/>
						</view>
					</view>
				</view>
				
				<!-- 患者档案表单 -->
				<view class="form-content" v-else>
					<!-- 姓名 -->
					<view class="input-group">
						<text class="field-label">姓名 <text class="label-required">*</text></text>
						<text class="field-hint">请填写您的真实姓名</text>
						<view class="input-wrapper">
							<text class="input-icon">👤</text>
							<input 
								class="input-field" 
								type="text" 
								placeholder="如：李四" 
								v-model="patientForm.name"
								maxlength="50"
							/>
						</view>
					</view>
					
					<!-- 性别 -->
					<view class="input-group">
						<text class="field-label">性别 <text class="label-required">*</text></text>
						<text class="field-hint">请选择您的性别</text>
						<view class="input-wrapper">
							<text class="input-icon">⚧️</text>
							<picker mode="selector" :range="genderOptions" :range-key="'label'" @change="onGenderChange">
								<view class="picker-view">
									<text :class="patientForm.gender ? 'picker-text' : 'picker-placeholder'">
										{{ patientForm.gender ? getGenderLabel(patientForm.gender) : '请选择性别（必填）' }}
									</text>
									<text class="picker-arrow">▼</text>
								</view>
							</picker>
						</view>
					</view>
					
					<!-- 身份证号 -->
					<view class="input-group">
						<text class="field-label">身份证号 <text class="label-required">*</text></text>
						<text class="field-hint">请填写您的18位身份证号码</text>
						<view class="input-wrapper">
							<text class="input-icon">🆔</text>
							<input 
								class="input-field" 
								type="text" 
								placeholder="如：110101199001011234" 
								v-model="patientForm.id_card"
								maxlength="18"
							/>
						</view>
						<text class="input-hint" v-if="patientForm.id_card && patientForm.id_card.length !== 18">
							身份证号应为18位
						</text>
					</view>
					
					<!-- 出生日期 -->
					<view class="input-group">
						<text class="field-label">出生日期 <text class="label-required">*</text></text>
						<text class="field-hint">请选择您的出生日期</text>
						<view class="input-wrapper">
							<text class="input-icon">📅</text>
							<picker mode="date" :value="patientForm.birth_date" @change="onBirthDateChange">
								<view class="picker-view">
									<text :class="patientForm.birth_date ? 'picker-text' : 'picker-placeholder'">
										{{ patientForm.birth_date || '请选择出生日期（必填）' }}
									</text>
									<text class="picker-arrow">▼</text>
								</view>
							</picker>
						</view>
					</view>
					
					<!-- 手机号 -->
					<view class="input-group">
						<text class="field-label">手机号</text>
						<text class="field-hint">请填写您的11位手机号码</text>
						<view class="input-wrapper">
							<text class="input-icon">📱</text>
							<input 
								class="input-field" 
								type="number" 
								placeholder="如：13812345678" 
								v-model="patientForm.phone"
								maxlength="11"
							/>
						</view>
						<text class="input-hint" v-if="patientForm.phone && patientForm.phone.length !== 11">
							请输入11位手机号
						</text>
					</view>
					
					<!-- 地址 -->
					<view class="input-group">
						<text class="field-label">联系地址</text>
						<text class="field-hint">请填写您的常用联系地址</text>
						<view class="input-wrapper textarea-wrapper">
							<text class="input-icon">📍</text>
							<textarea 
								class="textarea-field" 
								placeholder="如：北京市海淀区中关村大街1号"
								v-model="patientForm.address"
								maxlength="200"
							/>
						</view>
					</view>
					
					<!-- 紧急联系人 -->
					<view class="input-group">
						<text class="field-label">紧急联系人</text>
						<text class="field-hint">请填写紧急联系人的姓名</text>
						<view class="input-wrapper">
							<text class="input-icon">👨‍👩‍👧</text>
							<input 
								class="input-field" 
								type="text" 
								placeholder="如：张三" 
								v-model="patientForm.emergency_contact"
								maxlength="100"
							/>
						</view>
					</view>
					
					<!-- 紧急联系人电话 -->
					<view class="input-group">
						<text class="field-label">紧急联系人电话</text>
						<text class="field-hint">请填写紧急联系人的电话号码</text>
						<view class="input-wrapper">
							<text class="input-icon">📞</text>
							<input 
								class="input-field" 
								type="number" 
								placeholder="如：13912345678" 
								v-model="patientForm.emergency_phone"
								maxlength="20"
							/>
						</view>
					</view>
					
					<!-- 病史 -->
					<view class="input-group">
						<text class="field-label">既往病史</text>
						<text class="field-hint">请填写既往病史（如无可不填）</text>
						<view class="input-wrapper textarea-wrapper">
							<text class="input-icon">🏥</text>
							<textarea 
								class="textarea-field" 
								placeholder="如：高血压、糖尿病等"
								v-model="patientForm.medical_history"
								maxlength="500"
							/>
						</view>
					</view>
					
					<!-- 过敏史 -->
					<view class="input-group">
						<text class="field-label">过敏史</text>
						<text class="field-hint">请填写过敏史（如无可不填）</text>
						<view class="input-wrapper textarea-wrapper">
							<text class="input-icon">⚠️</text>
							<textarea 
								class="textarea-field" 
								placeholder="如：青霉素过敏、海鲜过敏等"
								v-model="patientForm.allergies"
								maxlength="200"
							/>
						</view>
					</view>
				</view>
				
				<!-- 错误提示 -->
				<view class="error-message" v-if="errorMsg">
					<text class="error-text">{{ errorMsg }}</text>
				</view>
				
				<!-- 提交按钮 -->
				<view class="button-group">
					<view 
						class="submit-button" 
						:class="{ 'button-loading': isLoading, 'button-disabled': !canSubmit }"
						@click="handleSubmit"
					>
						<text class="button-text" v-if="!isLoading">保存档案</text>
						<view class="loading-spinner" v-else></view>
					</view>
				</view>
				
				<!-- 跳过提示 -->
				<view class="skip-section" v-if="isNewProfile">
					<text class="skip-link" @click="skipForNow">稍后完善</text>
				</view>
				
				<view class="card-shine"></view>
			</view>
		</view>
		
		<!-- 底部导航栏 -->
		<bottom-nav-doctor v-if="userType === 'doctor'" current="profile"></bottom-nav-doctor>
		<bottom-nav-patient v-else current="profile"></bottom-nav-patient>
	</view>
</template>

<script>
import BottomNavDoctor from '@/components/bottom_nav/BottomNavDoctor.vue'
import BottomNavPatient from '@/components/bottom_nav/BottomNavPatient.vue'
import { patientAPI, doctorAPI, authAPI } from '@/utils/request.js'

export default {
	components: {
		BottomNavDoctor,
		BottomNavPatient
	},
	data() {
		return {
			userType: 'patient', // 用户类型
			isNewProfile: false, // 是否是新创建的档案
			
			// 医生表单数据
			doctorForm: {
				name: '',
				license_number: '',
				specialty: '',
				hospital: '',
				department: '',
				title: '',
				phone: '',
				email: '',
				bio: ''
			},
			
			// 患者表单数据
			patientForm: {
				name: '',
				gender: '',
				id_card: '',
				birth_date: '',
				phone: '',
				address: '',
				emergency_contact: '',
				emergency_phone: '',
				medical_history: '',
				allergies: ''
			},
			
			// 选择器选项
			specialtyOptions: [
				{ value: 'neurology', label: '神经科' },
				{ value: 'radiology', label: '放射科' },
				{ value: 'oncology', label: '肿瘤科' },
				{ value: 'neurosurgery', label: '神经外科' },
				{ value: 'general', label: '全科' }
			],
			
			genderOptions: [
				{ value: 'M', label: '男' },
				{ value: 'F', label: '女' }
			],
			
			isLoading: false,
			errorMsg: ''
		}
	},
	computed: {
		userTypeText() {
			return this.userType === 'doctor' ? '医生端' : '患者端'
		},
		canSubmit() {
			if (this.userType === 'doctor') {
				return this.doctorForm.license_number && 
				       this.doctorForm.specialty && 
				       this.doctorForm.hospital && 
				       this.doctorForm.department &&
				       !this.isLoading
			} else {
				return this.patientForm.gender && 
				       this.patientForm.id_card && 
				       this.patientForm.birth_date &&
				       !this.isLoading
			}
		}
	},
	async onLoad(options) {
		// 从路由参数或缓存获取用户类型
		if (options && options.userType) {
			this.userType = options.userType
		} else {
			const user = uni.getStorageSync('user')
			if (user && user.user_type) {
				this.userType = user.user_type
			}
		}
		
		// 检查是否是新用户（需要完善档案）
		if (options && options.isNew === 'true') {
			this.isNewProfile = true
		}
		
		// 加载现有档案数据（如果有）
		await this.loadExistingProfile()
	},
	methods: {
		goBack() { uni.navigateBack({ delta: 1, fail: () => { uni.reLaunch({ url: '/pages/selectIdentity/selectIdentity' }) } }) },
		// 加载现有档案数据
		async loadExistingProfile() {
			try {
				if (this.userType === 'doctor') {
					const response = await doctorAPI.getMyProfile()
					if (response) {
						this.doctorForm = {
							name: response.name || '',
							license_number: response.license_number || '',
							specialty: response.specialty || '',
							hospital: response.hospital || '',
							department: response.department || '',
							title: response.title || '',
							phone: response.phone || response.user?.phone || '',
							email: response.email || response.user?.email || '',
							bio: response.bio || ''
						}
					}
				} else {
					const response = await patientAPI.getMyProfile()
					if (response) {
						// 格式化日期为 YYYY-MM-DD
						let birthDate = ''
						if (response.birth_date) {
							const date = new Date(response.birth_date)
							birthDate = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
						}
						
						this.patientForm = {
							name: response.name || '',
							gender: response.gender || '',
							id_card: response.id_card || '',
							birth_date: birthDate,
							phone: response.phone || '',
							address: response.address || '',
							emergency_contact: response.emergency_contact || '',
							emergency_phone: response.emergency_phone || '',
							medical_history: response.medical_history || '',
							allergies: response.allergies || ''
						}
					}
				}
			} catch (error) {
				console.log('加载现有档案失败（可能是新用户）:', error)
				// 尝试获取基础用户信息
				try {
					const userResponse = await authAPI.getProfile()
					if (userResponse) {
						if (this.userType === 'doctor') {
							this.doctorForm.name = userResponse.name || ''
							this.doctorForm.phone = userResponse.phone || ''
							this.doctorForm.email = userResponse.email || ''
						} else {
							this.patientForm.name = userResponse.name || ''
							this.patientForm.phone = userResponse.phone || ''
						}
					}
				} catch (userError) {
					console.error('获取用户信息失败:', userError)
				}
			}
		},
		
		// 专科选择
		onSpecialtyChange(e) {
			const index = parseInt(e.detail.value)
			this.doctorForm.specialty = this.specialtyOptions[index].value
		},
		
		getSpecialtyLabel(value) {
			const option = this.specialtyOptions.find(opt => opt.value === value)
			return option ? option.label : value
		},
		
		// 性别选择
		onGenderChange(e) {
			const index = parseInt(e.detail.value)
			this.patientForm.gender = this.genderOptions[index].value
		},
		
		getGenderLabel(value) {
			const option = this.genderOptions.find(opt => opt.value === value)
			return option ? option.label : value
		},
		
		// 出生日期选择
		onBirthDateChange(e) {
			this.patientForm.birth_date = e.detail.value
		},
		
		// 验证表单
		validateForm() {
			this.errorMsg = ''
			
			if (this.userType === 'doctor') {
				if (!this.doctorForm.license_number.trim()) {
					this.errorMsg = '请输入执业证号'
					return false
				}
				if (!this.doctorForm.specialty) {
					this.errorMsg = '请选择专科'
					return false
				}
				if (!this.doctorForm.hospital.trim()) {
					this.errorMsg = '请输入医院名称'
					return false
				}
				if (!this.doctorForm.department.trim()) {
					this.errorMsg = '请输入科室名称'
					return false
				}
			} else {
				if (!this.patientForm.gender) {
					this.errorMsg = '请选择性别'
					return false
				}
				if (!this.patientForm.id_card.trim()) {
					this.errorMsg = '请输入身份证号'
					return false
				}
				if (this.patientForm.id_card.length !== 18) {
					this.errorMsg = '身份证号应为18位'
					return false
				}
				if (!this.patientForm.birth_date) {
					this.errorMsg = '请选择出生日期'
					return false
				}
			}
			
			return true
		},
		
		// 提交表单
		async handleSubmit() {
			if (!this.validateForm()) {
				return
			}
			
			if (!this.canSubmit || this.isLoading) {
				return
			}
			
			this.isLoading = true
			this.errorMsg = ''
			
			try {
				uni.showLoading({
					title: '保存中...',
					mask: true
				})
				
				if (this.userType === 'doctor') {
					// 更新或创建医生档案
					try {
						// 先尝试获取现有档案
						const profile = await doctorAPI.getMyProfile()
						if (profile && profile.id) {
							// 有档案，使用PUT更新
							await doctorAPI.updateProfile(profile.id, {
								name: this.doctorForm.name,
								license_number: this.doctorForm.license_number,
								specialty: this.doctorForm.specialty,
								hospital: this.doctorForm.hospital,
								department: this.doctorForm.department,
								title: this.doctorForm.title,
								phone: this.doctorForm.phone,
								email: this.doctorForm.email,
								bio: this.doctorForm.bio
							})
						}
					} catch (error) {
						// 如果没有档案（404错误），创建新档案
						if (error.message && (error.message.includes('未找到') || error.message.includes('404'))) {
							await doctorAPI.createProfile({
								name: this.doctorForm.name,
								license_number: this.doctorForm.license_number,
								specialty: this.doctorForm.specialty,
								hospital: this.doctorForm.hospital,
								department: this.doctorForm.department,
								title: this.doctorForm.title,
								phone: this.doctorForm.phone,
								email: this.doctorForm.email,
								bio: this.doctorForm.bio
							})
						} else {
							throw error
						}
					}
				} else {
					// 更新或创建患者档案
					try {
						// 先尝试获取现有档案
						const profile = await patientAPI.getMyProfile()
						if (profile && profile.id) {
							// 有档案，使用PUT更新
							await patientAPI.updateProfile(profile.id, {
								name: this.patientForm.name,
								gender: this.patientForm.gender,
								id_card: this.patientForm.id_card,
								birth_date: this.patientForm.birth_date,
								phone: this.patientForm.phone,
								address: this.patientForm.address,
								emergency_contact: this.patientForm.emergency_contact,
								emergency_phone: this.patientForm.emergency_phone,
								medical_history: this.patientForm.medical_history,
								allergies: this.patientForm.allergies
							})
						} else {
							// 没有id，尝试创建新档案
							await patientAPI.createProfile({
								name: this.patientForm.name,
								gender: this.patientForm.gender,
								id_card: this.patientForm.id_card,
								birth_date: this.patientForm.birth_date,
								phone: this.patientForm.phone,
								address: this.patientForm.address,
								emergency_contact: this.patientForm.emergency_contact,
								emergency_phone: this.patientForm.emergency_phone,
								medical_history: this.patientForm.medical_history,
								allergies: this.patientForm.allergies
							})
						}
					} catch (error) {
						console.error('保存患者档案错误:', error)
						// 如果没有档案（404错误），创建新档案
						if (error.message && (error.message.includes('未找到') || error.message.includes('404') || error.message.includes('Not Found'))) {
							try {
								await patientAPI.createProfile({
									name: this.patientForm.name,
									gender: this.patientForm.gender,
									id_card: this.patientForm.id_card,
									birth_date: this.patientForm.birth_date,
									phone: this.patientForm.phone,
									address: this.patientForm.address,
									emergency_contact: this.patientForm.emergency_contact,
									emergency_phone: this.patientForm.emergency_phone,
									medical_history: this.patientForm.medical_history,
									allergies: this.patientForm.allergies
								})
							} catch (createError) {
								console.error('创建患者档案失败:', createError)
								throw createError
							}
						} else {
							// 其他错误直接抛出
							throw error
						}
					}
				}
				
				uni.hideLoading()
				
				uni.showToast({
					title: '档案保存成功',
					icon: 'success',
					duration: 2000
				})
				
				// 延迟跳转
				setTimeout(() => {
					if (this.isNewProfile) {
						// 新用户完善档案后，跳转到主页
						if (this.userType === 'doctor') {
							uni.reLaunch({
								url: '/pages/managePatients/managePatients'
							})
						} else {
							uni.reLaunch({
								url: '/pages/medicalRecord/medicalRecord'
							})
						}
					} else {
						// 编辑档案后，返回上一页
						uni.navigateBack({
							delta: 1
						})
					}
				}, 1500)
				
			} catch (error) {
				uni.hideLoading()
				this.isLoading = false
				console.error('保存档案失败:', error)
				
				let errorMsg = '保存失败'
				if (error.message) {
					errorMsg = error.message
				} else if (typeof error === 'string') {
					errorMsg = error
				} else if (error.license_number || error.id_card) {
					errorMsg = error.license_number?.[0] || error.id_card?.[0] || '保存失败'
				}
				
				this.errorMsg = errorMsg
				
				uni.showToast({
					title: errorMsg,
					icon: 'none',
					duration: 3000
				})
			}
		},
		
		// 稍后完善
		skipForNow() {
			uni.showModal({
				title: '提示',
				content: '完善档案后可以获得更好的服务体验，确定要跳过吗？',
				success: (res) => {
					if (res.confirm) {
						if (this.userType === 'doctor') {
							uni.reLaunch({
								url: '/pages/managePatients/managePatients'
							})
						} else {
							uni.reLaunch({
								url: '/pages/medicalRecord/medicalRecord'
							})
						}
					}
				}
			})
		}
	}
}
</script>

<style scoped>
.page-container {
	min-height: 100vh;
	background: var(--ds-surface);
	position: relative;
	overflow-x: hidden;
	overflow-y: auto;
	display: flex;
	flex-direction: column;
	padding: 40px 20px 100px;
}

/* 背景装饰圆圈 */
.bg-decoration {
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	overflow: hidden;
	z-index: 0;
}

.circle {
	position: absolute;
	border-radius: 50%;
	background: rgba(10, 92, 255, 0.04);
	animation: float 6s ease-in-out infinite;
}

.circle-1 {
	width: 300px;
	height: 300px;
	top: -150px;
	right: -100px;
	animation-delay: 0s;
}

.circle-2 {
	width: 200px;
	height: 200px;
	bottom: -100px;
	left: -50px;
	animation-delay: 2s;
}

.circle-3 {
	width: 150px;
	height: 150px;
	top: 50%;
	left: -75px;
	animation-delay: 4s;
}

@keyframes float {
	0%, 100% {
		transform: translateY(0px) scale(1);
	}
	50% {
		transform: translateY(-20px) scale(1.05);
	}
}

/* 头部区域 */
.header-section {
	position: relative;
	z-index: 1;
	text-align: center;
	margin-bottom: 30px;
	animation: fadeInDown 0.8s ease-out;
}

.back-btn {
	position: absolute;
	top: 0;
	left: 0;
	display: flex;
	align-items: center;
	gap: 2px;
	padding: 6px 12px;
	border-radius: 20px;
	z-index: 2;
}
.back-pressed { background: rgba(10, 92, 255, 0.08); }
.back-char { font-size: 28px; font-weight: 300; color: var(--ds-brand); line-height: 1; margin-top: -2px; }
.back-text { font-size: 15px; font-weight: 600; color: var(--ds-brand); }

.logo-container {
	display: flex;
	flex-direction: column;
	align-items: center;
}

.logo-icon {
	width: 80px;
	height: 80px;
	background: var(--ds-brand-soft);
	border-radius: 24px;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 15px;
	
	border: 1px solid var(--ds-hairline);
}

.icon {
	font-size: 40px;
}

.app-title {
	font-size: 28px;
	font-weight: bold;
	color: var(--ds-ink-1);
	margin-bottom: 8px;
}

.app-subtitle {
	font-size: 14px;
	color: var(--ds-ink-3);
	letter-spacing: 1px;
}

/* 表单容器 */
.form-container {
	position: relative;
	z-index: 1;
	animation: fadeInUp 0.8s ease-out 0.2s both;
}

.form-card {
	position: relative;
	background: var(--ds-surface);
	border-radius: 20px;
	padding: 25px 20px;
	box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
	border: 1px solid var(--ds-hairline);
	overflow: hidden;
}

.card-gradient {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	height: 4px;
	background: var(--ds-grad-brand);
	border-radius: 20px 20px 0 0;
}

.form-content {
	position: relative;
	z-index: 1;
}

/* 字段标签 */
.field-label {
	font-size: 15px;
	font-weight: 600;
	color: var(--ds-ink-1);
	display: block;
	margin-bottom: 4px;
	margin-left: 4px;
}
.label-required {
	color: #FF4D5E;
	font-weight: 700;
}
.field-hint {
	font-size: 12px;
	color: var(--ds-ink-3);
	display: block;
	margin-bottom: 8px;
	margin-left: 4px;
}

/* 输入框组 */
.input-group {
	margin-bottom: 18px;
}

.input-wrapper {
	position: relative;
	background: var(--ds-surface);
	border-radius: 12px;
	border: 1px solid var(--ds-hairline);
	display: flex;
	align-items: center;
	padding: 0 15px;
	transition: all 0.3s ease;
	min-height: 50px;
}

.input-wrapper.textarea-wrapper {
	align-items: flex-start;
	padding: 15px;
	min-height: 100px;
}

.input-wrapper:focus-within {
	border-color: var(--ds-ink-1);
	box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1);
}

.input-icon {
	font-size: 18px;
	margin-right: 10px;
	color: var(--ds-ink-4);
	flex-shrink: 0;
}

.input-field {
	flex: 1;
	height: 50px;
	font-size: 15px;
	color: var(--ds-ink-1);
	background: transparent;
	border: none;
	outline: none;
}

.textarea-field {
	flex: 1;
	min-height: 80px;
	font-size: 15px;
	color: var(--ds-ink-1);
	background: transparent;
	border: none;
	outline: none;
	resize: none;
}

.input-field::placeholder,
.textarea-field::placeholder {
	color: var(--ds-ink-4);
}

.input-hint {
	font-size: 12px;
	color: var(--ds-warning);
	margin-top: 5px;
	margin-left: 15px;
}

/* 选择器样式 */
.picker-view {
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: space-between;
	height: 50px;
}

.picker-text {
	font-size: 15px;
	color: var(--ds-ink-1);
}

.picker-placeholder {
	font-size: 15px;
	color: var(--ds-ink-4);
}

.picker-arrow {
	font-size: 12px;
	color: var(--ds-ink-4);
	margin-left: 10px;
}

/* 错误提示 */
.error-message {
	margin-bottom: 15px;
	padding: 10px 15px;
	background: rgba(255, 107, 107, 0.1);
	border-radius: 8px;
	border-left: 3px solid #FF4D5E;
}

.error-text {
	font-size: 13px;
	color: #FF4D5E;
}

/* 按钮组 */
.button-group {
	margin-top: 25px;
}

.submit-button {
	width: 100%;
	height: 50px;
	background: var(--ds-grad-brand);
	border-radius: 25px;
	display: flex;
	align-items: center;
	justify-content: center;
	
	transition: all 0.3s ease;
	cursor: pointer;
}

.submit-button:active {
	transform: scale(0.98);
}

.submit-button.button-loading {
	opacity: 0.8;
	cursor: not-allowed;
}

.submit-button.button-disabled {
	background: #d0d0d0;
	box-shadow: none;
	cursor: not-allowed;
}

.button-text {
	color: #ffffff;
	font-size: 18px;
	font-weight: bold;
}

.loading-spinner {
	width: 24px;
	height: 24px;
	border: 3px solid rgba(255, 255, 255, 0.3);
	border-top: 3px solid #ffffff;
	border-radius: 50%;
	animation: spin 1s linear infinite;
}

@keyframes spin {
	0% { transform: rotate(0deg); }
	100% { transform: rotate(360deg); }
}

/* 跳过区域 */
.skip-section {
	text-align: center;
	margin-top: 20px;
}

.skip-link {
	font-size: 14px;
	color: var(--ds-ink-3);
	text-decoration: underline;
}

.skip-link:active {
	opacity: 0.7;
}

/* 卡片闪光效果 */
.card-shine {
	position: absolute;
	top: -50%;
	left: -50%;
	width: 200%;
	height: 200%;
	background: linear-gradient(45deg, 
		transparent 40%, 
		rgba(255, 255, 255, 0.3) 50%, 
		transparent 60%);
	transform: translateX(-100%);
	transition: transform 0.6s ease;
}

.form-card:active .card-shine {
	transform: translateX(100%);
}

/* 动画 */
@keyframes fadeInDown {
	from {
		opacity: 0;
		transform: translateY(-30px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}

@keyframes fadeInUp {
	from {
		opacity: 0;
		transform: translateY(30px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}
</style>

